from typing import List

class KeywordsGeneratorInstance:
    def __init__(self, keywords_chain=None) -> None:
        self.keywords_chain = keywords_chain

    def run(self, purpose:str=None, table:str=None) -> List[str]:
        result = self.keywords_chain.run(purpose=purpose, table=table)
        keywords = self.parse_keywords(result)
        return keywords

    async def arun(self, purpose:str=None, table:str=None) -> List[str]:
        result = await self.keywords_chain.arun(purpose=purpose, table=table)
        keywords = self.parse_keywords(result)
        return keywords
    
    def parse_keywords(self, result:str) -> List[str]:
        keywords = result.split(", ")
        return keywords