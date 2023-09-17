from embedchain.helper_classes.json_serializable import JSONSerializable

class BaseLoader(JSONSerializable):
    def __init__(self):
        pass

    def load_data():
        """
        Implemented by child classes
        """
        pass

    async def load_data_async(self, *args, **kwargs):
        """
        Implemented by child classes
        """
        return self.load_data(*args, **kwargs)