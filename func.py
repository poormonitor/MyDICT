import mimetypes
import os
import re
from functools import cache, lru_cache
from typing import Dict, List, Optional
import chardet

from bs4 import BeautifulSoup
from fastapi import HTTPException
from fastapi.responses import FileResponse, Response, RedirectResponse

from mdict.mdict_query import IndexBuilder


class Dictionary:
    name: str
    path: str
    thumbail: str
    dirname: str
    order: Optional[int]
    resources: List[str]

    def __repr__(self):
        return "<Dict %d %s>" % (self.order, self.name)

    def __init__(
        self,
        name: str,
        path: str,
        dirname: str,
        thumbail: str = None,
        resources: Dict[str, str] = {},
    ):
        self.name = name
        self.path = path
        self.dirname = dirname
        self.resources = resources

        if not thumbail:
            self.thumbail = os.path.join(os.path.dirname(__file__), "default.jpg")
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
    for i in os.listdir(dicts_path):
        if os.path.isdir(dict_path := os.path.join(dicts_path, i)):
            resources = getAllResources(dict_path)
            for j in resources.keys():
                name, ext = os.path.splitext(j)
                file_path = resources[j]
                if ext == ".mdx":
                    if image := hasThumbail(file_path, name):
                        dict = Dictionary(
                            path=file_path,
                            name=name,
                            dirname=os.path.basename(dict_path),
                            thumbail=image,
                            resources=resources,
                        )
                    else:
                        dict = Dictionary(
                            path=file_path,
                            dirname=os.path.basename(dict_path),
                            name=name,
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


@lru_cache(65535)
def queryDict(s: str, d: int) -> List[str]:
    path = getDict(d).path
    builder = IndexBuilder(path)
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
    path = getDict(d).path
    builder = IndexBuilder(path)
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
    path = getDict(d).path
    builder = IndexBuilder(path)
    try:
        rs = builder.mdd_lookup(os.path.normpath("/" + f))[0]
    except:
        rs = None
    return rs


def fixCSS(d: int, css: str) -> str:
    content = re.sub(
        r"url\(\"(.*)\"\)",
        lambda x: 'url("/api/resource?d=%d&r=%s")' % (d, x.group(1))
        if not x.group(1).startswith("data:")
        else 'url("%s")' % x.group(1),
        css,
    )
    return content


@cache
def fetchStatic(d: int, f: str) -> Response:
    headers = {"Cache-Control": "public, max-age=2592000"}
    resource = getResource(d, f)
    if resource:
        mime = mimetypes.guess_type(f)[0]
        encoding = chardet.detect(resource)["encoding"]
        if not mime:
            mime = "text/plain"

        if f.endswith(".css"):
            resource = fixCSS(d, resource.decode(encoding=encoding))
            mime = "text/css"

        return Response(content=resource, media_type=mime, headers=headers)

    dictionary = getDict(d)
    if f in dictionary.resources:
        if f.endswith(".css"):
            with open(dictionary.resources[f], "r", encoding="UTF-8") as fp:
                content = fixCSS(d, fp.read())
            return Response(content=content, media_type="text/css", headers=headers)

        return FileResponse(path=dictionary.resources[f], headers=headers)

    raise HTTPException(status_code=404, detail="Resource not found.")


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
        
    soup.body["class"] = "main-content"

    if not soup.head:
        soup.html.insert_before(soup.new_tag("head"))

    soup.head.append(
        soup.new_tag(
            "link", rel="stylesheet", type="text/css", href="universal.css"
        )
    )

    return str(soup)
