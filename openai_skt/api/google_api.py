import configparser

config = configparser.ConfigParser()
config.read('../.secrets.ini')
GOOGLE_SEARCH_KEY = config['GOOGLE']['GOOGLE_API_KEY']
CSE_ID = config['GOOGLE']['CSE_ID']

import requests

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
        return self.search(query, top_k)

    def _google_search(self, query, top_k):
        params = {
            "q": query,
            "key": self.api_key,
            "cx": self.cse_id,
            "num": top_k
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def parse_result(self, result):
        ret = []
        for item in result['items']:
            ret.append({
                '제목': item['title'],
                '링크': item['link'],
                '설명': item.get('snippet', ''),
                'data_type': 'web_page',
                'data_path': item['link'],
            })
        return ret

    async def async_parse_result(self, result):
        return self.parse_result(result)