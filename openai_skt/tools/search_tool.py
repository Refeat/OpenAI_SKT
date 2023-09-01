import asyncio
from api import KostatAPI, GallupAPI, YoutubeAPI

class SearchTool:
    category_api_dict = {
        'all': [KostatAPI(), GallupAPI()],
        'statistics': [KostatAPI()],
        # TODO: Add more APIs
    }
    def __init__(self) -> None:
        pass

    def search(self, query, category='all'):
        api_list = self.category_api_dict[category]
        result_dict = {}
        for api in api_list:
            result = api.search(query)
            result_dict[api.name] = result
        return result_dict

    async def async_search(self, query, category='all'):
        api_list = self.category_api_dict[category]
        result_dict = {}
        
        # Run all API searches concurrently using asyncio.gather
        results = await asyncio.gather(*[api.async_search(query) for api in api_list])

        # Map results to their respective API names
        for api, result in zip(api_list, results):
            result_dict[api.name] = result

        return result_dict
