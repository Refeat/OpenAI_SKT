from api.base import BaseAPI
import requests
import configparser

config = configparser.ConfigParser()
config.read('../.secrets.ini')
NAVER_CLIENT_ID = config['NAVER']['NAVER_CLIENT_ID']
NAVER_CLIENT_SECRET = config['NAVER']['NAVER_CLIENT_SECRET']

class NaverSearchAPI(BaseAPI):
    # 네이버 검색 API
    def __init__(self):
        super().__init__()
        self.base_url = 'https://openapi.naver.com/v1/search/webkr'  # 웹문서 검색 API URL, 다른 종류의 검색을 원하면 URL 변경 필요
        self.name = 'naver_search'
        self.client_id = NAVER_CLIENT_ID
        self.client_secret = NAVER_CLIENT_SECRET

    def search(self, query:str, top_k:int = 5):
        response = self._naver_search(query, top_k)
        return self.parse_result(response)

    async def async_search(self, query:str, top_k:int = 5):
        return self.search(query, top_k)

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

    def parse_result(self, result):
        ret = []
        for item in result['items']:
            ret.append({
                '제목': item['title'],
                '링크': item['link'],
                '설명': item['description'],
                'data_type': 'naver_search_result',
                'data_path': item['link'],
            })
        return ret

    async def async_parse_result(self, result):
        return self.parse_result(result)
