from typing import Union

from data.constants.row_identifier import RowIdentifier


class PostgresQueries:

    year_day_header = RowIdentifier.YEAR_DAY.value

    @staticmethod
    def get_column_names(schema: str, table: str) -> str:
        return f"""SELECT column_name
                    FROM information_schema.columns
                   WHERE table_schema = '{schema}'
                    AND table_name   = '{table}'
                   ORDER BY ordinal_position;"""

    @classmethod
    def get_incomplete_dates(cls, date: str, table: str) -> str:
        return f"""SELECT *
                   FROM {table}
                    WHERE
                      "date"  <= '{date}'
                      AND completed = false
                   ORDER BY {cls.year_day_header} ASC NULLS LAST;"""

    @classmethod
    def get_database(cls, table: str) -> str:
        return f"""SELECT *
                   FROM {table}
                   ORDER BY {cls.year_day_header} ASC NULLS LAST;"""

    @classmethod
    def update_row(cls, day: Union[int, str], table: str, data: list) -> str:
        processed_data = list(map(lambda data_entry: "{0} = {1}".format(*data_entry), data))
        return f"""UPDATE {table}
                   SET {", ".join(processed_data)}
                   WHERE {cls.year_day_header} = {day};"""
