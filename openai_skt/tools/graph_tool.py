from typing import Optional, Type, Any
from pydantic import BaseModel

from langchain.tools import BaseTool
from langchain.tools.python.tool import PythonREPLTool

class GraphTool(BaseTool):
    name = "graph_tool"
    description = "A tool to draw a graph. The inputs are the table containing the data and the features of the graph you want to draw. It return image path of the graph."
    args_schema: Optional[Type[BaseModel]] = None
    """Pydantic model class to validate and parse the tool's input arguments."""

    graph_chain: Any
    python_tool: Any

    def __init__(self, graph_chain) -> None:
        super().__init__()
        self.graph_chain = graph_chain
        self.python_tool = PythonREPLTool()

    def _run(self, query) -> dict:
        result = self.graph_chain.run(query=query)
        code, save_path = self.parse_result(result)
        if save_path is not None:
            result = self.python_tool._run(code)
            return save_path
        else:
            return None
    
    async def _arun(self, query) -> dict:
        result = await self.graph_chain.arun(query=query)
        code, save_path = self.parse_result(result)
        if save_path is not None:
            result = await self.python_tool._arun(code)
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