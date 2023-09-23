import os
from typing import List

from models.llm import DraftEditAgent, GraphChain, UnifiedSummaryChunkChain
from tools import DatabaseTool, SearchTool, TimeTool, SearchByURLTool, GraphTool

current_file_absolute_path = os.path.abspath(__file__)

class DraftEditInstance:
    def __init__(self, 
                verbose=False, 
                search_tool=None,
                database_tool=None,
                graph_tool=None,
                search_by_url_tool=None,
                summary_chunk_template=None,
                summary_chunk_input_variables=None,
                graph_template=None,
                graph_input_variables=None) -> None:
        self.summary_chunk_template = summary_chunk_template
        self.summary_chunk_input_variables = summary_chunk_input_variables
        self.graph_template = graph_template
        self.graph_input_variables = graph_input_variables

        self.search_by_url_tool = search_by_url_tool
        self.search_tool = search_tool
        self.database_tool = database_tool
        self.graph_tool = graph_tool

        if search_tool == None:
            self.search_tool = SearchTool(search_by_url_tool=self.search_by_url_tool)
        if database_tool == None:
            self.database_tool = DatabaseTool()
        if graph_tool == None:
            self.graph_tool = GraphTool()
        if search_by_url_tool == None:
            self.search_by_url_tool = SearchByURLTool()

        # tools = [self.database_tool, self.search_tool, self.graph_tool, self.search_by_url_tool]
        tools = [self.database_tool, self.graph_tool]

        self.draft_edit_agent = DraftEditAgent(tools=tools, verbose=True, model='gpt-4')

    def run(self, database, query:str, draft, draft_part:str):
        tools = self.set_tools(database)
        modified_draft_part = self.draft_edit_agent.run(tools=tools, query=query, draft_part=draft_part)
        self.parse_result(draft, draft_part, modified_draft_part)
        return draft
    
    async def arun(self, database, question:str, qna_history:List[List[str]]):
        tools = self.set_tools(database)
        answer = await self.qna_agent.arun(tools=tools, question=question, qna_history=qna_history)
        return answer
    
    def set_tools(self, database):
        database_tool = DatabaseTool()
        database_tool.set_database(database)
        # tools = [database_tool, self.search_tool, self.graph_tool]
        tools = [database_tool, self.graph_tool]
        return tools
    
    def parse_result(self, draft, draft_part:str, modified_draft_part:str):
        draft.edit(draft_part, modified_draft_part)