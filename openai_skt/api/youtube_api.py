from api.base import BaseAPI

class YoutubeAPI(BaseAPI):
    # 유튜브 API
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.youtube.com/'
        self.name = 'youtube'

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