from pydantic import BaseModel


class PostgresCredentials(BaseModel):
    table: str
    database: str
    db_schema: str
    host: str
    user: str
    password: str
    port: int
