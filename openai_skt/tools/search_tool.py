import ast
import asyncio
import requests
from typing import Any, Dict, Optional, Type, Union
from pydantic import BaseModel, Field, root_validator

from langchain.tools import BaseTool
from bs4 import BeautifulSoup

from api import KostatAPI, GallupAPI, YoutubeAPI, GoogleSearchAPI, NaverSearchAPI, SerpApiSearch
from models.llm import UnifiedSummaryChunkChain

class SearchToolInputSchema(BaseModel):
    query: str
    question: str

class SearchTool(BaseTool):
    category_api_dict = {
        'all': [KostatAPI(), YoutubeAPI(), GoogleSearchAPI(), NaverSearchAPI()],
        # 'all': [KostatAPI(), GallupAPI(), YoutubeAPI(), SerpApiSearch(), NaverSearchAPI()],
        'kostat': [KostatAPI()],
        'gallup': [GallupAPI()],
        'youtube': [YoutubeAPI()],
        'google': [GoogleSearchAPI()],
        # 'google': [SerpApiSearch()],
        'naver': [NaverSearchAPI()],
        # TODO: Add more APIs
    }
    name = "search_tool"
    description = "A tool to search on internet. The input consists of a 'query' and a 'question', where 'query' is the search query and 'question' is the information you want to get. For example, {'query': 'bitcoin price history', 'question': 'what was the price of bitcoin in 2022?'} would be the input if you want to know the price of bitcoin in 2022. Input must contain both a query and a question."
    args_schema: Optional[Type[BaseModel]] = SearchToolInputSchema
    """Pydantic model class to validate and parse the tool's input arguments."""
    summary_chunk_chain: Any = None
    search_by_url_tool: Any = None

    def __init__(self, search_by_url_tool, summary_chunk_chain=None, summary_chunk_template=None, input_variables=None) -> None:
        super().__init__()
        if summary_chunk_chain is None:
            self.summary_chunk_chain = UnifiedSummaryChunkChain()
        else:
            self.summary_chunk_chain = summary_chunk_chain
        self.search_by_url_tool = search_by_url_tool

    def search(self, query, category='all', top_k=5):
        api_list = self.category_api_dict[category]
        result_dict = {}
        for api in api_list:
            result = api.search(query, top_k=top_k)
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

    def _parse_input(self, tool_input: Union[str, Dict]) -> Union[str, Dict[str, Any]]:
        """Convert tool input to pydantic model."""
        input_args = self.args_schema
        if isinstance(tool_input, str):
            input_dict = ast.literal_eval(tool_input)
            
            return input_dict
        else:
            if input_args is not None:
                result = input_args.parse_obj(tool_input)
                return {k: v for k, v in result.dict().items() if k in tool_input}
        return tool_input


    def _run(self, query, question=None) -> dict:
        query = query.replace('"', '').replace("'", '')
        if question is None:
            question = query
        search_result_list = self.search(query, category='google', top_k=10)['google_search']
        if len(search_result_list) == 0:
            return {
                "status": "error",
                "message": "No results found."
            }
        chunk = search_result_list[0]
        url = chunk['data_path']
        # 여기서 chain을 사용하여 전체 검색결과에서 답을 찾을 수 있는지 확인한다.
        # 결과는 답이 나오거나 or 추가 검색을 위한 url이 나온다.
        single_webpage_result = self.search_by_url_tool._run(url)
        if single_webpage_result['status'] == 'error':
            return single_webpage_result
        single_webpage_content = single_webpage_result['content']
        question = question if question else query
        summary_result = self.summary_chunk_chain.run(chunk=single_webpage_content, question=question)
        return summary_result

    async def _arun(self, query) -> dict:
        # Not implemented
        return await self.async_search(query, category='google')
    
class SearchByURLTool(BaseTool):
    name = "search_by_url_tool"
    description = "A tool to search on internet by url."
    args_schema: Optional[Type[BaseModel]] = None
    """Pydantic model class to validate and parse the tool's input arguments."""

    def _run(self, query: str) -> dict:
        # Trim single and double quotes
        url = query.strip("'\"")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            
            # Check if the request was successful
            response.raise_for_status()

            # Use BeautifulSoup to parse the content and extract text
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)
            
            return {
                "status": "success",
                "content": text_content
            }
        except requests.RequestException as e:
            # Handle any exceptions that occurred during the request
            return {
                "status": "error",
                "message": str(e)
            }

    async def _arun(self, query) -> dict:
        # You might want to use an async library like 'httpx' here for asynchronous requests
        pass