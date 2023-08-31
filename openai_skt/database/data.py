from embedchain.embedchain import EmbedChain
from typing import List, Dict

class Data:
    def __init__(self, hash_id:str, parsed_data:Dict) -> None:
        self.hash = hash_id
        self.data_path = None
        self.data_type = None
        ids = parsed_data['ids']
        self.embeddings = parsed_data['embeddings']
        documents = parsed_data['documents']

        self.chunk_list = []
        for i, id_db in enumerate(ids):
            self.chunk_list.append(Chunk(id_db, documents[i], self.embeddings[i]))
        
        if ids:
            self.data_path = parsed_data['metadatas'][0]['url']
            self.data_type = parsed_data['metadatas'][0]['data_type']
    
    def __str__(self) -> str:
        return str(self.data_type) + ' / ' + str(self.data_path) + ' hash : [' + self.hash + ']'
    
    def __repr__(self) -> str:
        return str(self)

class Chunk:
    def __init__(self, id_db:str = None, data:str = None, embedding:List[float] = None) -> None:
        self.id = id_db
        self.data = data
        self.embedding = embedding