from typing import List

from langchain.prompts import load_prompt
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.embeddings import OpenAIEmbeddings


class KeywordsChain:
    def __init__(self, keywords_template_path='../openai_skt/models/templates/keywords_prompt.json', verbose=False) -> None:
        self.keywords_template_path = keywords_template_path
        self.keywords_prompt = load_prompt(self.keywords_template_path)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        self.verbose = verbose
        self.description_chain = LLMChain(llm=self.llm, prompt=self.keywords_prompt, verbose=self.verbose)

    def run(self, purpose:str=None):
        input_dict = {'purpose': purpose}
        keywords = self.description_chain.run(input_dict)
        return keywords

    async def arun(self, purpose:str=None):
        input_dict = {'purpose': purpose}
        keywords = await self.description_chain.arun(input_dict)
        return keywords

class DraftChain:
    def __init__(self, draft_template_path='../openai_skt/models/templates/draft_prompt.json', verbose=False) -> None:
        self.draft_template_path = draft_template_path
        self.draft_prompt = load_prompt(self.draft_template_path)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        self.verbose = verbose
        self.draft_chain = LLMChain(llm=self.llm, prompt=self.draft_prompt, verbose=self.verbose)

    def run(self, purpose:str=None, keywords:List[str]=None, database=None):
        input_dict = self.preprocess(purpose, keywords, database)
        draft = self.draft_chain.run(input_dict)
        return draft

    async def arun(self, purpose:str=None, keywords:List[str]=None, database=None):
        input_dict = self.preprocess(purpose, keywords, database)
        draft = await self.draft_chain.arun(input_dict)
        return draft
    
    def preprocess(self, purpose:str=None, keywords:List[str]=None, database=None):
        # TODO: 입력 정리
        purpose_input = purpose
        keywords_input = keywords
        database_input = database
        input_dict = {'purpose': purpose_input, 'keywords': keywords_input, 'database': database_input}
        return input_dict