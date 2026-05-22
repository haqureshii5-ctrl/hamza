import asyncio
import argparse

from bot.logger import logger
from bot import bot as crypto_bot
from bot.scheduler import schedule_daily


async def run_once() -> None:
    try:
        await crypto_bot.run_cycle()
    finally:
        crypto_bot.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Binance crypto trend posting bot.")
    parser.add_argument("--once", action="store_true", help="Run a single posting cycle and exit.")
    args = parser.parse_args()

    if args.once:
        asyncio.run(run_once())
        return

    schedule_daily()


if __name__ == "__main__":
    main()
