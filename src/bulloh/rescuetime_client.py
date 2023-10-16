import logging
from typing import List

import requests


class RescuetimeClient:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.BASE_URL = f"https://www.rescuetime.com/anapi/data?key={self.api_key}"

    def _get_raw_recorded_hours(self, date: str) -> List[list]:
        """Get the raw recorded hours for a given date.

        Args:
            date: The date to get the recorded hours for in the format YYYY-MM-DD.

        Returns:
            A list of the recorded hours for the given date, each element is a list with the following format:
            [Date, Time Spent (seconds), User ID, Productivity Level (from -2 to 2)]
        """
        recorded_hours_url = f"{self.BASE_URL}&perspective=interval&restrict_kind=productivity&interval=hour&"\
                             f"restrict_begin={date}&restrict_end={date}&format=json"

        return requests.get(recorded_hours_url).json()["rows"]

    def get_productive_time(self, date: str) -> float:
        """Get the productive time for a given date.

        Args:
            date: The date to get the productive time in the format YYYY-MM-DD.
        """
        logging.info(f"Getting productive time for {date}")
        raw_records = self._get_raw_recorded_hours(date)
        return round(sum([record[1] for record in raw_records if record[-1] > 0]) / 3600, 2)

    def get_leisure_time(self, date: str) -> float:
        """Get the leisure time for a given date.

        Args:
            date: The date to get the productive time in the format YYYY-MM-DD.
        """
        logging.info(f"Getting leisure time for {date}")
        raw_records = self._get_raw_recorded_hours(date)
        return round(sum([record[1] for record in raw_records if record[-1] < 0]) / 3600, 2)
