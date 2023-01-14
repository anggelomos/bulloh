from enum import Enum
from typing import List


class Habits(Enum):

    WORK_ON_RESOLUTIONS = "work on resolutions"
    READ = "read"
    SLEEP_MORE_THAN_7_HOURS = "sleep more than 7 hours"
    GO_TO_BED_EARLY = "go to bed early"
    PLAN_DAY = "plan day"
    PLAN_WEEK = "plan week"
    PLAN_MONTH = "plan month"
    MEDITATE = "meditate"
    EXERCISE = "exercise"
    JOURNALING = "journaling"
    LEARN_LANGUAGE = "learn language"


def get_habit_headers() -> List[str]:
    return [identifier.value for identifier in Habits]
