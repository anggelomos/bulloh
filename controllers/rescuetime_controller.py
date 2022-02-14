import requests
from data.constants.time_metrics import TimeMetrics
from typing import Dict, List
import os

from utilities.utilities import Utilities


class RescuetimeController:

    API_key = os.getenv("RT_API_KEY")

    def _get_hours_endpoint(self, date: str) -> str:
        return f"https://www.rescuetime.com/anapi/data?key={self.API_key}&perspective=interval&restrict_kind=productivity&interval=hour&restrict_begin={date}&restrict_end={date}&format=json"

    @staticmethod
    def _process_time(time_records: List[str], productive_time: bool) -> float:
        if productive_time:
            def filter_function(x): return x[-1] > 0
        else:
            def filter_function(x): return x[-1] < 0

        return sum(map(lambda x: x[1], filter(filter_function, time_records))) / 3600

    def get_recorded_time(self, date: str) -> Dict[TimeMetrics, float]:
        hours_request = requests.get(self._get_hours_endpoint(date)).json()["rows"]

        productive_time = self._process_time(hours_request, productive_time=True)
        leisure_time = self._process_time(hours_request, productive_time=False)

        return {
                TimeMetrics.WORK_TIME: Utilities.round_number(productive_time),
                TimeMetrics.LEISURE_TIME: Utilities.round_number(leisure_time),
                }
