import os
import re
import requests
import asyncio

from api.base import BaseAPI

try:
    try:
        NAVER_CLIENT_ID = os.environ['NAVER_CLIENT_ID']
        NAVER_CLIENT_SECRET = os.environ['NAVER_CLIENT_SECRET']
    except:
        import configparser
        config = configparser.ConfigParser()
        config.read('../.secrets.ini')
        NAVER_CLIENT_ID = config['NAVER']['NAVER_CLIENT_ID']
        NAVER_CLIENT_SECRET = config['NAVER']['NAVER_CLIENT_SECRET']
except:
    from django.conf import settings
    config = settings.KEY_INFORMATION
    NAVER_CLIENT_ID = config['NAVER']['NAVER_CLIENT_ID']
    NAVER_CLIENT_SECRET = config['NAVER']['NAVER_CLIENT_SECRET']

import aiohttp

class NaverSearchAPI(BaseAPI):
    # 네이버 검색 API
    def __init__(self):
        super().__init__()
        self.base_url = 'https://openapi.naver.com/v1/search/webkr'
        self.name = 'naver_search'
        self.client_id = NAVER_CLIENT_ID
        self.client_secret = NAVER_CLIENT_SECRET

    def search(self, query:str, top_k:int = 5):
        response = self._naver_search(query, top_k)
        return self.parse_result(response)

    async def async_search(self, query:str, top_k:int = 5):
        max_retries = 5
        retries = 0
        while retries < max_retries:
            response = await self._async_naver_search(query, top_k)
            
            if response.get('errorCode') != '012':  # Rate limit error code
                return self.parse_result(response)
            else:
                retries += 1
                # Optionally, you can add a delay here if required
                await asyncio.sleep(1)

        # If we reach here, it means we exhausted all our retries
        # You can either return an error, raise an exception, etc.
        print("Rate limit exceeded after maximum retries.")
        return []

    def _naver_search(self, query, top_k):
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        params = {
            "query": query,
            "display": top_k
        }
        response = requests.get(self.base_url, headers=headers, params=params)
        return response.json()

    async def _async_naver_search(self, query, top_k):
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        params = {
            "query": query,
            "display": top_k
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, headers=headers, params=params) as response:
                return await response.json()

    def parse_result(self, result):
        ret = []

        def remove_html_tags(text):
            # HTML 태그 제거
            clean = re.compile('<.*?>')
            return re.sub(clean, '', text)

        if 'items' in result:
            for item in result['items']:
                ret.append({
                    'title': remove_html_tags(item['title']),
                    # '링크': item['link'],
                    'description': remove_html_tags(item['description']),
                    'data_type': 'web_page',
                    'data_path': item['link'],
                })
        else:
            print(f"Warning: In {result}, 'items' key not found in the result.")
        return ret

    async def async_parse_result(self, result):
        return self.parse_result(result)