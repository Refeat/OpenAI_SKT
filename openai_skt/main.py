import os
import configparser

from utils import load_api_key

load_api_key()


import time
import asyncio
from typing import List

from database import CustomEmbedChain
from tools import SearchTool, SearchByURLTool
from models.draft_generator import DraftGeneratorInstance
from models.keywords_generator import KeywordsGeneratorInstance
from models.table_generator import TableGeneratorInstance
from models.qna_assistant import QnAInstance
from models.draft_edit_assistant import DraftEditInstance
from modules import Project

verbose = False

table_generator_instance = TableGeneratorInstance(verbose=verbose)
keywords_generator_instance = KeywordsGeneratorInstance(verbose=verbose)
draft_generator_instance = DraftGeneratorInstance(verbose=verbose)
qna_instance = QnAInstance(verbose=verbose)
draft_edit_instance = DraftEditInstance(verbose=verbose)

embedchain = CustomEmbedChain()

# tools
search_by_url_tool = SearchByURLTool()
search_tool = SearchTool(search_by_url_tool=search_by_url_tool)

async def main():
    # project = Project(
    #     project_id="test_9", 
    #     table_generator_instance=table_generator_instance, 
    #     keywords_generator_instance=keywords_generator_instance, 
    #     draft_generator_instance=draft_generator_instance, 
    #     qna_instance=qna_instance,
    #     draft_edit_instance=draft_edit_instance,
    #     search_tool=search_tool,
    #     embed_chain=embedchain
    # )
    start = time.time()
    # purpose = project.set_purpose(purpose="2023 연고전 보고서")
    # project.save()
    # # 아래는 프로젝트 로드
    # project = Project.load_from_file( 
    #     table_generator_instance=table_generator_instance, 
    #     keywords_generator_instance=keywords_generator_instance, 
    #     draft_generator_instance=draft_generator_instance, 
    #     qna_instance=qna_instance,
    #     search_tool=search_tool,
    #     embed_chain=embedchain,
    #     draft_edit_instance=draft_edit_instance,
    #     user_instance_path='./user/test_9/user_instance.json')
    # table = project.get_table()
    # print('table: ', table, time.time()-start) # 10
    # # project.set_table(table="1.서론...") # 유저가 목차 변경
    # project.save()
    # 아래는 프로젝트 로드
    # project = Project.load_from_file( 
    #     table_generator_instance=table_generator_instance, 
    #     keywords_generator_instance=keywords_generator_instance, 
    #     draft_generator_instance=draft_generator_instance, 
    #     qna_instance=qna_instance,
    #     search_tool=search_tool,
    #     embed_chain=embedchain,
    #     draft_edit_instance=draft_edit_instance,
    #     user_instance_path='./user/test_9/user_instance.json')
    # keywords = project.get_keywords()
    # print('keywords: ', keywords, time.time()-start) # 13
    # files = await project.async_search_keywords()
    # print('searched files: ', len(project.files), time.time()-start) # 81.67
    # project.save()
    # 아래는 프로젝트 로드
    # project = Project.load_from_file( 
    #     table_generator_instance=table_generator_instance, 
    #     keywords_generator_instance=keywords_generator_instance, 
    #     draft_generator_instance=draft_generator_instance, 
    #     qna_instance=qna_instance,
    #     search_tool=search_tool,
    #     embed_chain=embedchain,
    #     draft_edit_instance=draft_edit_instance,
    #     user_instance_path='./user/test_9/user_instance.json')
    # user_files = [('https://en.wikipedia.org/wiki/Elon_Musk', 'web_page'), ('hello', 'text'), ('https://www.youtube.com/watch?v=Z4fBZGbk5iQ', 'youtube_video'), ('hello.docx', 'docx')]
    # project.add_files(files=user_files) # 유저가 직접 파일 추가
    # database = project.parse_files_to_embedchain()
    # print('database: ', database, time.time()-start) # 576
    # project.save()
    # # 아래는 프로젝트 로드
    # project = Project.load_from_file( 
    #     table_generator_instance=table_generator_instance, 
    #     keywords_generator_instance=keywords_generator_instance, 
    #     draft_generator_instance=draft_generator_instance, 
    #     qna_instance=qna_instance,
    #     search_tool=search_tool,
    #     embed_chain=embedchain,
    #     draft_edit_instance=draft_edit_instance,
    #     user_instance_path='./user/test_9/user_instance.json')
    # draft = project.get_draft(draft_id=2)
    # print('draft: ', draft, time.time()-start) # 1326
    # project.save()
    # 아래는 프로젝트 로드
    project = Project.load_from_file( 
        table_generator_instance=table_generator_instance, 
        keywords_generator_instance=keywords_generator_instance, 
        draft_generator_instance=draft_generator_instance, 
        qna_instance=qna_instance,
        search_tool=search_tool,
        embed_chain=embedchain,
        draft_edit_instance=draft_edit_instance,
        user_instance_path='./user/test_9/user_instance.json')
    # qna_history = [] # [[question1, answer1], ...]
    # question="연고전 야구 스코어는?"
    # answer = project.get_qna_answer(question=question, qna_history=qna_history, queue=[])
    # qna_history.append([question, answer])
    # print('answer: ', answer, time.time()-start) # 1326
    draft_part = """
## 2. 경기 결과 및 분석
### 각 경기별 결과 요약

2023 연고전에서는 다양한 종목의 경기가 펼쳐졌습니다. 각 경기의 결과를 요약하면 다음과 같습니다:

| 종목 | 연세대학교 | 고려대학교 |
|------|-----------|-----------|
| 축구 | 2         | 1         |
| 농구 | 78        | 82        |
| 배구 | 3         | 0         |
"""
    query = "연고전 경기 결과를 표를 그래프로 만들어줘"
    start = time.time()
    draft = project.edit_draft(draft_part=draft_part, query=query) # part_draft: 유저가 드래그한 부분, query: 유저 커맨드, draft: draft 텍스트 반환

if __name__ == "__main__":
    asyncio.run(main())