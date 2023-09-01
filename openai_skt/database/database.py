import json
import asyncio
import nest_asyncio
from typing import List

from embedchain.embedchain import EmbedChain
from embedchain.config import AppConfig

from database.data import Data

# YoutubeLoader at langchain transcription language fix
from langchain.docstore.document import Document
from langchain.document_loaders import YoutubeLoader

def load_language_fix(self) -> List[Document]:
        """Load documents."""
        try:
            from youtube_transcript_api import (
                NoTranscriptFound,
                TranscriptsDisabled,
                YouTubeTranscriptApi,
            )
        except ImportError:
            raise ImportError(
                "Could not import youtube_transcript_api python package. "
                "Please install it with `pip install youtube-transcript-api`."
            )

        metadata = {"source": self.video_id}

        if self.add_video_info:
            # Get more video meta info
            # Such as title, description, thumbnail url, publish_date
            video_info = self._get_video_info()
            metadata.update(video_info)

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
        except TranscriptsDisabled:
            return []

        # detected_language = "en"  # Default to English if language detection fails

        try:
            # Detect the language of the transcript
            for transcript in transcript_list:
                # detected_language = transcript.language_code
                transcript_pieces = transcript.fetch()
                break
        except Exception as e:
            print(f"Language detection failed: {str(e)}")

        transcript = " ".join([t["text"].strip(" ") for t in transcript_pieces])

        return [Document(page_content=transcript, metadata=metadata)]

YoutubeLoader.load = load_language_fix

embed_chain = EmbedChain(config=AppConfig())

class DataBase:
    # db = DataBase([(path1, type1), (path2, type2), ...]) 으로 선언
    # db[x][y] <- db의 x번째 data, 그 데이터의 y번째 chunk 반환
    def __init__(self, files:List[tuple]):
        self.embed_chain = EmbedChain(config=AppConfig())
        self.data = {}
        self.chunks = {}
        self.where = None

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
        self.token_num = 0
        for data in self.data.values():
            self.token_num += data.token_num
        self.cost = self.token_num * 0.0001 * 0.0002
        self.update_where()
    
    def add(self, filepath: str, data_type: str):
        try:
            hash_id = self.embed_chain.add(filepath, data_type)
        except:
            print(filepath, 'has no data')
            return
        db_ids = list(self.embed_chain.db.get([], {'hash': hash_id}))
        parsed_data = self.embed_chain.db.collection.get(ids=db_ids, include=["documents", "metadatas", "embeddings"])
        self.data[hash_id] = Data(hash_id, parsed_data, self.chunks)
        

    def add_files(self, files: List[tuple]):
        for file in files:
            file_path, data_type = file
            self.add(file_path, data_type)

    async def async_add(self, filepath: str, data_type: str):
        self.add(filepath, data_type)
    
    async def async_add_files(self, files: List[tuple]):
        data_add_tasks = [self.async_add(file_path, data_type) for (file_path, data_type) in files]
        await asyncio.gather(*data_add_tasks)

    def query(self, query, top_k:int = 5):
        # input list of query ex) ['hi', 'hello']
        # output list of list of chunks zz ex) [[chunk1forquery1, chunk2forquery1, ..], [chunk1forquery2, chunk2forquery2, ...]]
        if isinstance(query, str):
            query = [query]
        elif isinstance(query, list):
            pass
        else:
            raise TypeError('query should be str or list of str')
        result_id_list = self.embed_chain.db.collection.query(query_texts = query, n_results=top_k, where=self.where)['ids']
        return [self.ids_2_chunk(ids) for ids in result_id_list]

    def ids_2_chunk(self, ids:List[str]):
        # input list of id [hash1, hash2, ...] (this should be hash of 'chunk')
        # output list of data [chunk1, chunk2, ...]
        return [self.chunks[cur_id] for cur_id in ids]

    def update_where(self):
        if len(self.data.keys()) == 1:
            self.where = {'hash': self[0].hash}
        else:
            self.where = {
                "$or": [{'hash': hash_id} for hash_id in self.data.keys()]
            }
    
    def save(self, database_path:str):
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)

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
