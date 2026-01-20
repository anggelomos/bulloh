import os

from dotenv import load_dotenv
import pytest

from bulloh.health_connect_client import HealthConnectClient, HealthConnectSource

load_dotenv()

TEST_DATE = "2025-11-14"

@pytest.fixture
def health_connect_client():
    return HealthConnectClient(
        username=os.getenv("HC_USERNAME"),
        password=os.getenv("HC_PASSWORD")
    )


@pytest.mark.xfail(reason="Health Connect client temporarily disabled")
def test_get_steps(health_connect_client):
    steps = health_connect_client.get_steps(TEST_DATE, HealthConnectSource.GOOGLE_FITNESS.value)

    assert isinstance(steps, int)
    assert steps > 0


@pytest.mark.xfail(reason="Health Connect client temporarily disabled")
def test_get_sleep(health_connect_client):
    fall_asleep_time, sleep_stages = health_connect_client.get_sleep(
        TEST_DATE, 
        HealthConnectSource.GOOGLE_FITNESS.value, 
        [4, 5, 6]
    )
    
    # Calculate totals like in main.py
    total_sleep_time = round(sum(sleep_stages.values()), 2)
    deep_sleep_time = round(sum([st for ss, st in sleep_stages.items() if ss == 5 ]), 2)
    rem_sleep_time = round(sum([st for ss, st in sleep_stages.items() if ss == 6 ]), 2)

    # Verify sleep data structure
    assert isinstance(sleep_stages, dict)
    assert len(sleep_stages) == 3
    
    # Verify fall asleep time (can be None or float)
    assert fall_asleep_time is None or isinstance(fall_asleep_time, float)
    
    # Verify sleep totals are valid
    assert isinstance(total_sleep_time, float)
    assert total_sleep_time > 0
    assert isinstance(deep_sleep_time, float)
    assert deep_sleep_time > 0
    assert isinstance(rem_sleep_time, float)
    assert rem_sleep_time > 0
