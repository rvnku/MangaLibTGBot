from src.bot import main
import asyncio
import logging


async def run():
    await asyncio.gather(main())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
