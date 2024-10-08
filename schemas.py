from pydantic import BaseModel, ConfigDict
from typing import Optional


class SpiritAdd(BaseModel):
    type: str
    name: str
    difficulty: Optional[str] = None
    source: str
    picture: str


class SpiritPatch(SpiritAdd):
    pass


class SpiritId(BaseModel):
    ids: list[int]


class Spirit(SpiritAdd):
    id: int
