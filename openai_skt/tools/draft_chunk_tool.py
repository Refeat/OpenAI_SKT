from typing import Optional, Type
from pydantic import BaseModel

from langchain.tools import BaseTool

from database.database import DataBase
from models.llm.chain import DraftChunkChain

draft_chunk_chain = DraftChunkChain()

class DraftChunkTool(BaseTool):
    name = "draft_chunk_tool"
    description = "A tool to find the parts of a draft that match a query."
    args_schema: Optional[Type[BaseModel]] = None
    """Pydantic model class to validate and parse the tool's input arguments."""

    def __init__(self, draft_chunk_chain) -> None:
        super().__init__()
        self.draft_chunk_chain = draft_chunk_chain

    def search(self, query, draft, table) -> dict:
        
        result = self.draft_chunk_chain.run()
        return result
    
    async def async_search(self, draft, query) -> dict:
        result = await self.draft_chunk_chain.arun(query)
        return result
    
    def parse_input(self, query, draft, table):
        # table list로 변경
        input_dict = {'query': query, 'draft': draft, 'table': table}
        return input_dict