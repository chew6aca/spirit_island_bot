from random import choice

from sqlalchemy import select
from database import SpiritOrm, new_session
from schemas import Spirit, SpiritAdd


class SpiritRepository:
    @classmethod
    async def add_spirit(cls, spirit: SpiritAdd) -> int:
        async with new_session() as session:
            data = spirit.model_dump()
            new_spirit = SpiritOrm(**data)
            session.add(new_spirit)
            await session.flush()
            await session.commit()
            return new_spirit.id
