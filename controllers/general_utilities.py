import datetime
from typing import Union


class GeneralUtilities:

    @staticmethod
    def round_number(number, amount_of_digits: int = 2, round_zero: bool = True) -> Union[float, int]:
        rounded_number = round(number, amount_of_digits)
        if rounded_number == 0 and round_zero:
            return 0
        return rounded_number

    @staticmethod
    def parse_date(date: str) -> datetime.datetime.date:
        if isinstance(date, str):
            return datetime.datetime.strptime(date, '%Y-%m-%d')

        return date

    @classmethod
    def get_date_in_milliseconds(cls, date: Union[str, datetime.datetime.date]) -> int:
        date = cls.parse_date(date)

        return int(date.timestamp()) * 1000

    @staticmethod
    def convert_milliseconds_to_hours(milliseconds: int) -> float:
        return milliseconds / 1000 / 60 / 60

    @classmethod
    def get_previous_date(cls, current_date: Union[str, datetime.date], amount_days: int, as_string: bool = True) -> Union[str, datetime.date]:
        current_date = cls.parse_date(current_date)
        previous_date = current_date - datetime.timedelta(days=amount_days)

        if as_string:
            return previous_date.strftime('%Y-%m-%d')
        return previous_date
