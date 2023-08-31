from typing import List

from langchain.prompts import load_prompt, PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.embeddings import OpenAIEmbeddings


class KeywordsChain:
    def __init__(self, keywords_template=None, keywords_template_path='../openai_skt/models/templates/keywords_prompt.json', verbose=False) -> None:
        if keywords_template is not None:
            self.keywords_template = prompt = PromptTemplate(
                    input_variables=["purpose", "table"],
                    template=keywords_template,
                )
        else:
            self.keywords_template_path = keywords_template_path
            self.keywords_prompt = load_prompt(self.keywords_template_path)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        self.verbose = verbose
        self.keywords_chain = LLMChain(llm=self.llm, prompt=self.keywords_prompt, verbose=self.verbose)

    def run(self, purpose:str=None, table:List[str]=None):
        input_dict = {'purpose': purpose, 'tables': None}
        keywords = self.keywords_chain.run(input_dict)
        return keywords

    async def arun(self, purpose:str=None):
        input_dict = {'purpose': purpose}
        keywords = await self.keywords_chain.arun(input_dict)
        return keywords

class DraftChain:
    def __init__(self, draft_template=None, draft_template_path='../openai_skt/models/templates/draft_prompt.json', verbose=False) -> None:
        if draft_template is not None:
            self.draft_template = PromptTemplate(
                    input_variables=["purpose", "tables", "database"],
                    template=draft_template,
                )
        else:
            self.draft_template_path = draft_template_path
            self.draft_prompt = load_prompt(self.draft_template_path)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0.0)
        self.verbose = verbose
        self.draft_chain = LLMChain(llm=self.llm, prompt=self.draft_prompt, verbose=self.verbose)

    def run(self, purpose:str=None, table:List[str]=None, database=None):
        input_dict = self.preprocess(purpose, table, database)
        draft = self.draft_chain.run(input_dict)
        return draft

    async def arun(self, purpose:str=None, table:List[str]=None, database=None):
        input_dict = self.preprocess(purpose, table, database)
        draft = await self.draft_chain.arun(input_dict)
        return draft
    
    def preprocess(self, purpose:str=None, table:List[str]=None, database=None):
        # TODO: 입력 정리
        purpose_input = purpose
        # TODO: table 정리
        table_input = table
        database_input = database
        input_dict = {'purpose': purpose_input, 'table': table_input, 'database': database_input}
        return input_dict
    
class TableChain:
    def __init__(self, table_template=None, table_template_path='../openai_skt/models/templates/table_prompt.json', verbose=False) -> None:
        if table_template is not None:
            self.table_prompt = PromptTemplate(
                    input_variables=["purpose"],
                    template=table_template,
                )
        else:
            self.table_template_path = table_template_path
            self.table_prompt = load_prompt(self.table_template_path)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        self.verbose = verbose
        self.table_chain = LLMChain(llm=self.llm, prompt=self.table_prompt, verbose=self.verbose)

    def run(self, purpose:str=None):
        input_dict = {'purpose': purpose}
        table = self.table_chain.run(input_dict)
        return table

    async def arun(self, purpose:str=None):
        input_dict = {'purpose': purpose}
        table = await self.table_chain.arun(input_dict)
        return table