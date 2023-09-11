from typing import List

from langchain.prompts import PromptTemplate
from langchain.prompts.loading import load_prompt
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

from models.llm import utils

class BaseChain:
    def __init__(self, 
                 template:str=None, 
                 input_variables:List[str]=None, 
                 template_path:str=None, 
                 model="gpt-3.5-turbo",
                 verbose=False) -> None:
        self.prompt = self._get_prompt(template, input_variables, template_path)
        self.llm = ChatOpenAI(model=model, temperature=0.0)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose=verbose)

    def _get_prompt(self, template, input_variables, template_path):
        if template:
            assert input_variables, "input_variables must be provided with template."
            return PromptTemplate(input_variables=input_variables, template=template)
        elif template_path:
            return load_prompt(template_path)
        raise ValueError("Either template or template_path should be provided.")

    def run(self, **kwargs):
        input_dict = self.parse_input(**kwargs)
        return self.chain.run(input_dict)

    async def arun(self, **kwargs):
        input_dict = self.parse_input(**kwargs)
        return await self.chain.arun(input_dict)

    def parse_input(self, **kwargs):
        return kwargs

class KeywordsChain(BaseChain):
    def __init__(self, 
                 keywords_template=None, 
                 input_variables:List[str]=None,
                 keywords_template_path='../openai_skt/models/templates/keywords_prompt.json', 
                 model='gpt-4', 
                 verbose=False) -> None:
        super().__init__(keywords_template, input_variables, keywords_template_path, model, verbose)

    def run(self, purpose:str=None, table:str=None):
        return super().run(purpose=purpose, table=table)

    async def arun(self, purpose:str=None, table:str=None):
        return await super().arun(purpose=purpose, table=table)

class DraftChain(BaseChain):
    def __init__(self, 
                draft_template=None, 
                input_variables:List[str]=None,
                draft_template_path='../openai_skt/models/templates/draft_prompt.json', 
                model='gpt-3.5-turbo-16k', 
                verbose=False) -> None:
        super().__init__(template=draft_template, input_variables=input_variables, template_path=draft_template_path, model=model, verbose=verbose)

    def run(self, database=None, purpose=None, table=None, draft=None, single_table=None):
        return super().run(database=database, purpose=purpose, table=table, draft=draft, single_table=single_table)
    
    async def arun(self, database=None, purpose=None, table=None, draft=None, single_table=None):
        return await super().arun(database=database, purpose=purpose, table=table, draft=draft, single_table=single_table)
       
class TableChain(BaseChain):
    def __init__(self, 
                table_template=None, 
                input_variables:List[str]=None,
                table_template_path='../openai_skt/models/templates/table_prompt.json', 
                model='gpt-4', 
                verbose=False) -> None:
        super().__init__(template=table_template, input_variables=input_variables, template_path=table_template_path, model=model, verbose=verbose)

    def run(self, purpose=None):
        return super().run(purpose=purpose)
    
    async def arun(self, purpose=None):
        return await super().arun(purpose=purpose)
    
class DraftChunkChain(BaseChain):
    def __init__(self, 
                draft_chunk_template=None, 
                input_variables:List[str]=None,
                draft_chunk_template_path='../openai_skt/models/templates/draft_chunk_prompt.json', 
                model='gpt-3.5-turbo-16k', 
                verbose=False) -> None:
        super().__init__(template=draft_chunk_template, input_variables=input_variables, template_path=draft_chunk_template_path, model=model, verbose=verbose)

    def run(self, draft:str=None, query:str=None):
        return super().run(draft=draft, query=query)
    
    async def arun(self, draft:str=None, query:str=None):
        return await super().arun(draft=draft, query=query)
    
class GraphChain(BaseChain):
    def __init__(self, 
                graph_template=None, 
                input_variables:List[str]=None,
                graph_template_path='../openai_skt/models/templates/graph_prompt.json', 
                model='gpt-3.5-turbo', 
                verbose=False) -> None:
        super().__init__(template=graph_template, input_variables=input_variables, template_path=graph_template_path, model=model, verbose=verbose)

    def run(self, query:str=None):
        return super().run(graph_to_draw=query)
    
    async def arun(self,query:str=None):
        return await super().arun(graph_to_draw=query)
    
class SummaryChunkChain(BaseChain):
    def __init__(self, 
                summary_chunk_template=None, 
                input_variables:List[str]=None,
                summary_chunk_template_path='../openai_skt/models/templates/summary_chunk_prompt.json', 
                model='gpt-3.5-turbo-16k', 
                verbose=False) -> None:
        super().__init__(template=summary_chunk_template, input_variables=input_variables, template_path=summary_chunk_template_path, model=model, verbose=verbose)

    def run(self, chunk:str=None):
        return super().run(document=chunk)
    
    async def arun(self,chunk:str=None):
        return await super().arun(document=chunk)

class UnifiedSummaryChunkChain(BaseChain):
    def __init__(self, 
                summary_chunk_template=None, 
                input_variables:List[str]=None,
                summary_chunk_template_path='../openai_skt/models/templates/unified_summary_chunk_prompt.json', 
                model='gpt-3.5-turbo-16k', 
                verbose=False) -> None:
        super().__init__(template=summary_chunk_template, input_variables=input_variables, template_path=summary_chunk_template_path, model=model, verbose=verbose)

    def run(self, chunk:str=None, question:str=None):
        return super().run(document=chunk, question=question)
    
    async def arun(self,chunk:str=None, question:str=None):
        return await super().arun(document=chunk, question=question)