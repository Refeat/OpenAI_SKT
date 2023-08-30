from embedchain.embedchain import EmbedChain
from typing import List, Dict
import tiktoken

class Data:
    def __init__(self, hash_id:str, parsed_data:Dict) -> None:
        self.hash = hash_id
        self.data_path = None
        self.data_type = None
        ids = parsed_data['ids']
        self.embeddings = parsed_data['embeddings']
        documents = parsed_data['documents']
        metadatas = parsed_data['metadatas']
        self.token_num = 0

        self.chunk_list = []
        for i, id_db in enumerate(ids):
            self.chunk_list.append(Chunk(metadatas[i]['url'], metadatas[i]['data_type'], id_db, documents[i], self.embeddings[i]))
            self.token_num += self.chunk_list[i].token_num
        
        if ids:
            self.data_path = metadatas[0]['url']
            self.data_type = parsed_data['metadatas'][0]['data_type']
    
    def __getitem__(self, idx):
        return self.chunk_list[idx]

    def __len__(self):
        return len(self.chunk_list)
    
    def __str__(self) -> str:
        return str(self.data_type) + ' | ' + str(self.data_path) + ' | Tokens : ' + str(self.token_num) + ' | hash : [' + self.hash + ']'
    
    def __repr__(self) -> str:
        return str(self)

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
        return str(self.data_type) + ' | ' + str(self.data_path) + ' | Tokens : ' + str(self.token_num) + ' | Doc : ' + self.data
    
    def __repr__(self) -> str:
        return str(self)
