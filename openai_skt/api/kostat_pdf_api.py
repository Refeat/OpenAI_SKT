import re
import asyncio
import urllib
import requests
import os

import aiohttp
from bs4 import BeautifulSoup

try:
    from api.base import BaseAPI
except ImportError:
    from base import BaseAPI

import sys

from embedchain.vectordb.chroma_db import ChromaDB
from embedchain.embedder.openai_embedder import OpenAiEmbedder

from embedchain.config import (AppConfig, BaseEmbedderConfig, BaseLlmConfig,
                               ChromaDbConfig)

### Init database at global scope - this is to avoid pydantic conflicts
### We'll fix this at future
sys.path.append('/home/ubuntu/draft/writer/openai_skt')
### Set OpenAI key 
import configparser
config = configparser.ConfigParser()
config.read('/home/ubuntu/draft/writer/.secrets.ini')
OPENAI_API_KEY = config['OPENAI']['OPENAI_API_KEY']
os.environ.update({'OPENAI_API_KEY': OPENAI_API_KEY})
# Do NOT add data in this API, use only query
config = AppConfig()
db = ChromaDB(config=None)
embedder = OpenAiEmbedder(config=BaseEmbedderConfig(model="text-embedding-ada-002"))
# Initialize database
db._set_embedder(embedder)
db._initialize()
# Set collection name from app config for backwards compatibility.
if config.collection_name:
    db.set_collection_name(config.collection_name)

# This is to filter useless kostat pdf
threshold = 0.28

class KostatPDFAPI(BaseAPI):
    # 통계청 API
    # 검색 카테고리: 통계청누리집, 지표누리, 국가통계포털(KOSIS)통계표, 온라인간행물, 통계설명자료, 통계용어
    category = ['통계청누리집', '국가통계포털(KOSIS)통계표'] # 나머지는 구현이 안되어 있음
    def __init__(self, category='통계청누리집'):
        super().__init__()
        self.base_url = 'https://kostat.go.kr/'
        self.search_url = self.base_url + 'unifSearch/search.es'
        self.name = 'kostat'
        if category not in self.category:
            raise ValueError(f"category must be one of {self.category}")
        self.category = category

    # # 사용하지 않는 것이 좋아보임
    # def search(self, query, top_k:int = 5, **kwargs):
    #     data, headers = self.parse_input(query, **kwargs)

    #     response = requests.post(self.search_url, data=data, headers=headers)
        
    #     if response.status_code == 200:
    #         html_content = response.text
    #         search_results = self.parse_result(html_content)
    #         return search_results[:top_k]
    #     else:
    #         print('통계청 API 검색 요청에 실패하였습니다., status_code:', response.status_code)
    #         return []
    
    def search(self, query, top_k:int = 5, **kwargs):
        # input list of query ex) ['hi', 'hello']
        # output list of list of chunks zz ex) [[chunk1forquery1, chunk2forquery1, ..], [chunk1forquery2, chunk2forquery2, ...]]
        if isinstance(query, str):
            query_texts = [query]
        elif isinstance(query, list):
            query_texts = query
        else:
            raise TypeError('query should be str or list of str')
        # print(query_texts)
        result_id_list = db.collection.query(query_texts=query_texts, n_results=top_k, where = {'data_source_type': 'kostat'}, include = ["distances", "metadatas", "documents"])
        # print(result_id_list)
        print(result_id_list['distances'])
        search_results = []
        for i in range(len(result_id_list['metadatas'][0])):
            if result_id_list['distances'][0][i] < threshold:
                search_results.append({
                    'title': result_id_list['metadatas'][0][i]['url'][:-4],
                    'description': result_id_list['documents'][0][i][:80],
                    'data_type': result_id_list['metadatas'][0][i]['data_type'],
                    'data_path': '/home/ubuntu/data/kostat/files/' + result_id_list['metadatas'][0][i]['url']
                })
        return search_results
        
    async def async_search(self, query, top_k:int = 5, **kwargs):
        # input list of query ex) ['hi', 'hello']
        # output list of list of chunks zz ex) [[chunk1forquery1, chunk2forquery1, ..], [chunk1forquery2, chunk2forquery2, ...]]
        return self.search(query, top_k)

    
    async def async_search_web(self, query, top_k:int = 5, **kwargs):
        data, headers = self.parse_input(query, **kwargs)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.search_url, data=data, headers=headers) as response:
                    html_content = await response.text()
                    search_results = self.parse_result(html_content)
                    tasks = [self.async_check_pdf(result['data_path']) for result in search_results[:top_k]]
                    pdf_urls = await asyncio.gather(*tasks)
                    for i in range(len(pdf_urls)):
                        if pdf_urls[i] is not None:
                            search_results[i]['data_path'] = pdf_urls[i]
                            search_results[i]['data_type'] = 'pdf_file'
                    return search_results[:top_k]
            except aiohttp.ClientError as e:  # 가장 일반적인 aiohttp 예외
                print(f"Request to {self.search_url} failed with error: {e}")
                return []
            except Exception as e:  # 그 외의 예외를 포착
                print(f"Unexpected error: {e}")
                return []

    def parse_result(self, result):
        soup = BeautifulSoup(result, 'lxml')

        search_results = []

        # 각 항목(리스트 아이템)을 순회
        if self.category == '통계청누리집':
            for li in soup.select('div.gsb_list.srh_rlist > ul > li'):
                title = li.select_one('a.gsbl_link').text.strip()
                date_full = li.select_one('p.gsbl_info').text.strip()
                date_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', date_full)
                date = date_match.group(1) if date_match else date_full
                description = li.select_one('p.gsbl_descript').text.strip()
                url = li.select_one('a.gsbl_link')['href']
                url = self.parse_url(url)

                search_results.append({
                    'title': title,
                    'date': date,
                    'description': description,
                    'data_type': 'web_page',
                    'data_path': url
                })

        elif self.category == '국가통계포털(KOSIS)통계표':
            for li in soup.select('div.gsb_list.srh_rlist > ul > li'):
                title = li.select_one('a.gsbl_link').text.replace('<!--HS-->', '').replace('<!--HE-->', '').strip()
                date = li.select_one('p.gsbl_info').text.strip()
                description = li.select_one('p.gsbl_descript').text.strip()
                javascript_url = li.select_one('a.gsbl_link')['href']
                url = self.parse_url(javascript_url)

                search_results.append({
                    'title': title,
                    'date': date,
                    'description': description,
                    'data_type': 'web_page',
                    'data_path': url
                })
        return search_results
    
    def parse_url(self, url):
        if self.category == '통계청누리집':
            return urllib.parse.urljoin(self.base_url, url)
        elif self.category == '국가통계포털(KOSIS)통계표':
            parameters = re.findall(r"'(.*?)'", url)

            # 파라미터에 맞게 매핑
            orgId = parameters[0]
            tblId = parameters[1]
            path = parameters[3]
            vw_cd = parameters[4]
            list_id = parameters[5]

            base_url = "https://kosis.kr/statHtml/statHtml.do"
            params = {
                "orgId": orgId,
                "tblId": tblId,
                "vw_cd": vw_cd,
                "list_id": list_id,
                "scrId": "",
                "seqNo": "",
                "lang_mode": "ko",
                "obj_var_id": "",
                "itm_id": "",
                "conn_path": "K1",
                "path": urllib.parse.quote(path)
            }

            return base_url + "?" + urllib.parse.urlencode(params)
    
    async def async_check_pdf(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'lxml')
                    elements_with_class = soup.find_all(class_='bvf_name')
                    if elements_with_class:
                        root, _ = os.path.splitext(elements_with_class[0].text)
                        pdf_url = '/home/ubuntu/data/kostat/files/' + root + '.pdf'
                        if os.path.exists(pdf_url):
                            return pdf_url
                    
                    return None
            except aiohttp.ClientError as e:  # 가장 일반적인 aiohttp 예외
                print(f"Request to {self.search_url} failed with error: {e}")
                return None
            except Exception as e:  # 그 외의 예외를 포착
                print(f"Unexpected error: {e}")
                return None
    
    def parse_input(self, query, **kwargs):
        body_search_dict = {
            '통계청누리집': 'web_bodo',
            '국가통계포털(KOSIS)통계표': 'statDB'
            }
        body_collection_dict = {
            '통계청누리집': 'web_bodo',
            '국가통계포털(KOSIS)통계표': 'statDB'
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ko,ko-KR;q=0.9,en;q=0.8,en-US;q=0.7,en-GB;q=0.6,ja;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "",
            "Host": "kostat.go.kr",
            "Origin": "https://kostat.go.kr",
            "Referer": "https://kostat.go.kr/unifSearch/search.es",
            "Sec-Ch-Ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }
        
        # Create payload (reduced to only the essentials, as you provided before)
        data = {
            'start': 0,
            'start1': 0,
            'count': 10,
            'startCount': 0,
            'startCount1': 0,
            'startDate': '',
            'endDate': '',
            'viewCount': 0,
            'viewContent': 'Y',
            'range': '',
            'subCol': 'ALL',
            'sort': 'DATE,1',
            'sortField': 'RANK,1',
            'searchOption': '',
            'divField': '',
            'datesearch': 'no',
            'requery': '',
            'lastquery': '',
            'detailSearchf': 'N',
            'subjectSearch': '',
            'synYN': 'Y',
            'searchField': '',
            'openDivClass3': '',
            'cookie': '000',
            'jopage': 1,
            'arkChk': 'Y',
            'YstartTmp': '',
            'MstartTmp': '',
            'DstartTmp': '',
            'YendTmp': '',
            'MendTmp': '',
            'DendTmp': '',
            'sortCondition': '',
            'searchFieldCondition': '',
            'termsCondition': '',
            'viewcountCondition': '',
            'statDBsearchField1': 1,
            'statDBsearchField2': 1,
            'statDBsearchField3': 1,
            'statDBsearchField4': 1,
            'statDBsearchField5': 1,
            'webCheckbox1': '',
            'webCheckbox2': '',
            'webCheckbox3': '',
            'webCheckbox4': '',
            'webCheckbox5': '',
            'webCheckbox6': '',
            'webCheckbox7': '',
            'webCheckbox8': '',
            'webCheckbox9': '',
            'webCheckbox10': '',
            'webCheckbox11': '',
            'webCheckbox12': '',
            'webCheckbox13': '',
            'hireCheckbox1': '',
            'hireCheckbox2': '',
            'hireCheckbox3': '',
            'hireCheckbox4': '',
            'hireCheckbox5': '',
            'hireCheckbox6': '',
            'hireCheckbox7': '',
            'hireCheckbox8': '',
            'hireCheckbox9': '',
            'collection': body_collection_dict[self.category],
            'statId': '',
            'orgCode': '',
            'select_search': body_search_dict[self.category],
            'query': query
        }
        data.update(kwargs)

        return data, headers
    
if __name__ == "__main__":
    kostat_api = KostatPDFAPI(category='통계청누리집')
    # Using asyncio to run the async function
    # result = asyncio.run(kostat_api.async_search_web('부동산'))
    # print(result)
    # result = asyncio.run(kostat_api.async_search('부동산'))
    # print(result)
    result = kostat_api.search('3D AI', top_k=20)
    print(result)
    print(len(result))