import os
import json
import asyncio
import pickle
from typing import List

from embedchain.embedchain import EmbedChain
from embedchain.config import AppConfig

from database.data import Data
import database.loader
import threading

class DataBase:
    # db = DataBase([(path1, type1), (path2, type2), ...]) 으로 선언
    # db[x][y] <- db의 x번째 data, 그 데이터의 y번째 chunk 반환
    thread_num = 2
    semaphore = threading.Semaphore(thread_num)
    def __init__(self, files:List[tuple], embed_chain:EmbedChain):
        self.set_embed_chain(embed_chain)
        self.data = {}
        self.chunks = {}
        self.where = None

        self.multithread_add_files(files)
        # self.add_files(files)
        self.update_token_num()
        self.update_where()
    
    @classmethod
    def load(cls, database_path, embed_chain:EmbedChain):
        file_extension = os.path.splitext(database_path)[1]
        
        if os.path.exists(database_path):
            if file_extension == '.json':
                with open(database_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()  # 파일의 내용을 문자열로 읽어옴
                    data = json.loads(file_content)

                files = []
                for item in data['data']:
                    if item['data_type'] == 'web_page':
                        files.append((item['data_path'], item['data_type']))

                # data_path와 data_type을 결합하여 files 리스트 생성
                return cls(files=files, embed_chain=embed_chain)
            elif file_extension == '.pkl':
                with open(database_path, 'rb') as f:
                    database = pickle.load(f)
                database.set_embed_chain(embed_chain)
                return database
        else:
            return cls(files=[], embed_chain=embed_chain)

    def __getstate__(self):
        state = self.__dict__.copy()
        # sqlite3.Connection 같은 객체가 있으면 여기서 제거
        state['embed_chain'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def set_embed_chain(self, embed_chain:EmbedChain):
        self.embed_chain = embed_chain

    def add(self, filepath: str, data_type: str):
        try:
            hash_id = self.embed_chain.add(filepath, data_type)
            db_ids = list(self.embed_chain.db.get([], {'hash': hash_id}))
            parsed_data = self.embed_chain.db.collection.get(ids=db_ids, include=["documents", "metadatas"])
            self.data[hash_id] = Data(hash_id, parsed_data, self.chunks)
            self.update_where()
            self.update_token_num()
        except:
            print(filepath, 'has no data')
            return
        finally:
            self.semaphore.release()

    def update_token_num(self):
        self.token_num = 0
        for data in self.data.values():
            self.token_num += data.token_num
        self.cost = self.token_num * 0.0001 * 0.0002

    def add_files(self, files: List[tuple]):
        for file in files:
            file_path, data_type = file
            self.add(file_path, data_type)

    async def async_add(self, filepath: str, data_type: str):
        self.add(filepath, data_type)
    
    async def async_add_files(self, files: List[tuple]):
        data_add_tasks = [self.async_add(file_path, data_type) for (file_path, data_type) in files]
        await asyncio.gather(*data_add_tasks)
    
    def multithread_add_files(self, files: List[tuple]):
        data_add_threads = []
        
        for file_path, data_type in files:
            # Acquire a semaphore before starting a new thread
            self.semaphore.acquire()
            
            thread = threading.Thread(target=self.add, args=[file_path, data_type])
            data_add_threads.append(thread)
            thread.start()

        for thread in data_add_threads:
            thread.join()

    def query(self, query, top_k:int = 5):
        # input list of query ex) ['hi', 'hello']
        # output list of list of chunks zz ex) [[chunk1forquery1, chunk2forquery1, ..], [chunk1forquery2, chunk2forquery2, ...]]
        if isinstance(query, str):
            query_texts = [query]
        elif isinstance(query, list):
            query_texts = query
        else:
            raise TypeError('query should be str or list of str')
        result_id_list = self.embed_chain.db.collection.query(query_texts = query_texts, n_results=top_k, where=self.where)['ids']
        results = [self.ids_2_chunk(ids) for ids in result_id_list]
        if isinstance(query, str):
            return results[0]
        elif isinstance(query, list):
            return results

    def ids_2_chunk(self, ids:List[str]):
        # input list of id [hash1, hash2, ...] (this should be hash of 'chunk')
        # output list of data [chunk1, chunk2, ...]
        return [self.chunks[cur_id] for cur_id in ids]

    def update_where(self):
        if len(self.data.keys()) == 0:
            self.where = {}
        elif len(self.data.keys()) == 1:
            self.where = {'hash': self[0].hash}
        else:
            self.where = {
                "$or": [{'hash': hash_id} for hash_id in self.data.keys()]
            }

    def save(self, database_path):
        # Get file extension
        file_extension = os.path.splitext(database_path)[1]
        
        # Check the file extension and save accordingly
        if file_extension == '.json':
            with open(database_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)
        elif file_extension == '.pkl':
            with open(database_path, 'wb') as f:
                pickle.dump(self, f)
        else:
            print(f"Unsupported file extension {file_extension}. Use .json or .pkl.")

    def to_dict(self):
        return {
            'data': [data.to_dict() for data in self.data.values()],
        }            
    
    def __str__(self) -> str:
        ret = 'DataBase{\n'
        for i, data in enumerate(self.data.values()):
            ret += '\t[' + str(i) + '] ' + str(data) + '\n'
        ret += '}\ntotal tokens : ' + str(self.token_num) + '\ncost : ' + str(self.cost)
        return ret

    def __getitem__(self, idx):
        if type(idx) is str:
            return self.data[idx]
        elif type(idx) is int:
            return list(self.data.values())[idx]

    def __len__(self):
        return len(self.data)

    def __repr__(self) -> str:
        return str(self)
