from api.base import BaseAPI

class GallupAPI(BaseAPI):
    # 갤럽 API
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.gallup.co.kr/'
        self.name = 'gallup'

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