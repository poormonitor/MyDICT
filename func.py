import mimetypes
import os
import re
import tempfile
import urllib.parse
from functools import cache, lru_cache
from typing import Dict, List, Optional

import chardet
import difflib
from bs4 import BeautifulSoup
from fastapi import HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response
from pyffmpeg import FFmpeg

from mdict.mdict_query import IndexBuilder


class Dictionary:
    name: str
    path: str
    version: str
    description: str
    thumbail: str
    dirname: str
    order: Optional[int]
    builder: IndexBuilder
    resources: List[str]

    def __repr__(self):
        return "<Dict %d %s>" % (self.order, self.name)

    def __init__(
        self,
        path: str,
        builder: IndexBuilder,
        dirname: str,
        thumbail: str = None,
        basename: str = "",
        resources: Dict[str, str] = {},
    ):
        self.path = path
        self.builder = builder
        self.name = urllib.parse.unquote(builder._title)
        self.version = builder._version
        self.description = builder._description
        self.dirname = dirname
        self.resources = resources

        if self.name.startswith("Title"):
            self.name = basename

        if not thumbail:
            self.thumbail = os.path.join(os.path.dirname(__file__), "default.png")
        else:
            self.thumbail = thumbail


def hasThumbail(file_path: str, name: str):
    EXTS = [".jpg", ".png", ".ico"]
    for i in EXTS:
        if os.path.exists(
            (image := os.path.join(os.path.dirname(file_path), name + i))
        ):
            return image
    return None


def getAllResources(path: str) -> Dict[str, str]:
    resources = {}

    for file in os.listdir(path):
        cur_path = os.path.join(path, file)
        if os.path.isdir(cur_path):
            resources.update(getAllResources(cur_path))
        else:
            bsname = os.path.basename(cur_path)
            resources[bsname] = os.path.normpath(cur_path)

    return resources


@cache
def getAllDictionaries() -> Dict[str, Dictionary]:
    dicts_path = os.path.join(os.path.dirname(__file__), "dicts/")
    found_dict = {}
    list_dir = os.listdir(dicts_path)
    list_dir.sort()
    for i in list_dir:
        if os.path.isdir(dict_path := os.path.join(dicts_path, i)):
            resources = getAllResources(dict_path)
            for j in resources.keys():
                name, ext = os.path.splitext(j)
                file_path = resources[j]
                if ext == ".mdx":
                    builder = IndexBuilder(file_path)
                    if image := hasThumbail(file_path, name):
                        dict = Dictionary(
                            path=file_path,
                            builder=builder,
                            basename=name,
                            dirname=os.path.basename(dict_path),
                            thumbail=image,
                            resources=resources,
                        )
                    else:
                        dict = Dictionary(
                            path=file_path,
                            builder=builder,
                            basename=name,
                            dirname=os.path.basename(dict_path),
                            resources=resources,
                        )
                    found_dict[dict.name] = dict
                    break

    return found_dict


@cache
def getDicts() -> List[Dictionary]:
    dicts = getAllDictionaries()
    d_values = list(dicts.values())
    d_values.sort(key=lambda x: x.dirname)
    for i, e in enumerate(d_values):
        e.order = i
    return d_values


@cache
def getDict(d: int) -> Dictionary:
    dicts = getDicts()
    if d not in range(len(dicts)):
        raise HTTPException(status_code=404, detail="Dictionary not found.")
    return dicts[d]


@cache
def getThumbail(d: int) -> str:
    dicts = getDicts()
    return dicts[d].thumbail


def fixRedirect(d: int, contents: List[str]) -> List[str]:
    result = []
    for content in contents:
        if content.startswith("@@@LINK"):
            new_word = content.replace("@@@LINK=", "").strip()
            new_rs = queryDict(new_word, d)
            result += new_rs
        else:
            result.append(content)
    return result


@lru_cache(65535)
def queryDict(s: str, d: int) -> List[str]:
    builder = getDict(d).builder
    return fixRedirect(d, builder.mdx_lookup(s))


@lru_cache(4096)
def queryDicts(s: str) -> List[Dictionary]:
    dicts = getDicts()
    rd = []
    for i in dicts:
        rs = queryDict(s, i.order)
        if rs:
            rd.append(i)
    return rd


@lru_cache(4096)
def getHint(s: str, d: int):
    builder = getDict(d).builder
    return builder.get_mdx_keys("%s*" % s)


@lru_cache(4096)
def getHints(s: str) -> List[str]:
    dicts = getDicts()
    hints = []
    for i in dicts:
        hints += getHint(s, i.order)
    return list(set(hints))


@cache
def getResource(d: int, f: str) -> str:
    builder = getDict(d).builder
    try:
        rs = builder.mdd_lookup(os.path.normpath("/" + f).replace("/", "\\"))[0]
    except:
        rs = None
    return rs


def stripMark(s: str) -> str:
    return s.replace('"', "").replace("'", "")


def fixCSS(d: int, css: str) -> str:
    content = re.sub(
        r"url\((.*)\)",
        lambda x: 'url("/api/resource?d=%d&r=%s")' % (d, stripMark(x.group(1)))
        if not stripMark(x.group(1)).startswith("data:")
        else 'url("%s")' % x.group(1),
        css,
    )
    return content


def fixSPX(a: bytes) -> bytes:
    ff = FFmpeg()

    tempin = tempfile.NamedTemporaryFile(suffix=".spx", delete=False)
    tempout = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)

    tempin.write(a)
    tempin.close()
    ff.convert(tempin.name, tempout.name)
    b = tempout.read()
    tempout.close()

    os.remove(tempin.name)
    os.remove(tempout.name)

    return b


@cache
def fetchStatic(d: int, f: str) -> Response:
    headers = {"Cache-Control": "public, max-age=2592000"}

    if f.endswith(".spx.mp3"):
        f = f.replace(".mp3", "")

    resource = getResource(d, f)
    if resource:
        mime = mimetypes.guess_type(f)[0]
        encoding = chardet.detect(resource)["encoding"]
        if not mime:
            mime = "text/plain"

        if f.endswith(".css"):
            resource = fixCSS(d, resource.decode(encoding=encoding))
            mime = "text/css"

        if f.endswith(".spx"):
            resource = fixSPX(resource)
            mime = "audio/mp3"

        return Response(content=resource, media_type=mime, headers=headers)

    dictionary = getDict(d)
    if f in dictionary.resources:
        if f.endswith(".css"):
            with open(dictionary.resources[f], "r", encoding="UTF-8") as fp:
                content = fixCSS(d, fp.read())
            return Response(content=content, media_type="text/css", headers=headers)

        return FileResponse(path=dictionary.resources[f], headers=headers)

    raise HTTPException(status_code=404, detail="Resource not found.")


def fixResource(d: int, content: str) -> str:
    soup = BeautifulSoup(content, "lxml")

    for script in soup.find_all("script"):
        script["src"] = (
            "$MYDICT_API/resource?d=%d&r=%s" % (d, script["src"])
            if script.get("src", None)
            else ""
        )

    for link in soup.find_all("link", rel="stylesheet"):
        link["href"] = (
            "$MYDICT_API/resource?d=%d&r=%s" % (d, link["href"])
            if link.get("href", None)
            else ""
        )

    for img in soup.find_all("img"):
        img["src"] = (
            "$MYDICT_API/resource?d=%d&r=%s" % (d, img["src"])
            if (src := img.get("src", None)) and not src.startswith("data:")
            else src
        )

    for a in soup.find_all("a"):
        if a.get("href", None):
            if a["href"].startswith("sound://"):
                file = a["href"].replace("sound://", "")
                if a["href"].endswith(".spx"):
                    file = file + ".mp3"
                new_url = "$MYDICT_API/resource?d=%d&r=%s" % (d, file)
                a["href"] = "javascript:new Audio('%s').play()" % (new_url)
            elif a["href"].startswith("entry://"):
                a["href"] = "javascript:window.parent.postMessage({go: '%s'})" % a[
                    "href"
                ].replace("entry://", "")
            elif a["href"].startswith("#"):
                a["href"] = (
                    "javascript:document.querySelector('%s').scrollIntoView({behavior: 'smooth'})"
                    % a["href"]
                )

    if not soup.head:
        soup.html.insert_before(soup.new_tag("head"))

    soup.head.append(
        soup.new_tag("link", rel="stylesheet", type="text/css", href="universal.css")
    )
    soup.head.append(soup.new_tag("script", src="darkreader.min.js"))

    return str(soup)


def addBack(content: str, back: str) -> str:
    soup = BeautifulSoup(content, "lxml")
    navi = soup.new_tag("div")
    navi.append(
        soup.new_tag(
            "a",
            **{
                "href": "javascript:window.parent.postMessage({go: '%s', back: true})"
                % back,
                "class": "goBack",
            },
        )
    )
    navi.a.string = "Go Back"
    soup.body.insert_before(navi)
    return str(soup)


def strSim(s1: str, s2: str) -> float:
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()
