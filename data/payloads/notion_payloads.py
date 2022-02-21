import json


class NotionPayloads:

    @staticmethod
    def get_headers(notion_version: str, auth_secret: str) -> dict:
        headers = {
                    "content-type": "application/json",
                    "Notion-Version": f"{notion_version}",
                    "Authorization": f"Bearer {auth_secret}"
                }
        return headers

    @staticmethod
    def get_tasks(date: str) -> str:
        payload = {
                        "filter": {
                            "property": "Due date",
                            "date": {
                                "equals": date
                            }
                        }
                    }
        return json.dumps(payload)
