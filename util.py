import json
from database import engine, SpiritOrm, create_tables
from sqlalchemy import insert
import asyncio


with open('data/spirits.json', encoding='utf-8') as file:
    spirits = json.load(file)


async def go():
    await create_tables()
    conn = await engine.connect()
    for spirit in spirits:
        query = insert(SpiritOrm).values(**spirit)
        await conn.execute(query)
    await conn.commit()
    await conn.close()


if __name__ == '__main__':
    asyncio.run(go())
