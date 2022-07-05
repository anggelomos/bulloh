from enum import Enum
from typing import List


class TimeMetrics(Enum):

    WORK_TIME = "work_time"
    FOCUS_TIME = "focus_time"
    LEISURE_TIME = "leisure_time"
    SLEEP_TIME = "sleep_time"


def get_time_headers() -> List[str]:
    return [identifier.value for identifier in TimeMetrics]
