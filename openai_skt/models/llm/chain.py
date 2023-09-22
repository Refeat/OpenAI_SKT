import os
import re
from typing import List, Any, Dict

from langchain.prompts import PromptTemplate
from langchain.prompts.loading import load_prompt
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import LLMResult

current_file_folder_path = os.path.dirname(os.path.abspath(__file__))

class CustomStreamingStdOutCallbackHandler(StreamingStdOutCallbackHandler):
    def __init__(
        self,
        *,
        queue,
    ) -> None:
        super().__init__()
        self.queue = queue

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        # sys.stdout.write(token)
        # sys.stdout.flush()
        if self.queue is not None:
            self.queue.append(token)
            
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        if self.queue is not None:
            self.queue.append('<br/>')

class BaseChain:
    def __init__(self, 
                 template:str=None, 
                 input_variables:List[str]=None, 
                 template_path:str=None, 
                 model="gpt-3.5-turbo",
                 verbose=False,
                 streaming=False,
                 temperature=0.0) -> None:
        self.prompt = self._get_prompt(template, input_variables, template_path)
        self.llm = ChatOpenAI(model=model, temperature=temperature, streaming=streaming)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose=verbose)

    def _get_prompt(self, template, input_variables, template_path):
        if template:
            assert input_variables, "input_variables must prompt_template.txtbe provided with template."
            return PromptTemplate(input_variables=input_variables, template=template)
        elif template_path:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            return PromptTemplate(input_variables=input_variables, template=template)
        raise ValueError("Either template or template_path should be provided.")

    def run(self, callbacks=None, **kwargs):
        input_dict = self.parse_input(**kwargs)
        result = self.chain.run(input_dict, callbacks=callbacks)
        return self.parse_output(result)

    async def arun(self, **kwargs):
        input_dict = self.parse_input(**kwargs)
        result = await self.chain.arun(input_dict)
        return self.parse_output(result)

    def parse_input(self, **kwargs):
        return kwargs

    def parse_output(self, output):
        return output

class KeywordsChain(BaseChain):
    def __init__(self, 
                 keywords_template=None, 
                 input_variables:List[str]=["purpose", "table"],
                 keywords_template_path=os.path.join(current_file_folder_path, '../templates/keywords_prompt_template.txt'), 
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
                input_variables:List[str]=["purpose", "draft", "database", "single_table", "table"],
                draft_template_path=os.path.join(current_file_folder_path, '../templates/draft_prompt_template.txt'),
                model='gpt-3.5-turbo-16k', 
                verbose=False,
                streaming=True) -> None:
        super().__init__(template=draft_template, input_variables=input_variables, template_path=draft_template_path, model=model, verbose=verbose, streaming=streaming)
        self.streaming = streaming

    def run(self, database=None, purpose=None, table=None, draft=None, single_table=None, queue=None):
        if self.streaming:
            callbacks=[CustomStreamingStdOutCallbackHandler(queue=queue)]
        else:
            callbacks=None
        return self.chain.run(callbacks=callbacks, database=database, purpose=purpose, table=table, draft=draft, single_table=single_table)
    
    async def arun(self, database=None, purpose=None, table=None, draft=None, single_table=None):
        return await super().arun(database=database, purpose=purpose, table=table, draft=draft, single_table=single_table)
       
class TableChain(BaseChain):
    def __init__(self, 
                table_template=None, 
                input_variables:List[str]=["purpose"],
                table_template_path=os.path.join(current_file_folder_path, '../templates/table_prompt_template.txt'),
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
                input_variables:List[str]=["draft", "query"],
                draft_chunk_template_path=os.path.join(current_file_folder_path, '../templates/draft_chunk_prompt_template.txt'),
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
                input_variables:List[str]=["graph_to_draw"],
                graph_template_path=os.path.join(current_file_folder_path, '../templates/graph_prompt_template.txt'),
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
                input_variables:List[str]=["document"],
                summary_chunk_template_path=os.path.join(current_file_folder_path, '../templates/summary_chunk_prompt_template.txt'),
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
                input_variables:List[str]=["question", "document"],
                summary_chunk_template_path=os.path.join(current_file_folder_path, '../templates/unified_summary_chunk_prompt_template.txt'),
                model='gpt-3.5-turbo-16k', 
                verbose=False) -> None:
        
        super().__init__(template=summary_chunk_template, input_variables=input_variables, template_path=summary_chunk_template_path, model=model, verbose=verbose)

    def run(self, chunk:str=None, question:str=None):
        return super().run(document=chunk, question=question)
    
    async def arun(self,chunk:str=None, question:str=None):
        return await super().arun(document=chunk, question=question)

class QnAPlanChain(BaseChain):
    def __init__(self, 
                qna_plan_template=None, 
                input_variables:List[str]=["chat_history", "user_input"],
                qna_plan_template_path=os.path.join(current_file_folder_path, '../templates/qna_plan_prompt_template.txt'), 
                model='gpt-4', 
                verbose=False) -> None:
        super().__init__(template=qna_plan_template, input_variables=input_variables, template_path=qna_plan_template_path, model=model, verbose=verbose)

    def run(self, user_input:str=None, chat_history:List[List[str]]=None):
        return super().run(user_input=user_input, chat_history=chat_history)
    
    async def arun(self, user_input:str=None, chat_history:List[List[str]]=None):
        return await super().arun(user_input=user_input, chat_history=chat_history)

    def parse_input(self, user_input:str=None, chat_history:List[List[str]]=None):
        chat_history_text = ""
        for chat in chat_history[-2:]:
            chat_history_text += f"User: {chat[0]}\n"
            chat_history_text += f"Agent: {chat[1]}\n"
        return {"chat_history": chat_history_text, "user_input": user_input}

    def parse_output(self, output:str=None):
        if 'Ask to user: ' in output:
            return output.split('Ask to user: ')[1].strip().split('\n')[0].strip()
        elif 'Step' in output:
            plans = re.findall(r'Step\d+: (?:\n)?(.*?\.)(?=\s|$)', output)
            return plans
        else:
            raise ValueError('Invalid output format')

class QnACriticChain(BaseChain):
    def __init__(self, 
                qna_critic_template=None, 
                input_variables:List[str]=["chat_history", "user_input", "plan_and_obs"],
                qna_critic_template_path=os.path.join(current_file_folder_path, '../templates/qna_critic_prompt_template.txt'), 
                model='gpt-4', 
                verbose=False) -> None:
        super().__init__(template=qna_critic_template, input_variables=input_variables, template_path=qna_critic_template_path, model=model, verbose=verbose)

    def run(self, user_input:str=None, plan_and_obs:List=None, chat_history:List[List[str]]=None):
        return super().run(user_input=user_input, plan_and_obs=plan_and_obs, chat_history=chat_history)
    
    async def arun(self, user_input:str=None, plan_and_obs:List[List[str]]=None, chat_history:List[List[str]]=None):
        return await super().arun(user_input=user_input, plan_and_obs=plan_and_obs, chat_history=chat_history)

    def parse_input(self, user_input:str=None, plan_and_obs:List[List[str]]=None, chat_history:List[List[str]]=None):
        chat_history_text = ""
        for user, agent in chat_history[-3:]:
            chat_history_text += f"User: {user}\n"
            chat_history_text += f"Agent: {agent}\n"

        plan_and_obs_text = ""
        for idx, (plan, obs) in enumerate(plan_and_obs):
            plan_and_obs_text += f"Plan{idx+1}: {plan}\n"
            plan_and_obs_text += f"Obs{idx+1}: {obs}\n"
        return {"chat_history": chat_history_text, "user_input": user_input, "plan_and_obs": plan_and_obs_text}
    
    def parse_output(self, output:str=None):
        return output.split('Final Answer: ')[1][0]
        
class WebIntegrateSearchChain(BaseChain):
    def __init__(self, 
                web_integrate_search_template=None, 
                input_variables:List[str]=["purpose", "search_results"],
                web_integrate_search_template_path=os.path.join(current_file_folder_path, '../templates/web_integrate_search_prompt_template.txt'), 
                model='gpt-4', 
                verbose=False) -> None:
        super().__init__(template=web_integrate_search_template, input_variables=input_variables, template_path=web_integrate_search_template_path, model=model, verbose=verbose)

    def run(self, purpose:str=None, search_results:List[Dict[str,str]]=None):
        return super().run(purpose=purpose, search_results=search_results)
    
    async def arun(self, purpose:str=None, search_results:List[Dict[str,str]]=None):
        return await super().arun(purpose=purpose, search_results=search_results)

    def parse_input(self, purpose:str=None, search_results:List[Dict[str,str]]=None):
        search_results_text = ''
        for idx, search_result in enumerate(search_results):
            search_results_text += f"web_result_{idx}(title:{search_result['title']}\tdescription:{search_result['description']}\turl:{search_result['data_path']})\n"
        return {
            "purpose": purpose,
            "search_results": search_results_text
        }        

    def parse_output(self, output:str=None):
        match = re.search(r'<Answer Type>\s*(\w+)\s*</Answer Type>\s*<Answer Description>\s*([^<]+)\s*</Answer Description>\s*<Answer link>\s*([^<]+)\s*</Answer link>', output)
        if match:
            final_answer_type = match.group(1) or ''
            final_answer = match.group(2) or ''
            final_answer_url = match.group(3) or ''
        return final_answer_type, final_answer, final_answer_url

class ImageGenerationChain(BaseChain):
    def __init__(self, 
                image_generation_template=None, 
                input_variables:List[str]=["table"],
                image_generation_template_path=os.path.join(current_file_folder_path, '../templates/image_generation_prompt_template.txt'), 
                model='gpt-3.5-turbo', 
                verbose=False,
                temperature=0.5) -> None:
        super().__init__(template=image_generation_template, input_variables=input_variables, template_path=image_generation_template_path, model=model, verbose=verbose)

    def run(self, table:str=None):
        return super().run(table=table)
    
    async def arun(self, table:str=None):
        return await super().run(table=table)

    def parse_output(self, output):
        output = output.replace('"', '').replace("'", '')
        return output