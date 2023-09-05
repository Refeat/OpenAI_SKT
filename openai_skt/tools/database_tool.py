from typing import Optional, Type
from pydantic import BaseModel

from langchain.tools import BaseTool

from database.database import DataBase

class DatabaseTool(BaseTool):
    name = "database"
    description = "A tool to extract data from a database with a query"
    args_schema: Optional[Type[BaseModel]] = None
    """Pydantic model class to validate and parse the tool's input arguments."""
    database: DataBase

    def __init__(self) -> None:
        super().__init__()

    def set_database(self, database: DataBase):
        self.database = database

    def _run(self, query) -> dict:
        result = self.database.query(query)
        return result
    
    async def _arun(self, query) -> dict:
        result = self.database.query(query)
        return result