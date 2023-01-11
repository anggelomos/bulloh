import datetime
import logging
import os
from controllers.notion_controller import NotionController
from controllers.rescuetime_controller import RescuetimeController
from data.constants.habits import get_habit_headers, get_habit_titles
from controllers.general_utilities import GeneralUtilities as gu
from data.constants.time_metrics import get_time_headers, TimeMetrics
from data.tasks.task_data import TaskData


def process_time(notion, postgres, rescuetime, day_number, date):
    work_time, leisure_time = rescuetime.get_recorded_time(date).values()
    focus_time = notion.get_focus_time()
    sleep_time = postgres.bulloh_database[day_number - 1][TimeMetrics.SLEEP_TIME.value]

    if not sleep_time and (datetime.date.today() - gu.parse_date(date).date()).days >= 3:
        sleep_time = 0

    if sleep_time is None:
        sleep_time = "null"

    return [work_time, focus_time, leisure_time, sleep_time]


def process_habits(notion, postgres, day_number, date):
    habits_data = []
    habits_checked = notion.get_habits_data(TaskData.DONE)
    habits_time = notion.get_habits_data(TaskData.FOCUS_TIME)

    for habit in get_habit_titles():
        habit_checked = 0
        habit_time = 0

        try:
            if habits_checked[habit]:
                habit_checked = postgres.bulloh_database[day_number - 2][habit] + 1
        except (KeyError, TypeError):
            habit_checked = 0

        try:
            if habits_time[habit]:
                habit_time = habits_time[habit]
        except KeyError:
            habit_time = 0

        if not habit_checked and (datetime.date.today() - gu.parse_date(date).date()).days < 3:
            habit_checked = "null"
            habit_time = "null"

        habits_data.append(habit_checked)
        habits_data.append(habit_time)

    return habits_data


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
    rescuetime = RescuetimeController()
    notion = NotionController(os.getenv('NT_auth'), notion_version="2021-08-16")
    today_date = datetime.date.today().strftime("%Y-%m-%d")

    for day_number, date in postgres.get_incomplete_dates(today_date):
        date = date.strftime("%Y-%m-%d")
        notion.get_entries(date)
        postgres.get_database()

        time_data = process_time(notion, postgres, rescuetime, day_number, date)
        habits_data = process_habits(notion, postgres, day_number, date)

        row_headers = get_time_headers() + get_habit_headers()
        row_data = time_data + habits_data
        postgres.update_row(day_number, list(zip(row_headers, row_data)))

    postgres.close_session()


if __name__ == "__main__":
    main()
