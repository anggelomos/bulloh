from enum import Enum
from typing import List


class Habits(Enum):

    READ = "read"
    READ_TIME = "read_time"
    MEDITATE = "meditate"
    MEDITATE_TIME = "meditate_time"
    PLAN_DAY = "plan_day"
    PLAN_DAY_TIME = "plan_day_time"
    JOURNALING = "journaling"
    JOURNALING_TIME = "journaling_time"
    LEARN_LANGUAGE = "learn_language"
    LEARN_LANGUAGE_TIME = "learn_language_time"
    EXERCISE = "exercise"
    EXERCISE_TIME = "exercise_time"
    STUDY = "study"
    STUDY_TIME = "study_time"


def get_habit_headers() -> List[str]:
    return [identifier.value for identifier in Habits]
