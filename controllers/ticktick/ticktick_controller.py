from typing import Dict
import re

from controllers.ticktick.ticktick_api import TicktickAPI
from data.constants.ticktick_ids import TicktickIds
from data.constants.time_metrics import TimeMetrics
from data.payloads.ticktick_payloads import TicktickPayloads
from utilities.general_utilities import GeneralUtilities as GU


class TicktickController:
    
    active_tasks = {}
    notion_ids = {}
    BASE_URL = "/api/v2"
    get_state = BASE_URL + "/batch/check/0"
    habit_checkins_url = BASE_URL + "/habitCheckins/query"
    general_focus_time_url = BASE_URL + "/pomodoros/statistics/heatmap"
    habits_focus_time_url = BASE_URL + "/pomodoros/statistics/dist"

    def __init__(self, username: str, password: str):
        self.ticktick_client = TicktickAPI(username, password)

    def get_habits(self, date: str) -> dict:
        day_before = GU.get_previous_date(date, amount_days=1)
        payload = TicktickPayloads.get_habits_checkins(TicktickIds.habit_list, GU.date_to_int(day_before))

        return self.ticktick_client.post(self.habit_checkins_url, payload)["checkins"]

    def get_general_focus_time(self, date: str) -> Dict[str, float]:
        processed_date = f"/{GU.date_to_int(date)}"*2
        raw_time = self.ticktick_client.get(self.general_focus_time_url+processed_date)[0]["duration"]
        return {TimeMetrics.FOCUS_TIME.value: GU.round_number(raw_time / 60)}

    def get_habits_time(self, date: str) -> Dict[str, float]:
        processed_date = f"/{GU.date_to_int(date)}"*2

        raw_habits_time = self.ticktick_client.get(self.habits_focus_time_url + processed_date)
        if raw_habits_time:
            return raw_habits_time["tagDurations"]
        return raw_habits_time

    def get_weight(self, date):
        raw_tasks = self.ticktick_client.get(self.get_state, token_required=True)["syncTaskBean"]["update"]

        def weight_tasks_filter(task):
            inbox_filter = task["projectId"] == "640c03cd8f08d5a6c4bb32e7"
            date_filter = date in task["createdTime"]
            title_filter = "weight measurement" in task["title"]
            return inbox_filter and date_filter and title_filter

        weight = 0
        weight_task = next(filter(weight_tasks_filter, raw_tasks), None)
        if weight_task:
            weight = float(re.search(r"[\d\.]+", weight_task["title"]).group(0))

        return {"weight": weight}
