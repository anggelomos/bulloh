from datetime import datetime
from typing import List


class HabitUtilities:

    @classmethod
    def clean_habit_checkins(cls, checkins: List[dict], date: int) -> bool:

        def is_habit_checked(checkin: dict) -> bool:
            return checkin["checkinStamp"] == date and checkin["status"] == 2

        return any(map(is_habit_checked, checkins))

    @classmethod
    def parse_habit_date(cls, date: str) -> tuple:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")

        day = parsed_date.strftime("%a").lower()
        week_number = int(parsed_date.strftime("%W"))
        year = int(parsed_date.strftime("%Y"))

        return day, week_number, year
