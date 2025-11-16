from datetime import datetime, timedelta
from enum import Enum
import json
import os

from dotenv import load_dotenv
import requests

load_dotenv()


class HealthConnectSource(Enum):
    GOOGLE_FITNESS = "com.google.android.apps.fitness"
    XIAOMI_WEARABLE = "com.xiaomi.wearable"


class HealthConnectClient:

    HC_HOST = os.getenv('HC_BASE_URL')
    if not HC_HOST:
        raise ValueError("Health Connect base URL (HC_HOST) is not set")

    BASE_URL = HC_HOST + "/api/v2"

    def __init__(self, username: str, password: str, api_token: str | None = None, refresh_token: str | None = None):
        self.token, self.refresh_token = self.validate_token(username, password, api_token, refresh_token)
        self.headers = {"Content-Type": "application/json",
                        "Authorization": f"Bearer {self.token}"}

    def _login(self, username: str, password: str):
        """Login to HealthConnect and return the token and refresh token."""
        payload = json.dumps({"username": username, "password": password})
        headers = {"Content-Type": "application/json"}

        response = requests.post(self.BASE_URL + "/login", headers=headers, data=payload)
        response.raise_for_status()

        response_data = response.json()
        return response_data["token"], response_data["refresh"]

    def validate_token(self,
                       username: str,
                       password: str,
                       api_token: str | None,
                       refresh_token: str | None) -> tuple[str, str]:
        """Validate the token and refresh token. If the token is invalid, try to refresh it.
           If the refresh token is invalid, login again.

        Args:
            api_token: The api token to validate.
            refresh_token: The refresh token to validate.
            username: The username to login with.
            password: The password to login with.

        Returns:
            A tuple with the token and refresh token.
        """
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {api_token}"}
        payload = json.dumps({"queries": {}})

        current_token_response = requests.post(self.BASE_URL + "/fetch/steps", headers=headers, data=payload)
        if current_token_response.ok and api_token and refresh_token:
            return api_token, refresh_token

        if refresh_token:
            headers = {"Content-Type": "application/json"}
            payload = json.dumps({"refresh": refresh_token})
            response = requests.post(self.BASE_URL + "/refresh", headers=headers, data=payload)

            if response.ok:
                return response.json()["token"], response.json()["refresh"]

        return self._login(username, password)

    @staticmethod
    def _get_request_query(date: str = "", app_id: str = "") -> dict:
        query: dict = {"queries": {}}

        if date:
            end_filter_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
            query["queries"]["start"] = {"$gte": f"{date}T05:00:00Z",
                                         "$lt": f"{end_filter_date}T05:00:00Z"}

        if app_id:
            query["queries"]["app"] = app_id

        return query

    def get_steps(self, date: str, app_id: str) -> int:
        """Get the number of steps for a given date.

        Args:
            date: The date to get the steps for in the format YYYY-MM-DD.
            app_id: The app id to get the steps for.

        Returns:
            The number of steps for the given date.
        """
        payload = self._get_request_query(app_id=app_id)
        end_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
        payload["queries"]["start"] = {"$gte": f"{date}T09:00:00Z",
                                       "$lt": f"{end_date}T04:00:00Z"}

        response = requests.post(self.BASE_URL + "/fetch/steps", headers=self.headers, data=json.dumps(payload))
        response.raise_for_status()

        total_steps = 0
        for step_object in response.json():
            total_steps += step_object["data"]["count"]

        return total_steps

    def get_sleep(self, date: str, app_id: str, sleep_stages: list[int]) -> tuple[float | None, dict[int, float]]:
        """Get the number of sleep for a given date.

        Args:
            date: The date to get the sleep for in the format YYYY-MM-DD.
            app_id: The app id to get the sleep for.
            sleep_stages: The sleep stages to get the sleep for. Official sleep stages are:
                            - 0: UNKNOWN
                            - 1: AWAKE
                            - 2: SLEEPING
                            - 3: OUT_OF_BED
                            - 4: LIGHT
                            - 5: DEEP
                            - 6: REM
                            - 7: AWAKE_IN_BED

        Returns:
            A tuple with the fall asleep time and a dictionary with the sleep stages as keys
            and the number of sleep hours for the given date as values.
        """
        payload = self._get_request_query(app_id=app_id)
        payload["queries"]["start"] = {"$gte": f"{date}T01:00:00Z",
                                       "$lt": f"{date}T15:00:00Z"}

        response = requests.post(self.BASE_URL + "/fetch/sleepSession", headers=self.headers, data=json.dumps(payload))
        response.raise_for_status()

        response_data = response.json()
        all_sleep_stages = []
        for sleep_chunk in response_data:
            all_sleep_stages.extend(sleep_chunk["data"]["stages"])

        total_sleep = {v: 0.0 for v in sleep_stages}
        for stage in all_sleep_stages:
            stage_type = stage["stage"]
            if stage_type not in sleep_stages:
                continue

            start_time = datetime.fromisoformat(stage["startTime"].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(stage["endTime"].replace('Z', '+00:00'))

            sleep_duration = (end_time - start_time).total_seconds()

            total_sleep[stage_type] += sleep_duration

        total_sleep = {k: round(v / 3600, 2) for k, v in total_sleep.items()}

        if not all_sleep_stages:
            return None, total_sleep

        fall_asleep_raw_time = datetime.fromisoformat(all_sleep_stages[0]["startTime"].replace('Z', '+00:00'))
        fall_asleep_time = (fall_asleep_raw_time - timedelta(hours=5)).strftime("%I.%M")

        return float(fall_asleep_time), total_sleep
