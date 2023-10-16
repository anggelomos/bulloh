import os
from datetime import date

import pytest

from bulloh.rescuetime_client import RescuetimeClient

current_date = date.today().strftime("%Y-%m-%d")


@pytest.fixture
def rescuetime_client():
    return RescuetimeClient(os.getenv("RT_API_KEY"))


def test_get_productivity_time(rescuetime_client):
    productivity_time = rescuetime_client.get_productive_time(current_date)

    assert isinstance(productivity_time, float)
    assert productivity_time >= 0


def test_get_leisure_time(rescuetime_client):
    leisure_time = rescuetime_client.get_leisure_time(current_date)

    assert isinstance(leisure_time, float)
    assert leisure_time >= 0


def test_wrong_date(rescuetime_client):
    wrong_date = "error_date"

    with pytest.raises(KeyError):
        rescuetime_client.get_productive_time(wrong_date)


def test_wrong_credentials():
    with pytest.raises(KeyError):
        RescuetimeClient("").get_productive_time(current_date)
