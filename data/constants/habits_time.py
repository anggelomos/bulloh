from enum import Enum
from typing import List


class HabitsTime(Enum):

    READ_TIME = "read time"
    PLAN_TIME = "plan time"
    MEDITATE_TIME = "meditate time"
    EXERCISE_TIME = "exercise time"
    JOURNALING_TIME = "journaling time"
    LEARN_LANGUAGE_TIME = "learn language time"


def get_habit_time_headers() -> List[str]:
    return [identifier.value for identifier in HabitsTime]
