import os
import configparser

config = configparser.ConfigParser()
config.read('../.secrets.ini')
OPENAI_API_KEY = config['OPENAI']['OPENAI_API_KEY']
YOUTUBE_KEY = config['YOUTUBE']['YOUTUBE_API_KEY']
NAVER_CLIENT_ID = config['NAVER']['NAVER_CLIENT_ID']
NAVER_CLIENT_SECRET = config['NAVER']['NAVER_CLIENT_SECRET']
GOOGLE_SEARCH_KEY = config['GOOGLE']['GOOGLE_API_KEY']
CSE_ID = config['GOOGLE']['CSE_ID']

os.environ.update({'OPENAI_API_KEY': OPENAI_API_KEY})
os.environ.update({'YOUTUBE_KEY': YOUTUBE_KEY})
os.environ.update({'NAVER_CLIENT_ID': NAVER_CLIENT_ID})
os.environ.update({'NAVER_CLIENT_SECRET': NAVER_CLIENT_SECRET})
os.environ.update({'GOOGLE_SEARCH_KEY': GOOGLE_SEARCH_KEY})
os.environ.update({'CSE_ID': CSE_ID})

import time
import asyncio
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
        project_id="test_6", 
        table_generator_instance=table_generator_instance, 
        keywords_generator_instance=keywords_generator_instance, 
        draft_generator_instance=draft_generator_instance, 
        search_tool=search_tool
    )
    start = time.time()
    purpose = project.set_purpose(purpose="2023년 우크라이나 러시아 전쟁에 관한 보고서")
    print('purpose: ', purpose, time.time()-start)
    table = project.get_table()
    print('table: ', table, time.time()-start) # 10
    # project.set_table(table="1.서론...") # 유저가 목차 변경
    keywords = project.get_keywords()
    print('keywords: ', keywords, time.time()-start) # 13
    files = await project.async_search_keywords()
    print('searched files: ', len(project.files), time.time()-start) # 81.67
    user_files = [('https://en.wikipedia.org/wiki/Elon_Musk', 'web_page'), ('hello', 'text'), ('https://www.youtube.com/watch?v=Z4fBZGbk5iQ', 'youtube_video'), ('hello.docx', 'docx')]
    project.add_files(files=user_files) # 유저가 직접 파일 추가
    database = project.parse_files_to_embedchain()
    print('database: ', database, time.time()-start) # 576
    draft = project.get_draft()
    print('draft: ', draft, time.time()-start) # 1326
    project.save_instance()
    print('saved instance: ', time.time()-start)

if __name__ == "__main__":
    asyncio.run(main())

