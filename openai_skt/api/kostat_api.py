from api.base import BaseAPI

class KostatAPI(BaseAPI):
    # 통계청 API
    def __init__(self):
        super().__init__()
        self.base_url = 'https://kostat.go.kr/'
        self.name = 'kostat'

    def search(self, query):
        pass
    
    async def async_search(self, query):
        # Implement your asynchronous search logic here
        pass

    def parse_result(self, result):
        pass

    async def async_parse_result(self, result):
        # Implement your asynchronous parse logic here
        pass