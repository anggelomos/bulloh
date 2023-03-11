import datetime
import logging
import os

from controllers.bulloh_controller import BullohController
from controllers.notion.notion_controller import NotionController
from controllers.rescuetime_controller import RescuetimeController
from controllers.ticktick.ticktick_controller import TicktickController


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
    bulloh = BullohController()
    rescuetime = RescuetimeController()
    notion = NotionController(os.getenv('NT_auth'), notion_version="2022-06-28")
    ticktick = TicktickController(os.getenv('TT_user'), os.getenv('TT_pass'))
    today_date = datetime.date.today()

    for date in notion.get_incomplete_dates(today_date):

        time_data = bulloh.process_time(rescuetime, ticktick, date)
        weight_data = bulloh.process_weight(ticktick, date)
        habits_data = bulloh.process_habits(ticktick, date)
        habits_time_data = bulloh.process_habits_time(ticktick, date)

        row_data = {**time_data, **weight_data, **habits_data, **habits_time_data}
        notion.update_row(date, row_data)


if __name__ == "__main__":
    main()
