from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session, init_db
from app.utils import get_blocks_until_is_not_unique, get_blocks_from_db


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.post("/api/quize_blocks")
async def post_quize_blocks_in_db(num: int, 
                                  session: AsyncSession = Depends(get_session)):
    return await get_blocks_until_is_not_unique(num, session)


@app.get("/api/quize_blocks")
async def post_quize_blocks_in_db(num: int, 
                                  session: AsyncSession = Depends(get_session)):
    return await get_blocks_from_db(num, session)