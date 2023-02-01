import datetime
import json
from typing import Union


class NotionPayloads:

    @staticmethod
    def get_headers(notion_version: str, auth_secret: str) -> dict:
        return {
                "content-type": "application/json",
                "Notion-Version": f"{notion_version}",
                "Authorization": f"Bearer {auth_secret}"
                }

    @staticmethod
    def get_checked_rows() -> str:
        payload = {
                  "sorts": [{"property": "date", "direction": "ascending"}],
                  "filter": {"and": [{"property": "completed", "checkbox": {"equals": True}}]}
                  }
        return json.dumps(payload)

    @staticmethod
    def get_data_between_dates(initial_date: Union[str, datetime.date], today_date: Union[str, datetime.date]) -> str:
        if isinstance(initial_date, datetime.date):
            initial_date = initial_date.strftime("%Y-%m-%d")

        if isinstance(today_date, datetime.date):
            today_date = today_date.strftime("%Y-%m-%d")

        filters = []
        if initial_date:
            filters.append({"property": "date","date": {"on_or_after": initial_date}})

        filters.append({"property": "date", "date": {"on_or_before": today_date}})

        return json.dumps({"sorts": [{"property": "day #", "direction": "ascending"}], "filter": {"and": filters}})

    @classmethod
    def get_date_rows(cls, date: str) -> str:
        return json.dumps({"filter": {"and": [{"property": "date", "date": {"equals": date}}]}})

    @classmethod
    def update_row(cls, row_data: dict) -> str:
        payload = {"properties": {}}
        for header, value in row_data.items():
            if header is None:
                payload["properties"][header] = {"number": None}
            elif isinstance(value, bool):
                payload["properties"][header] = {"checkbox": value}
            elif isinstance(value, int) or isinstance(value, float):
                payload["properties"][header] = {"number": value}
            else:
                raise ValueError("Unknown property type")

        return json.dumps(payload)
