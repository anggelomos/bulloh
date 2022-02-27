import os
from assertpy import assert_that
from controllers.notion_controller import NotionController
from data.constants.habits import Habits

date = "2022-01-20"
notion = NotionController(os.getenv('NT_auth'), notion_version='2021-08-16')
notion.get_entries(date)


def test_get_amount_points():
    points = notion.get_points()

    assert_that(points).is_type_of(int)
    assert_that(points).is_equal_to(34)


def test_get_amount_energy():
    energy = notion.get_energy_amount()

    assert_that(energy).is_type_of(int)
    assert_that(energy).is_equal_to(17)


def test_get_amount_focus_time():
    focus_time = notion.get_focus_time()

    assert_that(focus_time).is_type_of(float)
    assert_that(focus_time).is_equal_to(6.5)


def test_get_habits_time():
    habits_time = notion.get_habits_time()

    assert_that(habits_time).is_type_of(dict)
    for habit in Habits:
        habit_time = habits_time[habit.value]

        assert_that(habit_time).is_type_of(float)
        assert_that(habit_time).is_greater_than_or_equal_to(0)

    assert_that(sum(habits_time.values())).is_close_to(6.61, 0.1)


def test_get_habits_checked():
    habits_checked = notion.get_habits_checked()

    assert_that(habits_checked).is_type_of(dict)
    for habit in Habits:
        habit_time = habits_checked[habit.value]

        assert_that(habit_time).is_type_of(bool)

    assert_that(sum(habits_checked.values()) / len(habits_checked)).is_close_to(0.71, 0.1)
