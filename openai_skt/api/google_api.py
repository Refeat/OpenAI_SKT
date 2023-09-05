import os

try:
    try:
        GOOGLE_SEARCH_KEY = os.environ['GOOGLE_SEARCH_KEY']
        CSE_ID = os.environ['CSE_ID']
    except:
        import configparser

        config = configparser.ConfigParser()
        config.read('../.secrets.ini')
        GOOGLE_SEARCH_KEY = config['GOOGLE']['GOOGLE_API_KEY']
        CSE_ID = config['GOOGLE']['CSE_ID']
except:
    from django.conf import settings
    config = settings.KEY_INFORMATION
    GOOGLE_SEARCH_KEY = config['GOOGLE']['GOOGLE_API_KEY']
    CSE_ID = config['GOOGLE']['CSE_ID']

import requests

import aiohttp

from api.base import BaseAPI

class GoogleSearchAPI(BaseAPI):
    # 구글 검색 API
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.googleapis.com/customsearch/v1?'
        self.name = 'google_search'
        self.api_key = GOOGLE_SEARCH_KEY
        self.cse_id = CSE_ID

    def search(self, query:str, top_k:int = 5):
        response = self._google_search(query, top_k)
        return self.parse_result(response)

    async def async_search(self, query:str, top_k:int = 5):
        response = await self._google_search_async(query, top_k)
        return self.parse_result(response)

    def _google_search(self, query, top_k):
        try:
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.cse_id,
                "num": top_k
            }
            response = requests.get(self.base_url, params=params)
            return response.json()
        except:
            print("Warning: Google Search API request failed.")
            return {}

    async def _google_search_async(self, query, top_k):
        try:
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.cse_id,
                "num": top_k
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    return await response.json()
        except:
            print("Warning: Google Search API request failed.")
            return {}

    def parse_result(self, result):
        ret = []
        try:
            for item in result['items']:
                ret.append({
                    'title': item['title'],
                    # '링크': item['link'],
                    'description': item.get('snippet', ''),
                    'data_type': 'web_page',
                    'data_path': item['link'],
                })
        except:
            print(f"Warning: In {result}, 'items' key not found in the result.")
        return ret