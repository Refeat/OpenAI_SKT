import datetime

from langchain.tools import BaseTool

class TimeTool(BaseTool):
    name = "Time Tool"
    description = "Tool to get current time. There is no input"
    
    def __init__(self) -> None:
        super().__init__()

    def _run(self, query=None) -> str:
        # 현재 시간 출력
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f'Current time: {current_time}'

    async def _arun(self, query=None) -> str:
        # 현재 시간 출력 (비동기 방식이지만, datetime은 동기식이므로 그대로 사용)
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f'Current time: {current_time}'
