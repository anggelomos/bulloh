import itertools
import json
import logging
from typing import List

import psycopg2

from config import ROOT_DIR
from data.constants.row_identifier import RowIdentifier
from data.data_models.postgres_data_models import PostgresCredentials
from data.payloads.postgres_queries import PostgresQueries as pq


class PostgresController:

    resources_path = ROOT_DIR + "/resources/"
    credentials_file = "credentials_postgresql.json"

    def __init__(self):

        with open(self.resources_path+self.credentials_file, 'r') as f:
            self.credentials_data = PostgresCredentials(**json.load(f))

        self.postgres_conn = psycopg2.connect(database=self.credentials_data.database,
                                              host=self.credentials_data.host,
                                              user=self.credentials_data.user,
                                              password=self.credentials_data.password,
                                              port=self.credentials_data.port)

        self.postgres_cursor = self.postgres_conn.cursor()
        self.headers = self._get_headers()
        self.bulloh_database = []

    def _get_headers(self) -> List[str]:
        self.postgres_cursor.execute(pq.get_column_names(self.credentials_data.db_schema, self.credentials_data.table))
        return list(itertools.chain(*self.postgres_cursor.fetchall()))

    def close_session(self):
        self.postgres_conn.close()

    def _add_data_headers(self, data: list) -> List[dict]:

        def add_headers(row: list):
            row_dict = {}
            for index, header in enumerate(self.headers):
                row_dict[header] = row[index]

            return row_dict

        return list(map(add_headers, data))

    def get_database(self):
        logging.info("Getting database")

        self.postgres_cursor.execute(pq.get_database(self.credentials_data.table))
        raw_data = self.postgres_cursor.fetchall()

        self.bulloh_database = self._add_data_headers(raw_data)

    def get_incomplete_dates(self, current_date: str) -> list:
        logging.info(f"Getting incomplete dates for {current_date}")

        self.postgres_cursor.execute(pq.get_incomplete_dates(current_date, self.credentials_data.table))
        raw_data = self.postgres_cursor.fetchall()
        incomplete_dates = self._add_data_headers(raw_data)

        def process_incomplete_dates(raw_row: dict) -> list:
            return [int(raw_row[RowIdentifier.YEAR_DAY.value]), raw_row[RowIdentifier.DATE.value]]

        return list(map(process_incomplete_dates, incomplete_dates))

    def update_row(self, day: int, data: list):
        logging.info(f"Updating row day {day} with data {data}")

        self.postgres_cursor.execute(pq.update_row(day, self.credentials_data.table, data))
        self.postgres_conn.commit()
