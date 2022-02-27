import datetime
from assertpy import assert_that
from controllers.general_utilities import GeneralUtilities
from controllers.google_api_controller import GoogleAPIController
from data.constants.habits import Habits
from data.constants.row_identifier import RowIdentifier
from data.constants.time_metrics import TimeMetrics


google_api = GoogleAPIController()


def test_get_sleeping_hours():
    one_good_answer = False

    for amount_days in range(30):
        evaluate_date = GeneralUtilities.get_previous_date(datetime.date.today(), amount_days, as_string=True)

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
    assert_that(sleep_time).is_equal_to(0)


def test_unexisting_sleep_record():
    current_date = (datetime.date.today() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

    sleep_time = google_api.get_sleep_time(current_date)
    assert_that(sleep_time).is_equal_to("")


def test_get_sheets_required_dates():
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    required_dates = google_api.get_incomplete_dates(current_date)
    day_number, date = required_dates[0]

    assert_that(required_dates).is_type_of(list)
    assert_that(day_number).is_type_of(int)
    assert_that(day_number).is_greater_than(0)
    assert_that(date).is_type_of(str)
    assert_that(date).matches(r"\d{4}-\d{2}-\d{2}")


def test_update_sheets():
    amount_columns = len(google_api.bulloh_database[0]) - len(list(RowIdentifier))

    # Updating sheets data
    row_data = [1] * amount_columns
    google_api.update_sheets(day=366, data=row_data)
    updated_sheets = google_api.get_sheets_data()
    test_row = updated_sheets[-1]

    assert_that(test_row[RowIdentifier.COMPLETED.value]).is_equal_to("TRUE")
    for habit in Habits:
        assert_that(test_row[habit.value]).is_equal_to(1)

    for time_metrics in TimeMetrics:
        assert_that(test_row[time_metrics.value]).is_equal_to(1)

    # Reverting data to original the state
    row_data = [""] * amount_columns
    google_api.update_sheets(day=366, data=row_data)
    updated_sheets = google_api.get_sheets_data()
    test_row = updated_sheets[-1]

    assert_that(test_row[RowIdentifier.COMPLETED.value]).is_equal_to("FALSE")
    for habit in Habits:
        assert_that(test_row[habit.value]).is_equal_to("")

    for time_metrics in TimeMetrics:
        assert_that(test_row[time_metrics.value]).is_equal_to("")
