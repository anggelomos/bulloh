from enum import Enum

class Metrics(Enum):

    # Metrics date
    YEAR_DAY
    DATE
    DAY
    DAY_NAME
    WEEK
    MONTH
    COMPLETED

    # Time metrics
    WORK_TIME
    FOCUS_TIME
    LEISURE_TIME
    SLEEP_TIME
    READ_TIME

    # Habits
    MEDITATE
    PLAN_DAY
    WRITE
    LEARN_LANGUAGE
    EXERCISE
    READ
