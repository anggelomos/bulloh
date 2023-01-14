from enum import Enum
from typing import List


class TimeMetrics(Enum):

    WORK_TIME = "work time"
    FOCUS_TIME = "focus time"
    LEISURE_TIME = "leisure time"


def get_time_headers() -> List[str]:
    return [identifier.value for identifier in TimeMetrics]
