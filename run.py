from src.bot import main
import asyncio
import logging
import cloudscraper


async def run():
    await asyncio.gather(main(scraper))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    scraper = cloudscraper.create_scraper()
    asyncio.run(run())
