import logging
from typing import Dict

from controllers.rescuetime_controller import RescuetimeController
from data.constants.habits_time import get_habit_time_headers
from data.constants.ticktick_ids import TicktickIds
from utilities.general_utilities import GeneralUtilities as GU
from controllers.ticktick.ticktick_controller import TicktickController
from utilities.habit_utilities import HabitUtilities


class BullohController:

    @staticmethod
    def process_time(rescuetime: RescuetimeController, ticktick: TicktickController, date: str) -> Dict[str, float]:
        logging.info(f"Processing time data for date: {date}")
        work_and_leisure_time = rescuetime.get_recorded_time(date)
        focus_time = ticktick.get_general_focus_time(date)

        return {**work_and_leisure_time, **focus_time}

    @staticmethod
    def process_habits(ticktick: TicktickController, date: str) -> Dict[str, bool]:
        logging.info(f"Processing habits data for date: {date}")

        int_date = GU.date_to_int(date)
        habit_checkins_raw = ticktick.get_habits(date)

        habit_checkins = {}
        for habit_id, checkins in habit_checkins_raw.items():
            habit_checkins[TicktickIds.habit_list[habit_id]] = HabitUtilities.clean_habit_checkins(checkins, int_date)

        return habit_checkins

    @staticmethod
    def process_habits_time(ticktick: TicktickController, date: str) -> Dict[str, float]:
        logging.info(f"Processing habits time data for date: {date}")
        habits_time = dict(zip(get_habit_time_headers(), [0]*len(get_habit_time_headers())))
        habits_time_raw = ticktick.get_habits_time(date)

        if habits_time_raw:
            for habit in habits_time.keys():
                clean_habit = habit.replace(" time", "-habit")

                habit_time = sum([time for tag, time in habits_time_raw.items() if clean_habit in tag])
                habits_time[habit] = GU.round_number(habit_time / 60)

        return habits_time
