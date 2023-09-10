import sys
sys.path.append('..')

import os
os.environ["OPENAI_API_KEY"] = "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"

from database import DataBase,  CustomEmbedChain
embed_chain = CustomEmbedChain()

from embedchain.config import (AppConfig, BaseEmbedderConfig, BaseLlmConfig,
                               ChromaDbConfig)
from embedchain.embedchain import EmbedChain
from embedchain.embedder.openai_embedder import OpenAiEmbedder
from embedchain.helper_classes.json_serializable import register_deserializable
from embedchain.llm.openai_llm import OpenAiLlm
from embedchain.vectordb.chroma_db import ChromaDB

import time

# start = time.time()
# database = DataBase.load(database_path='./user/test_2/database.json', embed_chain=embed_chain) # optimize: 5m22s # 4m18s 3m4s 3m2s -> 60s
# database.save_by_pkl('database_save_path.pkl')
# print(time.time() - start)

import pickle


# with open("database_save_path.pkl", "wb") as f:
#     pickle.dump(database, f)
# print('save', time.time() - start)

start = time.time()
database = DataBase(files=[('https://stackoverflow.com/posts/57132803/revisions', 'web_page')], embed_chain=embed_chain)
DataBase.load_by_pkl('database_save_path.pkl', embed_chain=embed_chain)
print(time.time() - start)
