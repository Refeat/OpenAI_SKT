from typing import Optional, Type
from pydantic import BaseModel

from langchain.tools import BaseTool

from database.database import DataBase

class DraftChunkTool(BaseTool):
    name = "draft_chunk_tool"
    description = "A tool to find the parts of a draft that match a query."
    args_schema: Optional[Type[BaseModel]] = None
    """Pydantic model class to validate and parse the tool's input arguments."""

    def __init__(self, database=None) -> None:
        super().__init__()
        self.database = database

    def set_database(self, database: DataBase):
        self.database = database

    def search(self, input_dict: dict) -> dict:
        query = input_dict['query']
        result = self.database.query(query)
        return result
    
    async def async_search(self, input_dict: dict) -> dict:
        query = input_dict['query']
        result = self.database.query(query)
        return result