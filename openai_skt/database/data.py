from abc import ABC, abstractmethod

class Data(ABC):
    def __init__(self) -> None:
        self.data_path = None
        self.data = None
        self.embedding = None
        self.type = None

    def init_data(self, type:str=None, data_path:str=None):
        if type is not None:
            self.type = type
        else:
            raise ValueError("type must be specified")
        if data_path is not None:
            self.data_path = data_path
        else:
            raise ValueError("data_path must be specified")
        self.parse_data()

    def load_data(self):
        pass

    def save_data(self):
        pass

    @abstractmethod
    def parse_data(self):
        pass

    @abstractmethod
    async def async_get_embedding(self):
        pass

class WebSite(Data):
    def __init__(self) -> None:
        super().__init__()

class Pdf:
    pass

class Doc:
    pass

class Notion:
    pass

class Youtube:
    pass

