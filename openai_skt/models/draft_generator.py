import re
from typing import List

from modules import Draft, DraftPart

class DraftGeneratorInstance:
    def __init__(self, draft_chain=None) -> None:
        self.draft_chain = draft_chain

    def run(self, purpose:str=None, table:str=None, database=None) -> Draft:
        table_list = self.parse_table(table)
        draft = Draft(purpose=purpose, tables=table_list)
        for single_table in table_list:
            chunk_list, data_text = self.parse_database(database, query=single_table)
            single_draft = self.draft_chain.run(purpose=purpose, draft=draft.text, single_table=single_table, database=data_text, table=table)
            draft_part = DraftPart(text=single_draft, purpose=purpose, single_table=single_table, files=chunk_list)
            draft.add_draft_part(draft_part)
        return draft
    
    async def arun(self, purpose:str=None, table:str=None, database=None):
        # TODO: 수정필요
        draft = await self.draft_chain.arun(purpose=purpose, table=table, database=database)
        return draft
    
    def parse_database(self, database, query:str=None)->str:
        chunk_list = database.query(query=query)
        data_text = ''
        for idx, chunk in enumerate(chunk_list): # data is Chunk object
            data_text += f'{idx+1}. {chunk.data}\n'
        return chunk_list, data_text

    def parse_table(self, table:str=None)->List[str]:
        # 정규 표현식 패턴 사용
        table_list = re.split(r"\d+\.", table)[1:]  # 첫 번째 빈 문자열 제거

        # 앞 뒤 공백 제거
        table_list = [section.strip() for section in table_list]

        return table_list