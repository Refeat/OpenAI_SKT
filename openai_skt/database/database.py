import asyncio
import nest_asyncio
from typing import List

from embedchain.embedchain import EmbedChain
from embedchain.config import AppConfig

from database.data import Data

class DataBase:
    def __init__(self, files:List[tuple]):
        self.embed_chain = EmbedChain(config=AppConfig())
        self.data = []

        try:
            get_ipython
            is_jupyter = True
        except NameError:
            is_jupyter = False

        if is_jupyter:
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.async_add_files(files))
        else:
            asyncio.run(self.async_add_files(files))


    def __str__(self) -> str:
        ret = 'DataBase{\n'
        for i, data in enumerate(self.data):
            ret += '[' + str(i) + '] ' + str(data) + '\n'
        ret += '}'
        return ret

    def __repr__(self) -> str:
        return str(self)
    
    def add(self, filepath: str, data_type: str):
        hash_id = self.embed_chain.add(filepath, data_type)
        db_ids = list(self.embed_chain.db.get([], {'hash': hash_id}))
        parsed_data = self.embed_chain.db.collection.get(ids=db_ids, include=["documents", "metadatas", "embeddings"])
        self.data.append(Data(hash_id, parsed_data))

    def add_files(self, files: List[tuple]):
        for file in files:
            file_path, data_type = file
            self.add(file_path, data_type)
    
    async def async_add_files(self, files: List[tuple]):
        data_add_tasks = [self.async_add(file_path, data_type) for (file_path, data_type) in files]
        await asyncio.gather(*data_add_tasks)
    
    async def async_add(self, filepath: str, data_type: str):
        self.add(filepath, data_type)