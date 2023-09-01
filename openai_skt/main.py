import os
import configparser

config = configparser.ConfigParser()
config.read('../.secrets.ini')
openai_api_key = config['OPENAI']['OPENAI_API_KEY']
os.environ.update({'OPENAI_API_KEY': openai_api_key})

import json
import asyncio
from typing import List

from tools.search_tool import SearchTool
from models.llm.chain import KeywordsChain, DraftChain, TableChain
from models.draft_generator import DraftGeneratorInstance
from models.keywords_generator import KeywordsGeneratorInstance
from models.table_generator import TableGeneratorInstance
from modules import Project

verbose = True

table_chain = TableChain(verbose=verbose)
keywords_chain = KeywordsChain(verbose=verbose)
draft_chain = DraftChain(verbose=verbose)

table_generator_instance = TableGeneratorInstance(table_chain=table_chain)
keywords_generator_instance = KeywordsGeneratorInstance(keywords_chain=keywords_chain)
draft_generator_instance = DraftGeneratorInstance(draft_chain=draft_chain)

search_tool = SearchTool()

if __name__ == "__main__":
    user_instance = Project(
        user_id="test_1", 
        table_generator_instance=table_generator_instance, 
        keywords_generator_instance=keywords_generator_instance, 
        draft_generator_instance=draft_generator_instance, 
        search_tool=search_tool
    )
    purpose = user_instance.set_purpose(purpose="디지털 자산과 비트코인")
    print('purpose: ', purpose)
    table = user_instance.get_table()
    print('table: ', table)
    keywords = user_instance.get_keywords()
    print('keywords: ', keywords)
    files = user_instance.search_keywords()
    print('searched files: ', len(user_instance.files))
    database = user_instance.parse_files_to_embedchain()
    print('database: ', database)
    draft = user_instance.get_draft()
    print('draft: ', draft)
    user_instance.save_instance()