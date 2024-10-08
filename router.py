from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import FileResponse
from sqlalchemy import select, intersect
from typing_extensions import Annotated
from schemas import Spirit, SpiritAdd, SpiritId
from repository import SpiritRepository
from database import new_session, SpiritOrm
router = APIRouter(
    prefix='/spirits',
    tags=['spirits']
)

@router.post('')
async def add_spirit(spirits: list[SpiritAdd]) -> SpiritId:
    ids = []
    for spirit in spirits:
        new_spirit_id = await SpiritRepository.add_spirit(spirit)
        ids.append(new_spirit_id)
    return {'ids': ids}

@router.get('')
async def get_spirit(
    type: str | None = None,
    difficulty: str | None = None,
    source: str | None = None
) -> list[Spirit]:
    async with new_session() as session:
        res_query = []
        if type:
            query1 = select(SpiritOrm).filter(SpiritOrm.type.in_(type.split(',')))
            res_query.append(query1)
        if difficulty:
            query2 = select(SpiritOrm).filter(SpiritOrm.difficulty.in_(difficulty.split(',')))
            res_query.append(query2)
        if source:
            query3 = select(SpiritOrm).filter(SpiritOrm.source.in_(source.split(',')))
            res_query.append(query3)
        if not res_query:
            res = await session.execute(select(SpiritOrm))
        else:
            query = intersect(*res_query)
            res = await session.execute(query)
        return res
