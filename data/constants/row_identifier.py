from enum import Enum
from typing import List


class RowIdentifier(Enum):

    YEAR_DAY = "year_day"
    DATE = "date"
    DAY = "day"
    DAY_NAME = "day_name"
    WEEK = "week"
    MONTH = "month"
    COMPLETED = "completed"


def get_row_identifiers() -> List[str]:
    return [identifier.value for identifier in RowIdentifier]
