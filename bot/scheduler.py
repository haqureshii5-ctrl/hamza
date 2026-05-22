import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import settings
from .logger import logger
from . import bot


def schedule_daily() -> None:
    scheduler = AsyncIOScheduler(timezone="UTC")
    trigger = CronTrigger(hour=settings.daily_post_hour, minute=settings.daily_post_minute)
    scheduler.add_job(bot.run_cycle, trigger, name="crypto-trend-daily-cycle", max_instances=1)
    scheduler.start()
    logger.info("Scheduled daily bot cycle at %02d:%02d UTC", settings.daily_post_hour, settings.daily_post_minute)

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
        scheduler.shutdown()
        bot.close()
