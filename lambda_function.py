import datetime
import json
import logging
import os
from controllers.google_api_controller import GoogleAPIController
from controllers.notion_controller import NotionController
from controllers.rescuetime_controller import RescuetimeController
from data.constants.habits import Habits
from controllers.general_utilities import GeneralUtilities as gu


def lambda_handler(event, conntext):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
    google_api = GoogleAPIController()
    rescuetime = RescuetimeController()
    notion = NotionController(os.getenv('NT_auth'), notion_version="2021-08-16")
    today_date = datetime.date.today().strftime("%Y-%m-%d")

    for day_number, date in google_api.get_incomplete_dates(today_date):
        work_time, leisure_time = rescuetime.get_recorded_time(date).values()
        notion.get_entries(date)
        focus_time = notion.get_focus_time()
        sleep_time = google_api.get_sleep_time(date)
        habits_checked = notion.get_habits_checked()
        habits_time = notion.get_habits_time()

        habits_data = []
        for habit in Habits:
            habit_checked = 0
            habit_time = 0

            try:
                if habits_checked[habit.value]:
                    habit_checked = google_api.bulloh_database[day_number - 2][habit.value] + 1
            except KeyError:
                habit_checked = 0

            try:
                if habits_time[habit.value]:
                    habit_time = habits_time[habit.value]
            except KeyError:
                habit_time = 0

            if not habit_checked and not habit_time and (datetime.date.today() - gu.parse_date(date).date()).days < 3:
                habit_checked = ""
                habit_time = ""

            habits_data.append(habit_checked)
            habits_data.append(habit_time)

        row_data = [work_time, focus_time, leisure_time, sleep_time] + habits_data
        google_api.update_sheets(day_number, row_data)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With',
            'Access-Control-Allow-Origin': 'https://upbeat-jackson-774e87.netlify.app',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('Tasks synced!')
    }
