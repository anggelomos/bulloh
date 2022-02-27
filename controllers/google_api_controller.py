import datetime
import logging
import os.path
import sys
from typing import List

import requests

from config import ROOT_DIR
from controllers.aws_controller import AWSController
from controllers.general_utilities import GeneralUtilities as gu
from data.constants.row_identifier import RowIdentifier
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GoogleAPIController:

    resources_path = ROOT_DIR + "/resources/"
    credentials_file = "credentials_google_api.json"
    token_file = "google_api_token.json"

    def __init__(self):

        self.download_google_token()

        SCOPES = ["https://www.googleapis.com/auth/fitness.sleep.read",
                  "https://www.googleapis.com/auth/spreadsheets"]

        creds = None
        if os.path.exists(self.resources_path + self.token_file):
            creds = Credentials.from_authorized_user_file(self.resources_path + self.token_file, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.resources_path + self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.resources_path + self.token_file, "w") as token:
                token.write(creds.to_json())

        self.upload_google_token()
        self.token = creds.token
        sheets_service = build('sheets', 'v4', credentials=creds)
        self.sheets = sheets_service.spreadsheets().values()
        self.sleep_url = "https://www.googleapis.com/fitness/v1/users/me/sessions?activityType=72"
        self.bulloh_sheet_id = "1HG9e6-tCuh5o9wq-IwKYab-PiFkuzpp06PUk_1KuS4w"
        self.sheet_read_range = "2022!A1:Y367"

        self.bulloh_database = self.get_sheets_data()

    def get_header_token(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }

    def download_google_token(self):
        logging.info("Downloading Google API token")
        AWSController().download_file(self.resources_path + self.credentials_file, self.credentials_file)
        AWSController().download_file(self.resources_path + self.token_file, self.token_file)

    def upload_google_token(self):
        logging.info("Uploading Google API token")
        AWSController().upload_file(self.resources_path + self.credentials_file, self.credentials_file)
        AWSController().upload_file(self.resources_path + self.token_file, self.token_file)

    def get_sleep_time(self, current_date: str) -> float:
        logging.info(f"Getting sleep time for {current_date}")
        start_date_milliseconds = gu.get_date_in_milliseconds(current_date)
        end_date_milliseconds = gu.get_date_in_milliseconds(gu.parse_date(current_date) + datetime.timedelta(days=1))
        sleep_sessions = requests.get(self.sleep_url, headers=self.get_header_token()).json()["session"]

        filtered_sleep_sessions = list(filter(lambda x: int(x["startTimeMillis"]) > start_date_milliseconds and int(x["startTimeMillis"]) < end_date_milliseconds, sleep_sessions))

        sleep_time = ""
        for sleep_session in filtered_sleep_sessions:
            if "analysis" in sleep_session["name"]:
                return gu.round_number(gu.convert_milliseconds_to_hours(int(sleep_session["endTimeMillis"]) - int(sleep_session["startTimeMillis"])))

            sleep_time = gu.round_number(gu.convert_milliseconds_to_hours(int(sleep_session["endTimeMillis"]) - int(sleep_session["startTimeMillis"])))

        if not sleep_time and (datetime.date.today() - gu.parse_date(current_date).date()).days > 3:
            sleep_time = 0

        return sleep_time

    def get_sheets_data(self) -> List[dict]:
        logging.info("Getting data from sheets")
        sheets_raw_data = self.sheets.get(spreadsheetId=self.bulloh_sheet_id,
                                          range=self.sheet_read_range).execute()["values"]

        headers = sheets_raw_data.pop(0)

        def add_headers(row: list):
            row_dict = {}

            for index, header in enumerate(headers):
                try:
                    if row[index].replace(".", "", 1).isdigit():
                        row_dict[header] = float(row[index])
                    else:
                        row_dict[header] = row[index]
                except IndexError:
                    row_dict[header] = ""

            return row_dict

        return list(map(add_headers, sheets_raw_data))

    def get_incomplete_dates(self, current_date: str) -> list:
        logging.info(f"Getting incomplete dates for {current_date}")
        raw_incomplete_dates = []

        for row in self.bulloh_database:

            if row[RowIdentifier.COMPLETED.value] == "FALSE":
                raw_incomplete_dates.append(row)

            if row[RowIdentifier.DATE.value] == current_date:
                break

        def process_incomplete_dates(raw_row: dict) -> list:
            return [int(raw_row[RowIdentifier.YEAR_DAY.value]), raw_row[RowIdentifier.DATE.value]]

        return list(map(process_incomplete_dates, raw_incomplete_dates))

    def update_sheets(self, day: float, data: list):
        logging.info(f"Updating sheets day {day} with data {data}")
        update_range = f"2022!H{int(day+1)}:Y{int(day+1)}"
        body = {
            "values": [data]
        }
        self.sheets.update(spreadsheetId=self.bulloh_sheet_id, range=update_range,
                           valueInputOption="USER_ENTERED", body=body).execute()
