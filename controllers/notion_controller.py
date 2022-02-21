import datetime
import logging
import statistics
from typing import List

import requests
from controllers.general_utilities import GeneralUtilities as gu
from data.payloads.notion_payloads import NotionPayloads
from data.tasks.task_notion_parameters import TaskNotionParameters as tnp
from data.tasks.task_data import TaskData


class NotionController:
    base_url = "https://api.notion.com/v1"

    def __init__(self, current_date: str, auth_secret: str, notion_version: str, object_id: str):
        self._auth_secret = auth_secret
        self._notion_version = notion_version
        self.object_id = object_id
        self.current_date = current_date
        self.tasks = []
        self.update_tasks()

    @staticmethod
    def _parse_task(raw_task: dict) -> dict:
        properties = raw_task[tnp.PROPERTIES]
        task = {}
        task[TaskData.NOTION_ID] = raw_task[tnp.ID]
        task[TaskData.DONE] = properties[tnp.DONE][tnp.CHECKBOX]
        task[TaskData.TITLE] = properties[tnp.TASK][tnp.TITLE][0][tnp.PLAIN_TEXT]
        task[TaskData.POINTS] = properties[tnp.POINTS][tnp.NUMBER]
        task[TaskData.ENERGY] = properties[tnp.ENERGY][tnp.NUMBER]
        task[TaskData.FOCUS_TIME] = properties[tnp.FOCUS_TIME][tnp.NUMBER]

        try:
            task[TaskData.TAGS] = list(map(lambda tag: tag[tnp.NAME], properties[tnp.TAGS][tnp.MULTI_SELECT]))
        except KeyError:
            task[TaskData.TAGS] = []

        return task

    def update_tasks(self):
        self.tasks = self.get_tasks(self.current_date)

    def get_tasks(self, current_date: str) -> List[dict]:
        logging.info("Getting notion active tasks")
        payload = NotionPayloads.get_tasks(current_date)
        response = requests.post(url=self.base_url + "/databases/" + self.object_id + "/query",
                                 data=payload,
                                 headers=NotionPayloads.get_headers(self._notion_version, self._auth_secret))

        raw_tasks = response.json()["results"]
        notion_tasks = list(map(self._parse_task, raw_tasks))

        return notion_tasks

    def get_completion_percentage(self) -> float:
        return gu.round_number(statistics.mean(map(lambda task: task[TaskData.DONE], self.tasks)) * 100)

    def get_points(self) -> int:
        return sum(map(lambda task: task[TaskData.POINTS], self.tasks))

    def get_energy_amount(self) -> int:
        return sum(map(lambda task: task[TaskData.ENERGY], self.tasks))

    def get_focus_time(self):
        return sum(map(lambda task: task[TaskData.FOCUS_TIME], self.tasks))

    def get_reading_time(self):
        last_day_day = gu.get_previous_date(self.current_date, 1, as_string=True)
        last_day_tasks = self.get_tasks(last_day_day)

        def is_reading_task(task): return set(task[TaskData.TAGS]) == {"read", "habit"}
        current_reading_time = list(filter(is_reading_task, self.tasks))[0][TaskData.FOCUS_TIME]
        last_day_reading_time = list(filter(is_reading_task, last_day_tasks))[0][TaskData.FOCUS_TIME]

        return current_reading_time - last_day_reading_time
