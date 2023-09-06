from typing import Optional, Type, Any
from pydantic import BaseModel

from langchain.tools import BaseTool

class DraftChunkTool(BaseTool):
    name = "draft_chunk_tool"
    description = "A tool to extract a part of draft that corresponds to the user's query."
    args_schema: Optional[Type[BaseModel]] = None
    """Pydantic model class to validate and parse the tool's input arguments."""

    draft_chunk_chain: Any
    draft: str = None

    def __init__(self, draft_chunk_chain) -> None:
        super().__init__()
        self.draft_chunk_chain = draft_chunk_chain

    def set_draft(self, draft):
        self.draft = draft

    def _run(self, query:str) -> dict:
        result = self.draft_chunk_chain.run(draft=self.draft, query=query)
        return result
    
    async def _arun(self, query:str) -> dict:
        result = await self.draft_chunk_chain.arun(draft=self.draft, query=query)
        return result