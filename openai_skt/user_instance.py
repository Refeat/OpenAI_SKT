import os
import json
import asyncio
from typing import List

from database.database import DataBase
from tools.search_tool import SearchTool
from models.llm.chain import KeywordsChain, DraftChain, TableChain
from models.draft_generator import DraftGeneratorInstance
from models.keywords_generator import KeywordsGeneratorInstance
from models.table_generator import TableGeneratorInstance


table_chain = TableChain()
keywords_chain = KeywordsChain()
draft_chain = DraftChain()

table_generator_instance = TableGeneratorInstance(table_chain=table_chain)
keywords_generator_instance = KeywordsGeneratorInstance(chain=keywords_chain)
draft_generator_instance = DraftGeneratorInstance(draft_chain=draft_chain)

search_tool = SearchTool()

class UserInstance:
    save_root_path = f"./user"
    def __init__(self, 
                user_id, 
                table_generator_instance, 
                keywords_generator_instance, 
                draft_generator_instance, 
                search_tool) -> None:
        self.user_id = user_id
        self.purpose = None
        self.table = None
        self.keywords = None
        self.draft = None

        self.user_instance_path = None
        self.files = list()
        self.database = None
        self.database_path = None

        self.table_generator_instance = table_generator_instance
        self.keywords_generator_instance = keywords_generator_instance
        self.draft_generator_instance = draft_generator_instance
        # self.async_get_answer = None
        self.search_tool = search_tool
    
    def set_purpose(self, purpose:str=None):
        if purpose is not None:
            self.purpose = purpose
        else:
            raise ValueError("purpose must be specified")

    def init_instance(self, purpose=None, keywords=None, files:List[tuple]=None):
        assert purpose is not None
        self.purpose = purpose
        self.keywords = keywords
        self.database = DataBase(files=files)

    def load_instance(self, user_instance_path:str=None):
        assert user_instance_path is not None
        with open(user_instance_path, "r") as f:
            user_instance = json.load(f)
        self.purpose = user_instance["purpose"]
        self.keywords = user_instance["keywords"]
        self.database_path = user_instance["database_path"]
        self.database = DataBase(database_path=self.database_path)

    def save_instance(self):
        user_root_path = os.path.join(self.save_root_path, f"{self.user_id}")
        os.makedirs(user_root_path, exist_ok=True)

        # save user instance
        self.user_instance_path = os.path.join(user_root_path, "user_instance.json")
        with open(self.user_instance_path, "w") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)

        # save database
        user_database_path = os.path.join(user_root_path, "db")
        os.makedirs(user_database_path, exist_ok=True)
        self.database_path = os.path.join(user_root_path, "database.json")
        self.database.save(self.database_path)

    def to_dict(self):
        return {
            "purpose": self.purpose,
            "keywords": self.keywords,
            "database_path": self.database_path
        }
    
    def parse_files_to_embedchain(self):
        files = []
        for file in self.files.values():
            data_path, data_type = file['data_path'], file['data_type']
            files.append((data_path, data_type))
            self.database.add(data_path, data_type)
        return self.database
    
    def search_keywords(self):
        for keyword in self.keywords:
            file = self.search_tool.search(query=keyword)
            self.files.append(file)
        return self.files
    
    async def async_search_keywords(self):
        tasks = [self.search_tool.async_search(query=keyword) for keyword in self.keywords]
        self.files = await asyncio.gather(*tasks)
        return self.files

    def get_table(self):
        table = self.table_generator_instance.run(purpose=self.purpose)
        self.table = table
        return table
    
    async def async_get_table(self):
        table = await self.table_generator_instance.arun(purpose=self.purpose)
        self.table = table
        return table
    
    def get_keywords(self) -> List[str]:
        keywords = self.keywords_generator_instance.run(purpose=self.purpose, table=self.table)
        self.keywords = keywords
        return keywords
    
    async def async_get_keywords(self) -> List[str]:
        keywords = await self.keywords_generator_instance.arun(purpose=self.purpose, table=self.table)
        self.keywords = keywords
        return keywords

    def get_draft(self):
        draft = self.draft_generator_instance.run(purpose=self.purpose, keywords=self.keywords, database=self.database)
        self.draft = draft
        return draft

    async def async_get_draft(self):
        draft = await self.draft_generator_instance.arun(purpose=self.purpose, keywords=self.keywords, database=self.database)
        self.draft = draft
        return draft

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
    user_instance = UserInstance(
        user_id="test", 
        table_generator_instance=table_generator_instance, 
        keywords_generator_instance=keywords_generator_instance, 
        draft_generator_instance=draft_generator_instance, 
        search_tool=search_tool
    )
    user_instance.set_purpose(purpose="전세계적으로 축구가 유명한 스포츠인 이유")
    user_instance.get_table()
    user_instance.get_keywords()
    user_instance.search_keywords()
    user_instance.parse_files_to_embedchain()
    user_instance.get_draft()
    user_instance.save_instance()