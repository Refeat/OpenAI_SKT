from typing import List
import os

from models.llm import QnAAgent
from tools import DatabaseTool, SearchTool, TimeTool, SearchByURLTool
current_file_folder_path = os.path.dirname(os.path.abspath(__file__))

class QnAInstance:
    def __init__(self, 
                verbose=False, 
                search_tool=None,
                database_tool=None,
                qna_prompt_path=os.path.join(current_file_folder_path, "templates/qna_prompt_template.txt"),
                summary_chunk_template=None,
                input_variables=None,) -> None:
        self.summary_chunk_template = summary_chunk_template
        self.input_variables = input_variables

        self.search_by_url_tool = SearchByURLTool()
        self.time_tool = TimeTool()
        self.search_tool = search_tool
        self.database_tool = database_tool

        if search_tool == None:
            self.search_tool = SearchTool(search_by_url_tool=self.search_by_url_tool)
        if database_tool == None:
            self.database_tool = DatabaseTool()

        # tools = [self.database_tool, self.search_tool, self.time_tool]
        tools = [self.database_tool, self.time_tool]
        self.qna_agent = QnAAgent(
            tools=tools, verbose=True, model="gpt-3.5-turbo-16k", qna_prompt_path=qna_prompt_path
        )

    def run(self, database, question: str, qna_history: List[List[str]], queue=None):
        tools = self.set_tools(database)
        answer = self.qna_agent.run(tools=tools, question=question, qna_history=qna_history, queue=queue)
        return answer
    
    async def arun(self, database, question:str, qna_history:List[List[str]], queue=None):
        tools = self.set_tools(database)
        answer = await self.qna_agent.run(tools=tools, question=question, qna_history=qna_history, queue=queue)
        return answer

    def set_tools(self, database):
        database_tool = DatabaseTool()
        database_tool.set_database(database)
        tools = [database_tool, self.search_tool, self.time_tool]
        return tools
