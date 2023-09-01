import os
import configparser

config = configparser.ConfigParser()
config.read('../.secrets.ini')
openai_api_key = config['OPENAI']['OPENAI_API_KEY']
os.environ.update({'OPENAI_API_KEY': openai_api_key})

import json
import asyncio
from typing import List

from database.database import DataBase
from tools.search_tool import SearchTool
from models.llm.chain import KeywordsChain, DraftChain, TableChain
from models.draft_generator import DraftGeneratorInstance
from models.keywords_generator import KeywordsGeneratorInstance
from models.table_generator import TableGeneratorInstance

verbose = True

table_chain = TableChain(verbose=verbose)
keywords_chain = KeywordsChain(verbose=verbose)
draft_chain = DraftChain(verbose=verbose)

table_generator_instance = TableGeneratorInstance(table_chain=table_chain)
keywords_generator_instance = KeywordsGeneratorInstance(keywords_chain=keywords_chain)
draft_generator_instance = DraftGeneratorInstance(draft_chain=draft_chain)

search_tool = SearchTool()