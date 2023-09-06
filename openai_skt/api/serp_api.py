import os

try:
    try:
        SERPAPI_KEY = os.environ['SERPAPI_KEY']
    except:
        import configparser

        config = configparser.ConfigParser()
        config.read('../.secrets.ini')
        SERPAPI_KEY = config['SERPAPI']['SERPAPI_KEY']
except:
    from django.conf import settings
    config = settings.KEY_INFORMATION
    SERPAPI_KEY = config['SERPAPI']['SERPAPI_KEY']
    
import requests
import aiohttp

from api.base import BaseAPI

class SerpApiSearch(BaseAPI):
    # serpapi 검색 API
    def __init__(self):
        super().__init__()
        self.base_url = 'https://serpapi.com/search.json'
        self.name = 'google_search'
        self.api_key = SERPAPI_KEY

    def search(self, query: str, top_k: int = 5):
        response = self._serpapi_search(query, top_k)
        return self.parse_result(response)[:top_k]

    async def async_search(self, query: str, top_k: int = 5):
        response = await self._serpapi_search_async(query, top_k)
        return self.parse_result(response)[:top_k]

    def _serpapi_search(self, query, top_k):
        try:
            params = {
                "q": query,
                "engine": "google",
                "api_key": self.api_key,
                "num": top_k
            }
            response = requests.get(self.base_url, params=params)
            return response.json()
        except:
            print("Warning: SerpApi Search API request failed.")
            return {}

    async def _serpapi_search_async(self, query, top_k):
        try:
            params = {
                "q": query,
                "engine": "google",
                "api_key": self.api_key
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    return await response.json()
        except:
            print("Warning: SerpApi Search API request failed.")
            return {}

    def parse_result(self, result):
        ret = []
        try:
            for item in result['organic_results']:
                ret.append({
                    'title': item['title'],
                    'description': item.get('snippet', ''),
                    'data_type': 'web_page',
                    'data_path': item['link'],
                })
        except:
            print(f"Warning: In {result}, 'items' key not found in the result.")
        return ret
