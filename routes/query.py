from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from func import (
    queryDict,
    getThumbail,
    getDicts,
    getHints,
    fixResource,
    fetchStatic,
    addBack,
    strSim,
    getVersion,
)
from typing import List, Optional, Tuple

router = APIRouter()


class ADict(BaseModel):
    order: int = Field(description="The id for the dictionary.")
    name: str = Field(description="The name of the dict.")


class Dicts(BaseModel):
    lst: List[ADict] = Field(description="The dictionaries that MyDICT owns.")
    version: str = Field(description="Current file version.")


class AvailableDicts(BaseModel):
    lst: List[int] = Field(description="The dictionaries that owns the word you query.")


class Hint(BaseModel):
    lst: List[Tuple[str, List[int]]] = Field(description="Hint for the search.")


class SearchResult(BaseModel):
    result: List[str] = Field(description="The content.")


@router.get("/thumbail", tags=["query"])
def thumbail(d: int):
    return FileResponse(path=getThumbail(d))


@router.get("/query", response_model=SearchResult, tags=["query"])
def query(s: str, d: int, back: Optional[str] = None):
    result = queryDict(s, d)
    exp = [fixResource(d, i) for i in result]
    if exp and back:
        exp[0] = addBack(exp[0], back)
    return SearchResult(result=exp)


@router.get("/dicts", response_model=Dicts, tags=["query"])
def dicts():
    lst = [ADict(name=i.name, order=i.order) for i in getDicts()]
    return Dicts(lst=lst, version=getVersion())


@router.get("/hint", response_model=Hint, tags=["query"])
def hint(s: str, start: Optional[int] = 0, limit: Optional[int] = 10):
    lst = list(getHints(s).items())
    lst.sort(key=lambda x: strSim(x[0], s), reverse=True)
    return Hint(
        lst=lst[
            start
            if 0 <= start < len(lst)
            else 0 : limit
            if 0 < limit <= len(lst)
            else len(lst)
        ]
    )


@router.get("/resource", tags=["query"])
def resource(d: int, r: str):
    return fetchStatic(d, r)
