from typing import Optional, Type
from pydantic import BaseModel

from langchain.tools import BaseTool

from models.llm.chain import DraftChunkChain

draft_chunk_chain = DraftChunkChain()

class DraftChunkTool(BaseTool):
    name = "draft_chunk_tool"
    description = "A tool to extract a part of draft that corresponds to the user's query."
    args_schema: Optional[Type[BaseModel]] = None
    """Pydantic model class to validate and parse the tool's input arguments."""

    draft_chunk_chain: Any 

    def __init__(self, draft_chunk_chain) -> None:
        super().__init__()
        self.draft_chunk_chain = draft_chunk_chain

    def _run(self, draft:str, query:str) -> dict:
        result = self.draft_chunk_chain.run(draft=draft, query=query)
        return result
    
    async def _arun(self, draft:str, query:str) -> dict:
        result = await self.draft_chunk_chain.arun(draft=draft, query=query)
        return result