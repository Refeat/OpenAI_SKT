import os
import configparser

config = configparser.ConfigParser()
config.read('../.secrets.ini')
try:
    openai_api_key = config['OPENAI']['OPENAI_API_KEY']
    os.environ.update({'OPENAI_API_KEY': openai_api_key})
except:
    from django.conf import settings
    config = settings.KEY_INFORMATION
    openai_api_key = config['OPENAI']['OPENAI_API_KEY']
    os.environ.update({'OPENAI_API_KEY': openai_api_key})

import json
import asyncio
from typing import List

from database.database import DataBase
from utils import time_logger, async_time_logger

class Project:
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
        self.drafts = list() # [draft1, draft2, ...]

        self.user_instance_path = None
        self.files = dict() # {'keyword': {'api_name':[{},{}]]}}, AI가 검색한 파일들
        self.database = DataBase(files=[])
        self.database_path = None

        self.table_generator_instance = table_generator_instance
        self.keywords_generator_instance = keywords_generator_instance
        self.draft_generator_instance = draft_generator_instance
        # self.async_get_answer = None
        self.search_tool = search_tool
    
    def set_purpose(self, purpose:str=None):
        if purpose is not None:
            self.purpose = purpose
            return purpose
        else:
            raise ValueError("purpose must be specified")

    def set_table(self, table:str):
        # TODO: 유저가 목차를 변경할 수 있도록
        self.table = table
        return table
    
    def add_files(self, files:List[tuple]):
        # [(path1, type1), (path2, type2), ...]
        # type: ['web_page', 'youtube_video', 'pdf_file', 'text']
        self.database.add_files(files)

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

    @time_logger
    def save_instance(self):
        user_root_path = os.path.join(self.save_root_path, f"{self.user_id}")
        os.makedirs(user_root_path, exist_ok=True)
        self.database_path = os.path.join(user_root_path, "database.json")

        # save user instance
        self.user_instance_path = os.path.join(user_root_path, "user_instance.json")
        with open(self.user_instance_path, "w", encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
        print(f"saved user instance to {self.user_instance_path}")

        # save drafts
        for i, draft in enumerate(self.drafts):
            draft_path = os.path.join(user_root_path, f"draft_{i}.md")
            with open(draft_path, "w", encoding='utf-8') as f:
                f.write(draft.text)
            print(f"saved draft to {draft_path}")

        # save database
        self.database.save(self.database_path)
        print(f"saved database to {self.database_path}")

    def to_dict(self):
        return {
            "purpose": self.purpose,
            "keywords": self.keywords,
            "database_path": self.database_path,
            "draft": [draft.to_dict() for draft in self.drafts]
        }
    
    @time_logger
    def parse_files_to_embedchain(self):
        # {'keyword': {'api_name':[{},{}]]}}
        files = []
        for keyword, files_of_keyword  in self.files.items(): # keyword: 국민연금, files_of_keyword: {'kostat':[], 'gallup':[]}
            for api_name, files_of_api in files_of_keyword.items(): # api_name: kostat, files_of_api: [{'제목':'IMF', '내용':'IMF 내용'}]
                for file in files_of_api:
                    data_path, data_type = file['data_path'], file['data_type']
                    files.append((data_path, data_type))
                    # self.database.add(data_path, data_type)

        self.database.multithread_add_files(files)
        return self.database

    @async_time_logger
    async def async_parse_files_to_embedchain(self):
        # {'keyword': {'api_name':[{},{}]]}}
        async def handle_file(file):
            data_path, data_type = file['data_path'], file['data_type']
            await self.database.async_add(data_path, data_type)
            return (data_path, data_type)

        tasks = [handle_file(file) for files_of_keyword in self.files.values() for files_of_api in files_of_keyword.values() for file in files_of_api]
        files = await asyncio.gather(*tasks)

        return self.database
    
    @time_logger
    def search_keywords(self):
        for keyword in self.keywords:
            file = self.search_tool.search(query=keyword)
            self.files[keyword] = file
        return self.files
    
    @async_time_logger
    async def async_search_keywords(self):
        tasks = [self.search_tool.async_search(query=keyword) for keyword in self.keywords]
        results = await asyncio.gather(*tasks)

        for keyword, result in zip(self.keywords, results):
            self.files[keyword] = result

        return self.files

    @time_logger
    def get_table(self):
        table = self.table_generator_instance.run(purpose=self.purpose)
        self.table = table
        return table
    
    @async_time_logger
    async def async_get_table(self):
        table = await self.table_generator_instance.arun(purpose=self.purpose)
        self.table = table
        return table
    
    @time_logger
    def get_keywords(self) -> List[str]:
        keywords = self.keywords_generator_instance.run(purpose=self.purpose, table=self.table)
        self.keywords = keywords
        return keywords
    
    @async_time_logger
    async def async_get_keywords(self) -> List[str]:
        keywords = await self.keywords_generator_instance.arun(purpose=self.purpose, table=self.table)
        self.keywords = keywords
        return keywords

    @time_logger
    def get_draft(self):
        draft = self.draft_generator_instance.run(purpose=self.purpose, table=self.table, database=self.database)
        self.drafts.append(draft)
        return draft

    @async_time_logger
    async def async_get_draft(self):
        draft = await self.draft_generator_instance.arun(purpose=self.purpose, table=self.table, database=self.database)
        self.drafts.append(draft)
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