import logging
from typing import AsyncIterator  # noqa: UP035

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import settings

log = logging.getLogger(__name__)

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.unicode_string(),
    # pool_pre_ping=True,
    # echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    # autoflush=False,
    # future=True,
)


async def get_session() -> AsyncIterator[async_sessionmaker]:
    try:
        yield AsyncSessionLocal
    except SQLAlchemyError as e:
        log.exception(e)
