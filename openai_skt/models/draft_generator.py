import re
import time
from typing import List

from modules import Draft, DraftPart
from models.llm import DraftChain

class DraftGeneratorInstance:
    def __init__(self, verbose=False, draft_chain=None) -> None:
        self.draft_chain = draft_chain
        if draft_chain == None:
            self.draft_chain = DraftChain(verbose=verbose)

    def run(self, purpose:str=None, table:str=None, database=None, draft_id=None, queue=None) -> Draft:
        table_list = self.parse_table(table)
        draft = Draft(draft_id=draft_id, purpose=purpose, tables=table_list)
        for single_table in table_list:
            chunk_list, data_text = self.parse_database(database, query=single_table)
            single_draft = self.draft_chain.run(purpose=purpose, draft=draft.text, single_table=single_table, database=data_text, table=table, queue=queue)
            draft_part = DraftPart(text=single_draft, single_table=single_table, files=chunk_list)
            draft.add_draft_part(draft_part)
        return draft
    
    async def arun(self, purpose:str=None, table:str=None, database=None, draft_id=None):
        # TODO: 수정필요
        draft = await self.draft_chain.arun(purpose=purpose, table=table, database=database)
        return draft
    
    def parse_database(self, database, query:str=None)->str:
        chunk_list = database.query(query=query)
        data_text = ''
        for idx, chunk in enumerate(chunk_list): # data is Chunk object
            data_text += f'{idx+1}. {chunk.data}\n'
        return chunk_list, data_text

    def parse_table(self, table:str=None) -> List[str]:
        table_list = re.split(r"(\d+\.)", table)[1:]  # 첫 번째 빈 문자열 제거

        # 숫자와 내용을 합침
        table_list = [table_list[i] + table_list[i+1] for i in range(0, len(table_list), 2)]

        return table_list