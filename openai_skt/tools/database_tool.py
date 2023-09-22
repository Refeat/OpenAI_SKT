import ast
from typing import Optional, Type, Any, Union, Dict
from pydantic import BaseModel

from langchain.tools import BaseTool

from database.database import DataBase
from models.llm import UnifiedSummaryChunkChain

class DatabaseToolInputSchema(BaseModel):
    query: str
    question: str

class DatabaseTool(BaseTool):
    name = "database_tool"
    description = "A tool to get data with from database. The input consists of a 'query' and a 'question', where 'query' is the search query and 'question' is the information you want to get. For example, {'query': 'bitcoin price history', 'question': 'what was the price of bitcoin in 2022?'} would be the input if you want to know the price of bitcoin in 2022. Input must contain both a query and a question."
    database: DataBase= None
    args_schema: Optional[Type[BaseModel]] = DatabaseToolInputSchema
    """Pydantic model class to validate and parse the tool's input arguments."""
    summary_chunk_chain: Any = None

    def __init__(self, summary_chunk_chain=None) -> None:
        super().__init__()
        if summary_chunk_chain is None:
            self.summary_chunk_chain = UnifiedSummaryChunkChain()
        else:
            self.summary_chunk_chain = summary_chunk_chain

    def set_database(self, database: DataBase):
        self.database = database

    def _parse_input(self, tool_input: Union[str, Dict]) -> Union[str, Dict[str, Any]]:
        """Convert tool input to pydantic model."""
        input_args = self.args_schema
        if isinstance(tool_input, str):
            # parts = [s.strip().split(': ') for s in tool_input.split(',')]
                
            # Convert the list of [key, value] to a dictionary
            input_dict = ast.literal_eval(tool_input)
            
            return input_dict
        else:
            if input_args is not None:
                result = input_args.parse_obj(tool_input)
                return {k: v for k, v in result.dict().items() if k in tool_input}
        return tool_input

    def _run(self, query, question=None) -> dict:
        if question is None:
            question = query
        chunks = self.database.query(query)
        data = ''
        for idx, chunk in enumerate(chunks):
            data += f'chunk{idx+1}: {chunk.data}\n'
        summary_result = self.summary_chunk_chain.run(chunk=data, question=question)
        return summary_result
    
    async def _arun(self, query) -> dict:
        chunks = self.database.query(query)
        data = ''
        for idx, chunk in enumerate(chunks):
            data += f'{idx} chunk: {chunk.data}\n'
        return data