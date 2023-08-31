import json
from typing import List

from database.database import DataBase
from models.llm.chain import KeywordsChain, DraftChain
from models.draft_generator import DraftGeneratorInstance
from models.keywords_generator import KeywordsGeneratorInstance
from models.qna_assistant import QnAInstance

keywords_chain = KeywordsChain()
draft_chain = DraftChain()

class UserInstance:
    def __init__(self) -> None:
        self.database = None
        self.keywords = None
        self.database_path = None
        self.qna_history = None

        self.keywords_generator_instance = None
        self.draft_generator_instance = None
        self.qna_instance = None
    
    def set_purpose(self, purpose:str=None):
        if purpose is not None:
            self.purpose = purpose
        else:
            raise ValueError("purpose must be specified")
        if self.keywords_generator_instance is None:
            self.keywords_generator_instance = KeywordsGeneratorInstance(chain=keywords_chain)


    def init_instance(self, purpose=None, keywords=None, files:List[tuple]=None):
        assert purpose is not None
        self.purpose = purpose
        self.keywords = keywords
        self.database = DataBase.init_database(files=files)
        self.draft_generator_instance = DraftGeneratorInstance(database=self.database, draft_chain=draft_chain)
        self.qna_instance = QnAInstance(database=self.database)

    def load_instance(self, user_instance_path:str=None):
        assert user_instance_path is not None
        with open(user_instance_path, "r") as f:
            user_instance = json.load(f)
        self.purpose = user_instance["purpose"]
        self.keywords = user_instance["keywords"]
        self.database_path = user_instance["database_path"]
        self.database = DataBase.load_database(database_path=self.database_path)
        self.draft_generator_instance = DraftGeneratorInstance(database=self.database, draft_chain=draft_chain)
        self.qna_instance = QnAInstance(database=self.database)

    
    def get_keywords(self):
        keywords = self.keywords_generator_instance.run(purpose=self.purpose) # List[str]
        return keywords
    
    async def async_get_keywords(self):
        keywords = await self.keywords_generator_instance.arun(purpose=self.purpose)
        return keywords

    def get_draft(self):
        # purpose, keywords, database
        keywords = self.draft_generator_instance.run(purpose=self.purpose, keywords=self.keywords)
        return keywords

    async def async_get_draft(self):
        # purpose, keywords, database
        keywords = await self.draft_generator_instance.arun(purpose=self.purpose, keywords=self.keywords)
        return keywords

    def get_answer(self, question:str=None):
        answer = self.qna_instance.run(question=question, qna_history=self.qna_history)
        if self.qna_history is None:
            self.qna_history = [question, answer]
        else:
            self.qna_history.append([question, answer])
        return answer

    async def async_get_answer(self, question:str=None):
        answer = await self.qna_instance.arun(question=question, qna_history=self.qna_history)
        if self.qna_history is None:
            self.qna_history = [question, answer]
        else:
            self.qna_history.append([question, answer])
        return answer


if __name__ == "__main__":
    pass