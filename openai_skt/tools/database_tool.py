from typing import Optional, Type
from pydantic import BaseModel

from langchain.tools import BaseTool

from database.database import DataBase

class DatabaseTool(BaseTool):
    name = "database"
    description = "A tool to get data with a input question. Input should be a fully formed question in Korean."
    database: DataBase= None

    def __init__(self) -> None:
        super().__init__()

    def set_database(self, database: DataBase):
        self.database = database

    def _run(self, query) -> dict:
        chunks = self.database.query(query)
        data = ''
        for idx, chunk in enumerate(chunks):
            data += f'chunk{idx+1}: {chunk.data}\n'
        return data
    
    async def _arun(self, query) -> dict:
        chunks = self.database.query(query)
        data = ''
        for idx, chunk in enumerate(chunks):
            data += f'{idx} chunk: {chunk.data}\n'
        return data