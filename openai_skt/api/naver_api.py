from api.base import BaseAPI
import requests
import configparser

config = configparser.ConfigParser()
config.read('../.secrets.ini')
try:
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
        response = await self._async_naver_search(query, top_k)
        return self.parse_result(response)

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
        if 'items' in result:
            for item in result['items']:
                ret.append({
                    'title': item['title'],
                    # '링크': item['link'],
                    'description': item['description'],
                    'data_type': 'web_page',
                    'data_path': item['link'],
                })
        else:
            print("Warning: 'items' key not found in the result.")
        return ret

    async def async_parse_result(self, result):
        return self.parse_result(result)