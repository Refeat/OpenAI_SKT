import os
import configparser

config = configparser.ConfigParser()
config.read('../.secrets.ini')
openai_api_key = config['OPENAI']['OPENAI_API_KEY']
os.environ.update({'OPENAI_API_KEY': openai_api_key})

import json
import time
import asyncio
import logging
from typing import List

from tools.search_tool import SearchTool
from models.llm.chain import KeywordsChain, DraftChain, TableChain
from models.draft_generator import DraftGeneratorInstance
from models.keywords_generator import KeywordsGeneratorInstance
from models.table_generator import TableGeneratorInstance
from modules import Project

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

verbose = False

table_chain = TableChain(verbose=verbose)
keywords_chain = KeywordsChain(verbose=verbose)
draft_chain = DraftChain(verbose=verbose)

table_generator_instance = TableGeneratorInstance(table_chain=table_chain)
keywords_generator_instance = KeywordsGeneratorInstance(keywords_chain=keywords_chain)
draft_generator_instance = DraftGeneratorInstance(draft_chain=draft_chain)

search_tool = SearchTool()

async def main():
    project = Project(
        user_id="test_2", 
        table_generator_instance=table_generator_instance, 
        keywords_generator_instance=keywords_generator_instance, 
        draft_generator_instance=draft_generator_instance, 
        search_tool=search_tool
    )
    start = time.time()
    purpose = project.set_purpose(purpose="네이버 클로바 X는 성공할 수 있을까?")
    print('purpose: ', purpose, time.time()-start)
    table = project.get_table()
    print('table: ', table, time.time()-start) # 10
    keywords = project.get_keywords()
    print('keywords: ', keywords, time.time()-start) # 13
    files = await project.async_search_keywords()
    print('searched files: ', len(project.files), time.time()-start) # 81.67
    # database = project.parse_files_to_embedchain()
    # print('database: ', database, time.time()-start) # 576
    database = await project.async_parse_files_to_embedchain()
    print('database: ', database, time.time()-start) # 1219
    draft = project.get_draft()
    print('draft: ', draft, time.time()-start) # 1326
    project.save_instance()
    print('saved instance: ', time.time()-start)

if __name__ == "__main__":
    asyncio.run(main())

