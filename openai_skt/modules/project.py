import os

try:
    try:
        pass
    except:
        import configparser

        config = configparser.ConfigParser()
        config.read('../.secrets.ini')
        openai_api_key = config['OPENAI']['OPENAI_API_KEY']
        os.environ.update({'OPENAI_API_KEY': openai_api_key})
except:
    from django.conf import settings
    config = settings.KEY_INFORMATION
    openai_api_key = config['OPENAI']['OPENAI_API_KEY']
    os.environ.update({'OPENAI_API_KEY': openai_api_key})

import json
import pickle
import asyncio
from typing import List, Dict

from database.database import DataBase
from modules import Draft

# 변경사항
# 1. files(suggestions)가 api가 key -> keyword가 key로 변경
# 2. self.drafts -> self.draft 마지막 draft 객체에 담음
# 3. async_search_keywords이후 json 파일로 저장
# 4. project 저장이 pkl과 json 두가지로 저장
# 5. project load시 pkl로 불러옴.(Project)
# 6. qna 함수 추가
# 7. draft_id 추가, draft 생성시(get_draft)에 함께 넣어줌
# 8. embedchain대신 customembedchain 사용

class Project:
    save_root_path = f"./user"
    def __init__(self, 
                project_id,
                table_generator_instance,
                keywords_generator_instance,
                draft_generator_instance,
                qna_instance,
                search_tool,
                embed_chain) -> None:
        self.project_id = project_id
        self.draft_id = 'draft_0'
        self.purpose = None
        self.table = None
        self.keywords = None
        self.draft = None # draft
        self.qna_history = list()

        self.files = dict() # {'검색어1':{'통계청':[{'내용':, '경로':},{}]}}, 키워드로 검색한 파일들
        self.database = DataBase(files=[], embed_chain=embed_chain)
        self.user_root_path = os.path.join(self.save_root_path, f"{self.project_id}")
        os.makedirs(self.user_root_path, exist_ok=True)
        self.database_path = os.path.join(self.user_root_path, "database.pkl") # you can change the extension to .json
        self.user_instance_json_path = os.path.join(self.user_root_path, "user_instance.json")
        self.user_instance_pkl_path = os.path.join(self.user_root_path, "user_instance.pkl")
        self.suggestions_json_path = os.path.join(self.user_root_path, "suggestions.json")

        self.draft_root_path = os.path.join(self.user_root_path, f"drafts")
        self.draft_json_path = os.path.join(self.user_root_path, f"last_draft.json")
        self.draft_md_path = os.path.join(self.user_root_path, f"last_draft.md")

        self.table_generator_instance = table_generator_instance
        self.keywords_generator_instance = keywords_generator_instance
        self.draft_generator_instance = draft_generator_instance
        self.qna_instance = qna_instance
        
        self.search_tool = search_tool
    
    def set_purpose(self, purpose:str=None):
        if purpose is not None:
            self.purpose = purpose
        return self.purpose

    def set_keywords(self, keywords:List[str]=None):
        if keywords is not None:
            self.keywords = keywords
        return self.keywords

    def set_table(self, table:str=None):
        if table is not None:
            self.table = table
        return self.table
            
    def set_files(self, files:Dict[str, Dict[str, List[Dict[str, str]]]]=None):
        if files is not None:
            self.files = files
        return self.files
    
    def set_draft(self, draft_path:str=None):
        if draft_path is not None:
            self.draft = Draft.load(draft_path)
        return self.draft
    
    def add_files(self, files:List[tuple]):
        # [(path1, type1), (path2, type2), ...]
        # type: ['web_page', 'youtube_video', 'pdf_file', 'text']
        self.database.add_files(files)

    @classmethod
    def load_from_file(cls, 
                    table_generator_instance,
                    keywords_generator_instance,
                    draft_generator_instance,
                    qna_instance,
                    search_tool,
                    embed_chain,
                    user_instance_path
                    ):
        # Check that mandatory variables are not None
        if not table_generator_instance:
            raise ValueError("`table_generator_instance` must not be None.")
        if not keywords_generator_instance:
            raise ValueError("`keywords_generator_instance` must not be None.")
        if not draft_generator_instance:
            raise ValueError("`draft_generator_instance` must not be None.")
        if not qna_instance:
            raise ValueError("`qna_instance` must not be None.")
        if not search_tool:
            raise ValueError("`search_tool` must not be None.")
        if not embed_chain:
            raise ValueError("`embed_chain` must not be None.")
        if not user_instance_path:
            raise ValueError("`user_instance_path` must not be None.")

        file_extension = os.path.splitext(user_instance_path)[1]
        if os.path.exists(user_instance_path):
            if file_extension == '.json':
                with open(user_instance_path, "r", encoding='utf-8') as f:
                    user_instance = json.load(f)
                project_id = user_instance["project_id"]
                purpose = user_instance["purpose"]
                table = user_instance["table"]
                keywords = user_instance["keywords"]
                database_path = user_instance["database_path"]
                draft_path = user_instance["draft_path"]
                project = cls(project_id, table_generator_instance, keywords_generator_instance, draft_generator_instance, qna_instance, search_tool, embed_chain)
                project.set_purpose(purpose)
                project.set_table(table)
                project.set_keywords(keywords)
                # project.set_files(files)
                project.set_draft(draft_path)
                project.load_database(database_path, embed_chain)
                return project
            elif file_extension == '.pkl':
                with open(user_instance_path, "rb") as f:
                    project = pickle.load(f)
                project.table_generator_instance = table_generator_instance
                project.keywords_generator_instance = keywords_generator_instance
                project.draft_generator_instance = draft_generator_instance
                project.qna_instance = qna_instance
                project.search_tool = search_tool
                project.embed_chain = embed_chain
                return project
            else:
                raise ValueError(f"Invalid file extension: {file_extension}")
        else:
            raise ValueError(f"File does not exist: {user_instance_path}")
        
    def load_database(self, database_path, embed_chain):
        self.database = DataBase.load(database_path=database_path, embed_chain=embed_chain)
    
    @classmethod
    def load(cls, 
            table_generator_instance,
            keywords_generator_instance,
            draft_generator_instance,
            qna_instance,
            search_tool,
            embed_chain,
            project_id=None,
            purpose:str=None,
            table:str=None,
            files:Dict[str, List[Dict[str, str]]]=None,
            keywords:List[str]=None):
        # Check that mandatory variables are not None
        if not table_generator_instance:
            raise ValueError("`table_generator_instance` must not be None.")
        if not keywords_generator_instance:
            raise ValueError("`keywords_generator_instance` must not be None.")
        if not draft_generator_instance:
            raise ValueError("`draft_generator_instance` must not be None.")
        if not qna_instance:
            raise ValueError("`qna_instance` must not be None.")
        if not search_tool:
            raise ValueError("`search_tool` must not be None.")
        if not embed_chain:
            raise ValueError("`embed_chain` must not be None.")
        project = cls(project_id, table_generator_instance, keywords_generator_instance, draft_generator_instance, qna_instance, search_tool, embed_chain)
        project.set_purpose(purpose)
        project.set_table(table)
        project.set_keywords(keywords)
        project.set_files(files)
        project.load_database(project.database_path, embed_chain)
        return project

    def save(self):
        # save database
        if self.database is not None:
            self.database.save(self.database_path)

        # save drafts
        if self.draft is not None:
            self.draft.save(draft_root_path=self.draft_root_path)
            self.draft.save(draft_json_path=self.draft_json_path)
        else:
            self.draft_json_path = None

        # save user instance to json
        with open(self.user_instance_json_path, "w", encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
        print(f"saved user instance to {self.user_instance_json_path}")
        self.draft_json_path = os.path.join(self.user_root_path, f"last_draft.json")

        # save with pickle
        with open(self.user_instance_pkl_path, "wb") as f:
            pickle.dump(self, f)
        print(f"saved user instance to {self.user_instance_pkl_path}")

    def to_dict(self):
        return {
            "project_id": self.project_id,
            "purpose": self.purpose,
            "table": self.table,
            "keywords": self.keywords,
            "database_path": self.database_path,
            "draft_path": self.draft_json_path,
        }
    
    def __getstate__(self):
        state = self.__dict__.copy()
        # sqlite3.Connection 같은 객체가 있으면 여기서 제거
        state['embed_chain'] = None
        state['table_generator_instance'] = None
        state['keywords_generator_instance'] = None
        state['draft_generator_instance'] = None
        state['qna_instance'] = None
        state['search_tool'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __str__(self) -> str:
        return f"Project(project_id={self.project_id}, purpose={self.purpose}, keywords={self.keywords}, table={self.table})"
    
    def parse_files_to_embedchain(self):
        # {'api_name':[{},{}]]}
        files = []
        for keyword, files_of_keyword in self.files.items(): # keyword: IMF, files_of_keyword: {'kostat':[{'제목':'IMF', '내용':'IMF 내용'}]}
            for api_name, files_of_api in files_of_keyword.items(): # api_name: kostat, files_of_api: [{'제목':'IMF', '내용':'IMF 내용'}]
                for file in files_of_api:
                    data_path, data_type = file['data_path'], file['data_type']
                    files.append((data_path, data_type))

        self.database.multithread_add_files(files)
        return self.database

    async def async_parse_files_to_embedchain(self):
        # {'keyword': {'api_name':[{},{}]]}}
        async def handle_file(file):
            data_path, data_type = file['data_path'], file['data_type']
            await self.database.async_add(data_path, data_type)
            return (data_path, data_type)

        tasks = [handle_file(file) for files_of_keyword in self.files.values() for files_of_api in files_of_keyword.values() for file in files_of_api]
        files = await asyncio.gather(*tasks)

        return self.database
    
    def search_keywords(self):
        keywords_files = {}
        for keyword in self.keywords:
            api_files = {}
            result = self.search_tool.search(query=keyword)
            for api_name, infos in result.items():
                for info in infos:
                    if api_name not in api_files:
                        api_files[api_name] = []
                    api_files[api_name].append(info)
            keywords_files[keyword] = api_files

        # save suggestions
        with open(self.suggestions_json_path, "w", encoding='utf-8') as f:
            json.dump(keywords_files, f, ensure_ascii=False, indent=4)
        print(f"saved suggestions to {self.suggestions_json_path}")
        self.files = keywords_files
        return keywords_files
    
    async def async_search_keywords(self):
        tasks = [self.search_tool.async_search(query=keyword) for keyword in self.keywords]
        results = await asyncio.gather(*tasks)

        keywords_files = {}
        for keyword, result in zip(self.keywords, results):
            api_files = {}
            for api_name, infos in result.items():
                for info in infos:
                    if api_name not in api_files:
                        api_files[api_name] = []
                    api_files[api_name].append(info)
            keywords_files[keyword] = api_files

        # save suggestions
        with open(self.suggestions_json_path, "w", encoding='utf-8') as f:
            json.dump(keywords_files, f, ensure_ascii=False, indent=4)
        self.files = keywords_files
        return keywords_files

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
        draft = self.draft_generator_instance.run(purpose=self.purpose, table=self.table, database=self.database, draft_id=self.draft_id)
        self.draft = draft
        return draft

    async def async_get_draft(self):
        draft = await self.draft_generator_instance.arun(purpose=self.purpose, table=self.table, database=self.database, draft_id=self.draft_id)
        self.draft = draft
        return draft

    def get_qna_answer(self, question:str=None, qna_history:List[List[str]]=None, queue=None):
        answer = self.qna_instance.run(database=self.database, question=question, qna_history=qna_history, queue=queue)
        return answer

    async def async_get_qna_answer(self, question:str=None, qna_history:List[List[str]]=None, queue=None):
        answer = await self.qna_instance.run(database=self.database, question=question, qna_history=qna_history, queue=queue)
        return answer

    def edit_draft(self, draft_id:int, query:str):
        draft = self.drafts[draft_id]
        draft.edit(query)
        return self.drafts[draft_id]