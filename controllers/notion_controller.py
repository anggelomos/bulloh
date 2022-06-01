import logging
from typing import List, Tuple
import requests
from data.payloads.notion_payloads import NotionPayloads
from data.tasks.task_notion_parameters import TaskNotionParameters as tnp
from data.tasks.task_data import TaskData


class NotionController:
    base_url = "https://api.notion.com/v1"
    tasks_table_id = "811f2937421e488793c3441b8ca65509"
    habits_table_id = "b19a57ac5bd14747bcf4eb0d98adef10"

    def __init__(self, auth_secret: str, notion_version: str):
        self._auth_secret = auth_secret
        self._notion_version = notion_version
        self.tasks = []
        self.habits = []

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

    def get_entries(self, current_date: str) -> Tuple[List[dict], List[dict]]:
        logging.info(f"Getting notion entries of {current_date}")
        tasks = []
        habits = []
        payload = NotionPayloads.get_tasks(current_date)
        response = requests.post(url=self.base_url + "/databases/" + self.tasks_table_id + "/query",
                                 data=payload,
                                 headers=NotionPayloads.get_headers(self._notion_version, self._auth_secret))

        raw_tasks = response.json()["results"]
        parsed_entries = list(map(self._parse_task, raw_tasks))

        for entry in parsed_entries:
            if "habit" in entry[TaskData.TAGS] and len(entry[TaskData.TAGS]) >= 2:
                if not list(filter(lambda habit: habit[TaskData.TITLE] == entry[TaskData.TITLE], habits)):
                    habits.append(entry)
            else:
                tasks.append(entry)

        self.tasks = tasks
        self.habits = habits
        return tasks, habits

    def get_points(self) -> int:
        logging.info("Getting tasks points")
        return sum(map(lambda task: task[TaskData.POINTS], self.tasks))

    def get_energy_amount(self) -> int:
        logging.info("Getting tasks amount of energy")
        return sum(map(lambda task: task[TaskData.ENERGY], self.tasks))

    def get_focus_time(self):
        logging.info("Getting tasks focus time")
        return sum(map(lambda task: task[TaskData.FOCUS_TIME] if task[TaskData.FOCUS_TIME] else 0, self.tasks))

    def get_habits_time(self):
        logging.info("Getting habits time")

        def process_habit_time(task: dict) -> tuple:
            habit_tag = list(filter(lambda tag: tag != "habit", task[TaskData.TAGS]))[0]
            habit_time = task[TaskData.FOCUS_TIME]

            return habit_tag, float(habit_time)

        return dict(map(process_habit_time, self.habits))

    def get_habits_checked(self):
        logging.info("Getting habits checked")

        def process_habit_checked(task: dict) -> tuple:
            habit_tag = list(filter(lambda tag: tag != "habit", task[TaskData.TAGS]))[0]
            habit_checked = task[TaskData.DONE]

            return habit_tag, habit_checked

        return dict(map(process_habit_checked, self.habits))
