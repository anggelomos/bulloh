from enum import Enum
from typing import List


class RowIdentifier(Enum):

    COMPLETED = "completed"
    DATE = "date"
    DAY = "day #"
    WEEK = "week #"
    MONTH = "month #"
    QUARTER = "quarter #"


def get_row_identifiers() -> List[str]:
    return [identifier.value for identifier in RowIdentifier]
