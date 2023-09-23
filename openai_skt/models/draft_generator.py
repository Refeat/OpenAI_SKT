import re
from typing import List

from modules import Draft, DraftPart
from models.llm import DraftChain, ImageGenerationChain, TableQueryChain, ReDraftChain
from api import DalleAPI

class DraftGeneratorInstance:
    def __init__(self, verbose=False, draft_chain=None) -> None:
        self.draft_chain = draft_chain
        if draft_chain == None:
            self.draft_chain = DraftChain(verbose=True)
        ## TODO gkggggg
        self.image_generation_chain = ImageGenerationChain(verbose=verbose)
        self.table_query_chain = TableQueryChain(verbose=verbose)
        self.dalle_api = DalleAPI()
        # self.redraft_chain = ReDraftChain(verbose=verbose)
        self.redraft_chain = ReDraftChain(verbose=True)

    def run(self, purpose:str=None, table:str=None, database=None, draft_id=None, queue=None) -> Draft:
        
        table_list = self.parse_table(table)
        draft = Draft(draft_id=draft_id, purpose=purpose, tables=table_list)
        print(table_list)
        print(len(table_list))
        for single_table in table_list:
            # query = self.table_query_chain.run(table=single_table)
            query = single_table
            print(single_table)
            chunk_list, data_text = self.parse_database(database, query=query)
            # print(query, single_table, chunk_list)
            # single_draft = self.draft_chain.run(purpose=purpose, draft=draft.text, single_table=single_table, database=data_text, table=table, queue=queue)
            new_draft = self.draft_chain.run(purpose=purpose, draft=draft.text, single_table=single_table, database=data_text, table=table)
            single_draft = self.redraft_chain.run(draft=new_draft, database=data_text, single_table=single_table, queue=queue)
            draft_part = DraftPart(text=single_draft, single_table=single_table, files=chunk_list)
            draft.add_draft_part(draft_part)
        image_url = self.generate_image(table)
        if image_url is not None:
            draft.text = f"\n![Generated Image]({image_url})\n\n" + draft.text
        
        return draft
    
    async def arun(self, purpose:str=None, table:str=None, database=None, draft_id=None):
        # TODO: 수정필요
        draft = await self.draft_chain.arun(purpose=purpose, table=table, database=database)
        return draft
    
    def parse_database(self, database, query:str=None)->str:
        chunk_list = database.query(query=query, max_token=4096)
        data_text = ''
        for idx, chunk in enumerate(chunk_list): # data is Chunk object
            data_text += f'{idx+1}. {chunk.data}\n'
        return chunk_list, data_text

    def parse_table(self, table:str=None) -> List[str]:
        table_list = re.split(r"(\d+\.)", table)[1:]  # 첫 번째 빈 문자열 제거

        # 숫자와 내용을 합침
        table_list = [table_list[i] + table_list[i+1] for i in range(0, len(table_list), 2)]

        return table_list

    def generate_image(self, table: str) -> str:
        max_retries = 3
        attempts = 0
        image_url = None
        while attempts < max_retries:
            try:
                image_caption = self.image_generation_chain.run(table=table)
                image_url = self.dalle_api.generate_image(image_caption)
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                attempts += 1
        return image_url