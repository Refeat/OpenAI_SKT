class DataBase:
    def __init__(self):
        pass

    @classmethod
    def init_database(cls, files):
        database =  cls()
        # TODO:file 초기화
        return database

    @classmethod
    def load_database(cls, database_path:str):
        database = cls()
        # TODO:file 로드
        return database