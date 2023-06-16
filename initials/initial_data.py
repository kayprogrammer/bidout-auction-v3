import asyncio
import os
import sys

sys.path.append(os.path.abspath("./"))  # To single-handedly execute this script

import logging

from initials.data_script import CreateData
from app.core.database import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    db = AsyncSessionLocal()
    create_data = CreateData(db)
    await create_data.initialize()
    await db.close()


async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
