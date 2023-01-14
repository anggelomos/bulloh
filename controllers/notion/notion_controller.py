import datetime
from typing import Union, List

from controllers.notion.notion_api import NotionAPI
from data.constants.habits import get_habit_headers
from data.constants.habits_time import get_habit_time_headers
from data.constants.row_identifier import RowIdentifier
from data.constants.time_metrics import get_time_headers
from utilities.general_utilities import GeneralUtilities
from data.payloads.notion_payloads import NotionPayloads as payloads


class NotionController:
    base_url = "https://api.notion.com/v1"
    stats_table_id = "baa09f8600924192b1e9ceef4cfa70ce"

    def __init__(self, auth_secret: str, notion_version: str):
        self.notion_client = NotionAPI(auth_secret, notion_version)

    @staticmethod
    def _parse_prop(prop: dict) -> Union[str, bool, float]:
        if "checkbox" in prop:
            return prop["checkbox"]
        elif "number" in prop:
            if not prop["number"]:
                return 0
            return prop["number"]
        elif "date" in prop:
            return prop["date"]["start"]
        elif "formula" in prop:
            return prop["formula"]["boolean"]
        else:
            raise ValueError("Unknown property type")

    def parse_rows(self, rows: Union[List[dict], dict], as_dict: bool = False) -> Union[list, dict]:
        headers = GeneralUtilities.get_all_headers()

        if isinstance(rows, dict):
            rows = [rows]

        rows_parsed = []
        for row in rows:
            row_data = []
            for header in headers:
                row_data.append(self._parse_prop(row["properties"][header]))

            if as_dict:
                rows_parsed.append(dict(zip(headers, row_data)))
            else:
                rows_parsed.append(row_data)

        return rows_parsed

    def _get_last_checked(self):
        checked_rows = self.notion_client.query_table(self.stats_table_id, payloads.get_checked_rows())
        if checked_rows:
            return self.parse_rows(checked_rows[-1], as_dict=True)[0]
        return None

    def get_incomplete_dates(self, today_date: datetime.date):
        initial_date = None
        last_checked_row = self._get_last_checked()
        if last_checked_row:
            initial_date = GeneralUtilities.get_previous_date(last_checked_row[RowIdentifier.DATE.value],
                                                              amount_days=14,
                                                              as_string=False)

        if initial_date and (today_date.year > initial_date.year):
            initial_date = None

        payload = payloads.get_data_between_dates(initial_date, today_date)
        incomplete_rows = self.parse_rows(self.notion_client.query_table(self.stats_table_id, payload), as_dict=True)

        return [row[RowIdentifier.DATE.value] for row in incomplete_rows]

    def update_row(self, date: str, row_data: dict):
        date_row = self.notion_client.query_table(self.stats_table_id, payloads.get_date_rows(date))
        row_headers = get_time_headers() + get_habit_headers() + get_habit_time_headers()
        row_id = date_row[0]["id"]

        notion_row_data_raw = self.parse_rows(date_row, as_dict=True)[0]
        notion_row_data = {header: value for header, value in notion_row_data_raw.items() if header in row_headers}

        if row_data != notion_row_data:
            self.notion_client.update_table_entry(row_id, payloads.update_row(row_data))
