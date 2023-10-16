import math

import pytest
from tickthon import Task

from bulloh import Bulloh


@pytest.fixture
def bulloh():
    return Bulloh()


def test_process_weight(bulloh):
    expected_weight = 99.9
    date = "2099-09-09"
    weight_logs = [Task(title="test weright wrong", ticktick_id="", ticktick_etag="", created_date="2099-01-01"),
                   Task(title="weight measurement: 99.9", ticktick_id="", ticktick_etag="", created_date="2099-09-09"),
                   Task(title="test weright wrong", ticktick_id="", ticktick_etag="", created_date="2099-01-01"),]

    weight = bulloh.process_weight(date, weight_logs)

    assert isinstance(weight, float)
    assert math.isclose(weight, expected_weight)


def test_process_weight_without_logs(bulloh):
    expected_weight = 0.0
    date = "2099-09-09"
    weight_logs = [Task(title="weight measurement: 99.9", ticktick_id="", ticktick_etag="", created_date="2099-01-01"),
                   Task(title="weight measurement: 99.9", ticktick_id="", ticktick_etag="", created_date="2099-01-02"),
                   Task(title="weight measurement: 99.9", ticktick_id="", ticktick_etag="", created_date="2099-01-03")]

    weight = bulloh.process_weight(date, weight_logs)

    assert isinstance(weight, float)
    assert math.isclose(weight, expected_weight)
