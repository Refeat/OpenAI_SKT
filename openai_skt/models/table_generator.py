class TableGeneratorInstance:
    def __init__(self, table_chain=None) -> None:
        self.table_chain = table_chain

    def run(self, purpose:str=None):
        table = self.table_chain.run(purpose=purpose)
        return table

    async def arun(self, purpose:str=None):
        table = await self.table_chain.arun(purpose=purpose)
        return table