from datetime import date
from assertpy import assert_that
from controllers.rescuetime_controller import RescuetimeController
from data.constants.time_metrics import TimeMetrics


current_date = date.today().strftime("%Y-%m-%d")
rescuetime = RescuetimeController()


def test_get_productivity_time():

    productivity_time = rescuetime.get_recorded_time(current_date)
    work_time = productivity_time[TimeMetrics.WORK_TIME]
    leisure_time = productivity_time[TimeMetrics.LEISURE_TIME]

    assert_that(productivity_time).is_length(2)
    assert_that(work_time).is_type_of(float)
    assert_that(leisure_time).is_type_of(float)


def test_wrong_date():
    wrong_date = "error_date"

    assert_that(rescuetime.get_recorded_time).raises(KeyError).when_called_with(wrong_date)


def test_wrong_credentials():
    rescuetime.API_key = ""

    assert_that(rescuetime.get_recorded_time).raises(KeyError).when_called_with(current_date)
