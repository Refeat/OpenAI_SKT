from embedchain.embedchain import EmbedChain
from embedchain.config import AppConfig
import asyncio
from typing import List
from database.data import Data

class DataBase:
    def __init__(self, files:List[tuple]):
        self.embed_chain = EmbedChain(config=AppConfig())
        self.data = []
        asyncio.run(self.add_files(files))

    # init 방식이 통합됨에 따라 굳이 classmethod 사용할 이유가 없음
    # @classmethod
    # def init_database(cls, files:List[tuple]):
    #     # files : list of tuple [(file_path, data_type), (file_path, data_type), ...]
    #     # 각 chunk마다 이전에 한 번 embedding을 만든 적 있는 데이터라면 자동으로 db에서 로딩해옴
    #     database =  cls()
    #     database.embed_chain = EmbedChain(config=AppConfig())
    #     database.data = []
    #     asyncio.run(database.add_files(files))
        
    #     return database

    # init_database가 자동으로 save, load를 하므로 불필요할듯
    # @classmethod
    # def load_database(cls, database_path:str):
    #     # asyncio.run(init_database(files))) 로 실행해야함!
    #     database = cls()
    #     database.embed_chain = EmbedChain(config=AppConfig())
    #     # TODO:file 로드
    #     return database

    def __str__(self) -> str:
        ret = 'DataBase{\n'
        for i, data in enumerate(self.data):
            ret += '[' + str(i) + '] ' + str(data) + '\n'
        ret += '}'
        return ret

    def __repr__(self) -> str:
        return str(self)
    
    async def add_files(self, files: List[tuple]):
        data_add_tasks = [self.add(file_path, data_type) for (file_path, data_type) in files]
        await asyncio.gather(*data_add_tasks)
    
    async def add(self, filepath: str, data_type: str):
        hash_id = self.embed_chain.add(filepath, data_type)
        db_ids = list(self.embed_chain.db.get([], {'hash': hash_id}))
        parsed_data = self.embed_chain.db.collection.get(ids=db_ids, include=["documents", "metadatas", "embeddings"])
        self.data.append(Data(hash_id, parsed_data))