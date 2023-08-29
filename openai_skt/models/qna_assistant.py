from typing import List

from models.llm.agent import QnAAgent

class QnAInstance:
    def __init__(self, database=None) -> None:
        self.database = database
        self.qna_agent = QnAAgent(database=self.database)

    def run(self, question:str=None, qna_history:List[List[str]]=None):
        answer = self.qna_agent.run(question=question, qna_history=qna_history)
        return answer
    
    async def arun(self, question:str=None, qna_history:List[List[str]]=None):
        answer = await self.qna_agent.arun(question=question, qna_history=qna_history)
        return answer