from typing import Optional, Type
from pydantic import BaseModel

from langchain.tools import BaseTool
from langchain.tools.python.tool import PythonREPLTool

from models.llm.chain import GraphChain

graph_chain = GraphChain()

class GraphTool(BaseTool):
    name = "graph_tool"
    description = "A tool to draw a graph. It return image path of the graph."
    args_schema: Optional[Type[BaseModel]] = None
    """Pydantic model class to validate and parse the tool's input arguments."""

    def __init__(self, graph_chain) -> None:
        super().__init__()
        self.graph_chain = graph_chain
        self.python_tool = PythonREPLTool()

    def draw_graph(self, query) -> dict:
        result = self.graph_chain.run(query=query)
        code, save_path = self.parse_result(result)
        if save_path is not None:
            result = self.python_tool.run(code=code)
            return save_path
        else:
            return None
    
    async def async_draw_graph(self, query) -> dict:
        result = await self.graph_chain.arun(query=query)
        code, save_path = self.parse_result(result)
        if save_path is not None:
            result = await self.python_tool.arun(code=code)
            return save_path
        else:
            return None
    
    def parse_result(self, result) -> str:
        start_code = result.find("```python") + len("```python")
        end_code = result.rfind("```")
        code = result[start_code:end_code].strip() # text of python code
        start_path = result.find('step4: ') + len('step4: ')
        save_path = result[start_path:].strip() if result[start_path:].strip() != 'No graph' else None
        return code, save_path