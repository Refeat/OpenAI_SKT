from embedchain.embedchain import EmbedChain
from typing import List, Dict
import tiktoken

class Data:
    def __init__(self, hash_id:str, parsed_data:Dict, chunks_dict:Dict) -> None:
        self.hash = hash_id
        self.data_path = None
        self.data_type = None
        ids = parsed_data['ids']
        self.embeddings = parsed_data['embeddings']
        documents = parsed_data['documents']
        metadatas = parsed_data['metadatas']
        self.token_num = 0

        self.chunks = {}
        for i, id_db in enumerate(ids):
            self.chunks[id_db] = Chunk(metadatas[i]['url'], metadatas[i]['data_type'], id_db, documents[i], self.embeddings[i])
            chunks_dict[id_db] = self.chunks[id_db]
            self.token_num += self.chunks[id_db].token_num
        
        if ids:
            self.data_path = metadatas[0]['url']
            self.data_type = parsed_data['metadatas'][0]['data_type']
    
    def __getitem__(self, idx):
        if type(idx) is str:
            return self.chunks[idx]
        elif type(idx) is int:
            return self.chunks.values()[idx]

    def __len__(self):
        return len(self.chunks)
    
    def __str__(self) -> str:
        return str(self.data_type) + ' | ' + str(self.data_path) + ' | Tokens : ' + str(self.token_num) + ' | hash : [' + self.hash + ']'
    
    def __repr__(self) -> str:
        return str(self)
    
    def to_dict(self):
        return {
            'hash': self.hash,
            'data_path': self.data_path,
            'data_type': self.data_type,
            'token_num': self.token_num,
            'chunks': [chunk.to_dict() for chunk in self.chunks.values()],
        }

class Chunk:
    def __init__(self, data_path:str = None, data_type:str = None, id_db:str = None, data:str = None, embedding:List[float] = None) -> None:
        self.id = id_db
        self.data = data
        self.embedding = embedding
        self.data_path = data_path
        self.data_type = data_type
        tokenizer = tiktoken.get_encoding("cl100k_base")
        self.token_num = len(tokenizer.encode(self.data))
    
    def __str__(self) -> str:
        return str(self.data_type) + ' | ' + str(self.data_path) + ' | Tokens : ' + str(self.token_num) + ' | Doc : ' + self.data + '\n'
    
    def __repr__(self) -> str:
        return str(self.data_type) + ' | ' + str(self.data_path) + ' | Tokens : ' + str(self.token_num) + ' | Hash : ' + self.id + '\n'
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data,
            'data_path': self.data_path,
            'data_type': self.data_type,
            'token_num': self.token_num
        }
