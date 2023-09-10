from models.llm import TableChain

class TableGeneratorInstance:
    def __init__(self, verbose=False) -> None:
        self.table_chain = TableChain(verbose=verbose)

    def run(self, purpose:str=None):
        table = self.table_chain.run(purpose=purpose)
        return table

    async def arun(self, purpose:str=None):
        table = await self.table_chain.arun(purpose=purpose)
        return table