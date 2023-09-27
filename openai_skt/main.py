import os
import configparser

import sys
sys.path.append('./database/chunk/VipsPython/Vips')

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

verbose = True

table_generator_instance = TableGeneratorInstance(verbose=verbose)
keywords_generator_instance = KeywordsGeneratorInstance(verbose=verbose)
draft_generator_instance = DraftGeneratorInstance(verbose=verbose)
qna_instance = QnAInstance(verbose=verbose)
draft_edit_instance = DraftEditInstance(verbose=True)

embedchain = CustomEmbedChain()

# tools
search_by_url_tool = SearchByURLTool()
search_tool = SearchTool(search_by_url_tool=search_by_url_tool)

async def main():
    # project = Project(
    #     project_id="test_15", 
    #     table_generator_instance=table_generator_instance, 
    #     keywords_generator_instance=keywords_generator_instance, 
    #     draft_generator_instance=draft_generator_instance, 
    #     qna_instance=qna_instance,
    #     draft_edit_instance=draft_edit_instance,
    #     search_tool=search_tool,
    #     embed_chain=embedchain
    # )
    # start = time.time()
    # purpose = project.set_purpose(purpose="후쿠시마 오염수 방류")
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
    table = project.get_table()
    # print('table: ', table) # 10
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
    keywords = project.get_keywords()
    # print('keywords: ', keywords) # 13
    # project.set_keywords(keywords=['갈비탕', '감자탕', '해장국', '순대국', '뼈해장국', '곰탕', '설렁탕', '닭곰탕'])
    files = await project.async_search_keywords()
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
    # user_files = [('/root/OpenAI_SKT/openai_skt/tutorials/test_data/(보도자료) 제20회 전국학생통계활용대회 결과 발표.pdf', 'pdf_file'), ('../../OpenAI_SKT/openai_skt/tutorials/test_data/X2Download.app - 월세=월급, 미친 집값의 나라에서 한국인이 발견한 기회 _ 고투조이 변성민 (128 kbps).mp3', 'audio')]
    # user_files = [('/home/ubuntu/draft/writer/openai_skt/tutorials/test_data/(국립농산물품질관리원) 농관원  빅데이터 분석？활용 연구 기반 마련  보도자료(2.22. 조간).pdf', 'pdf_file'), ('/home/ubuntu/draft/writer/openai_skt/tutorials/test_data/X2Download.app - 월세=월급, 미친 집값의 나라에서 한국인이 발견한 기회 _ 고투조이 변성민 (128 kbps).mp3', 'audio'), ('https://pytorch.org/get-started/locally/', 'web_page')]
    # project.add_files(files=user_files) # 유저가 직접 파일 추가
    # start = time.time()
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
    draft = project.get_draft(draft_id=2)
    # print('draft: ', draft, time.time()-start) # 1326
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
    # qna_history = [] # [[question1, answer1], ...]
    # question="연고전 야구 스코어는?"
    # answer = project.get_qna_answer(question=question, qna_history=qna_history, queue=[])
    # qna_history.append([question, answer])
    # print('answer: ', answer, time.time()-start) # 1326
#     draft_part = """
# 아래 그래프는 1960년대부터 지금까지 연도별 미국의 물가상승률과 실업률의 관계 그래프다.
# """
#     query = "1960년대부터 지금까지 연도별 미국의 물가상승률과 실업률의 관계 그래프 그려줘. 데이터는 1년마다 표시해줘. x축은 연도, y축은 물가상승률과 실업률이다."
#     start = time.time()
#     draft = project.edit_draft(draft_part=draft_part, query=query) # part_draft: 유저가 드래그한 부분, query: 유저 커맨드, draft: draft 텍스트 반환

if __name__ == "__main__":
    asyncio.run(main())