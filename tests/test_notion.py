import datetime
import os

from assertpy import assert_that
from controllers.notion_controller import NotionController

date = "2022-01-20"
notion = NotionController(date, os.getenv('NT_auth'), notion_version='2021-08-16', object_id="811f2937421e488793c3441b8ca65509")


def test_get_completion_percentage():
    completion_percentage = notion.get_completion_percentage()

    assert_that(completion_percentage).is_type_of(float)
    assert_that(completion_percentage).is_equal_to(33.33)


def test_get_amount_points():
    points = notion.get_points()

    assert_that(points).is_type_of(int)
    assert_that(points).is_equal_to(37)


def test_get_amount_energy():
    energy = notion.get_energy_amount()

    assert_that(energy).is_type_of(int)
    assert_that(energy).is_equal_to(21)


def test_get_amount_focus_time():
    focus_time = notion.get_focus_time()

    assert_that(focus_time).is_type_of(float)
    assert_that(focus_time).is_equal_to(8.48)


def test_get_reading_time():
    reading_time = notion.get_reading_time()

    assert_that(reading_time).is_type_of(float)
    assert_that(reading_time).is_equal_to(0.25)
