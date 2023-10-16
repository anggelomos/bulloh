import logging
from typing import List

from tickthon import Task


class Bulloh:

    @staticmethod
    def process_weight(date: str, weight_logs: List[Task]) -> float:
        """Processes weight data from Ticktick and returns the weight for the given date"""
        logging.info(f"Processing weight data for date: {date}")

        raw_weight = next(filter(lambda log: date in log.created_date, weight_logs), None)
        if raw_weight:
            return float(raw_weight.title.split()[-1])
        return 0.0
