from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from func import (
    queryDict,
    queryDicts,
    getThumbail,
    getDicts,
    getHints,
    fixResource,
    fetchStatic,
    transCap,
)
from typing import List, Optional

router = APIRouter()


class ADict(BaseModel):
    order: int = Field(description="The id for the dictionary.")
    name: str = Field(description="The name of the dict.")


class Dicts(BaseModel):
    lst: List[ADict] = Field(description="The dictionaries that MyDICT owns.")


class AvailableDicts(BaseModel):
    lst: List[int] = Field(description="The dictionaries that owns the word you query.")


class Hint(BaseModel):
    lst: List[str] = Field(description="Hint for the search.")


class SearchResult(BaseModel):
    result: List[str] = Field(description="The content.")


@router.get("/available", response_model=AvailableDicts, tags=["query"])
def available(s: str):
    lst = [i.order for i in queryDicts(s)]
    return AvailableDicts(lst=lst)


@router.get("/thumbail", tags=["query"])
def thumbail(d: int):
    return FileResponse(path=getThumbail(d))


@router.get("/query", response_model=SearchResult, tags=["query"])
def query(s: str, d: int):
    result = queryDict(s, d)
    exp = [fixResource(d, i) for i in result]
    return SearchResult(result=exp)


@router.get("/dicts", response_model=Dicts, tags=["query"])
def dicts():
    lst = [ADict(name=i.name, order=i.order) for i in getDicts()]
    return Dicts(lst=lst)


@router.get("/hint", response_model=Hint, tags=["query"])
def hint(s: str, start: Optional[int] = 0, limit: Optional[int] = 10):
    lst = getHints(s)
    lst.sort(key=lambda x: (len(x), transCap(x)))
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
