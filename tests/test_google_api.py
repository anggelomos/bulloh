import datetime

from assertpy import assert_that
from controllers.google_api_controller import GoogleAPIController

google_api = GoogleAPIController()


def test_get_sleeping_hours():
    one_good_answer = False

    for amount_days in range(30):
        evaluate_date = (datetime.date.today() - datetime.timedelta(days=amount_days)).strftime("%Y-%m-%d")

        sleep_time = google_api.get_sleep_time(evaluate_date)

        try:
            assert_that(sleep_time).is_type_of(float)
            assert_that(sleep_time).is_greater_than(0)
            one_good_answer = True
            break
        except AssertionError:
            pass

    assert_that(one_good_answer).is_true()


def test_old_sleep_record():

    old_date = "1990-01-01"
    sleep_time = google_api.get_sleep_time(old_date)
    assert_that(sleep_time).is_equal_to(-1)


def test_unexisting_sleep_record():
    current_date = (datetime.date.today() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

    sleep_time = google_api.get_sleep_time(current_date)
    assert_that(sleep_time).is_none()
