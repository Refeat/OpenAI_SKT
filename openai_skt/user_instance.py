import json
from typing import List

from database import DataBase
from models.chain import KeywordsChain, DraftChain
from models.agent import QnAAgent
from draft_generator import DraftGeneratorInstance
from keywords_generator import KeywordsGeneratorInstance
from qna_assistant import QnAInstance

keywords_chain = KeywordsChain()
draft_chain = DraftChain()
qna_agent = QnAAgent()

class UserInstance:
    def __init__(self) -> None:
        self.keywords_generator_instance = None
        self.database = None
        self.draft_generator_instance = None
        self.qna_instance = None
        self.keywords = None
        self.database_path = None
    
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
        self.draft_generator_instance = DraftGeneratorInstance(database=self.database)
        self.qna_instance = QnAInstance(database=self.database)

    def load_instance(self, user_instance_path:str=None):
        assert user_instance_path is not None
        with open(user_instance_path, "r") as f:
            user_instance = json.load(f)
        self.purpose = user_instance["purpose"]
        self.keywords = user_instance["keywords"]
        self.database_path = user_instance["database_path"]
        self.database = DataBase.load_database(database_path=self.database_path)
        self.draft_generator_instance = DraftGeneratorInstance(database=self.database)
        self.qna_instance = QnAInstance(database=self.database)

    
    def get_keywords(self):
        keywords = self.keywords_generator_instance.run(purpose=self.purpose) # List[str]
        return keywords
    
    async def async_get_keywords(self):
        keywords = await self.keywords_generator_instance.arun(purpose=self.purpose)
        return keywords

    def get_draft():
        pass # purpose, keywords, database

    async def async_get_draft():
        pass # purpose, keywords, database

    def get_answer():
        pass

    async def async_get_answer():
        pass


if __name__ == "__main__":
    pass