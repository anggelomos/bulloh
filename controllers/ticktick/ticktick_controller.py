from typing import Dict

from controllers.ticktick.ticktick_api import TicktickAPI
from data.constants.ticktick_ids import TicktickIds
from data.constants.time_metrics import TimeMetrics
from data.payloads.ticktick_payloads import TicktickPayloads
from utilities.general_utilities import GeneralUtilities as GU


class TicktickController:
    
    active_tasks = {}
    notion_ids = {}
    BASE_URL = "/api/v2"
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
