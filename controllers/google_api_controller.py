import datetime
import os.path

import requests
from controllers.aws_controller import AWSController
from controllers.general_utilities import GeneralUtilities as gu
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GoogleAPIController:

    credentials_path = "../secrets/"
    credentials_file = "credentials_google_fit.json"
    token_file = "google_fit_token.json"

    def __init__(self):

        self.download_google_token()

        SCOPES = ["https://www.googleapis.com/auth/fitness.sleep.read"]

        creds = None
        if os.path.exists(self.credentials_path+self.token_file):
            creds = Credentials.from_authorized_user_file(self.credentials_path+self.token_file, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path + self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.credentials_path+self.token_file, "w") as token:
                token.write(creds.to_json())

        self.upload_google_token()
        self.token = creds.token
        self.sleep_url = "https://www.googleapis.com/fitness/v1/users/me/sessions?activityType=72"

    def get_header_token(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }

    def download_google_token(self):
        AWSController().download_file(self.credentials_path + self.credentials_file, self.credentials_file)
        AWSController().download_file(self.credentials_path + self.token_file, self.token_file)

    def upload_google_token(self):
        AWSController().upload_file(self.credentials_path + self.credentials_file, self.credentials_file)
        AWSController().upload_file(self.credentials_path + self.token_file, self.token_file)

    def get_sleep_time(self, current_date: str) -> float:
        start_date_milliseconds = gu.get_date_in_milliseconds(current_date)
        end_date_milliseconds = gu.get_date_in_milliseconds(gu.parse_date(current_date) + datetime.timedelta(days=1))
        sleep_sessions = requests.get(self.sleep_url, headers=self.get_header_token()).json()["session"]

        filtered_sleep_sessions = list(filter(lambda x: int(x["startTimeMillis"]) > start_date_milliseconds and int(x["startTimeMillis"]) < end_date_milliseconds, sleep_sessions))

        if (datetime.date.today() - gu.parse_date(current_date).date()).days > 5:
            return -1

        sleep_time = None
        for sleep_session in filtered_sleep_sessions:
            if "analysis" in sleep_session["name"]:
                return gu.round_number(gu.convert_milliseconds_to_hours(int(sleep_session["endTimeMillis"]) - int(sleep_session["startTimeMillis"])))

            sleep_time = gu.round_number(gu.convert_milliseconds_to_hours(int(sleep_session["endTimeMillis"]) - int(sleep_session["startTimeMillis"])))

        return sleep_time
