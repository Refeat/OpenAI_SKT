from abc import ABC, abstractmethod

class BaseAPI(ABC):
    def __init__(self):
        self.base_url = None
        self.name = None

    @abstractmethod
    def search(self, query):
        pass

    @abstractmethod
    async def async_search(self, query):
        pass

    @abstractmethod
    def parse_result(self, result):
        pass