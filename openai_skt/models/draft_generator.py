from typing import List

class DraftGeneratorInstance:
    def __init__(self, database=None, draft_generate_chain=None) -> None:
        self.database = database
        self.draft_generate_chain = draft_generate_chain

    def run(self, purpose:str=None, keywords:List[str]=None):
        draft = self.draft_generate_chain.run(purpose=purpose, keywords=keywords, database=self.database)
        return draft
    
    async def arun(self, purpose:str=None, keywords:List[str]=None):
        draft = await self.draft_generate_chain.arun(purpose=purpose, keywords=keywords, database=self.database)
        return draft