class KeywordsGeneratorInstance:
    def __init__(self, keywords_chain=None) -> None:
        self.keywords_chain = keywords_chain

    def run(self, purpose:str=None):
        keywords = self.keywords_chain.run(purpose=purpose)
        return keywords

    async def arun(self, purpose:str=None):
        keywords = await self.keywords_chain.arun(purpose=purpose)
        return keywords