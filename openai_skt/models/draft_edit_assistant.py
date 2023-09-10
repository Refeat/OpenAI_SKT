from typing import List

from models.llm import DraftEditAgent
from tools import DatabaseTool, SearchTool, TimeTool, SearchByURLTool

search_by_url_tool = SearchByURLTool()
search_tool = SearchTool(search_by_url_tool=search_by_url_tool)
time_tool = TimeTool()
database_tool = DatabaseTool()

tools=[database_tool, search_tool, time_tool]

class DraftEditInstance:
    def __init__(self, verbose=False) -> None:
        self.draft_edit_agent = DraftEditAgent(tools=tools, verbose=verbose, model='gpt-3.5-turbo-16k')

    def run(self, database, query:str, draft:str):
        tools = self.set_tools(database)
        answer = self.draft_edit_agent.run(tools=tools, query=query, draft=draft)
        return answer
    
    async def arun(self, database, question:str, qna_history:List[List[str]]):
        tools = self.set_tools(database)
        answer = await self.qna_agent.arun(tools=tools, question=question, qna_history=qna_history)
        return answer
    
    def set_tools(self, database):
        database_tool = DatabaseTool()
        database_tool.set_database(database)
        tools = [database_tool, search_tool, time_tool]
        return tools