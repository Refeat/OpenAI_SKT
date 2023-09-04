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
        delimiters = ['\n', ',']
        special_chars = ['"', "'"]
        lines = result.split(delimiters[0])

        # Then split each line by the subsequent delimiters
        keywords = []
        for line in lines:
            line = line.strip()  # Remove leading and trailing whitespace
            if line:  # Check ensures no empty strings are included
                temp = [line]
                for delimiter in delimiters[1:]:
                    temp = [element.split(delimiter) for element in temp]
                    temp = [item.strip() for sublist in temp for item in sublist]
                keywords.extend(temp)


        # Replace special characters
        for i, keyword in enumerate(keywords):
            for char in special_chars:
                keyword = keyword.replace(char, '')
            keywords[i] = keyword

        return keywords