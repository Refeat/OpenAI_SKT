from embedchain.embedchain import EmbedChain
from embedchain.config import AppConfig
import asyncio
from typing import List
from database.data import Data

embed_chain = EmbedChain(config=AppConfig())

class DataBase:
    # db = DataBase([(path1, type1), (path2, type2), ...]) 으로 선언
    # db[x][y] <- db의 x번째 data, 그 데이터의 y번째 chunk 반환
    def __init__(self, files:List[tuple]):
        self.embed_chain = embed_chain
        self.data = []
        asyncio.run(self.add_files(files))
        self.token_num = 0
        for data in self.data:
            self.token_num += data.token_num
        self.cost = self.token_num * 0.0001 * 0.0002

    def __str__(self) -> str:
        ret = 'DataBase{\n'
        for i, data in enumerate(self.data):
            ret += '\t[' + str(i) + '] ' + str(data) + '\n'
        ret += '}\ntotal tokens : ' + str(self.token_num) + '\ncost : ' + str(self.cost)
        return ret

    def __getitem__(self, idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)

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