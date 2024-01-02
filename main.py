from datetime import datetime
import logging
import os
from zoneinfo import ZoneInfo

from nothion import NotionClient
from nothion.personal_stats_model import PersonalStats
from tickthon import TicktickClient

from bulloh import Bulloh
from bulloh import RescuetimeClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")


def main():
    rescuetime = RescuetimeClient(os.getenv("RT_API_KEY"))
    ticktick = TicktickClient(os.getenv("TT_USER"), os.getenv("TT_PASS"))
    notion = NotionClient(os.getenv("NT_AUTH"))
    bulloh = Bulloh()

    today_date = datetime.now()
    for date in notion.get_incomplete_stats_dates(today_date):
        logging.info(f"Processing date: {date}")

        personal_stats = PersonalStats(date=date,
                                       work_time=rescuetime.get_productive_time(date),
                                       leisure_time=rescuetime.get_leisure_time(date),
                                       focus_time=ticktick.get_overall_focus_time(date),
                                       sleep_time=0,
                                       weight=bulloh.process_weight(date, ticktick.weight_measurements))

        logging.info(f"Updating stats for date: {date}, stats: {personal_stats}")
        notion.update_stats(personal_stats)


if __name__ == "__main__":
    main()
