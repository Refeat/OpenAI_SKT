import re
from typing import List, Union

from langchain import LLMChain
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import BaseChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout_final_only import (
    FinalStreamingStdOutCallbackHandler,
)
from langchain.schema import AgentAction, AgentFinish, HumanMessage

from tools import DatabaseTool

# Set up a prompt template
class CustomPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    
    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])

        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]

class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

class QnAAgent:
    # TODO: Database 객체로 선언 안하는 방법이 있는지 생각
    def __init__(self, database, qna_prompt_path='../openai_skt/models/templates/qna_prompt_template.txt', verbose=False) -> None:
        with open(qna_prompt_path, 'r') as f:
            self.qna_prompt_template = f.read()
        
        self.database = database
        self.output_parser = CustomOutputParser()
        self.verbose = verbose
        self.tools = [DatabaseTool(database=self.database)]

        self.qna_prompt = CustomPromptTemplate(
            template=self.qna_prompt_template,
            tools=self.tools,
            # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
            # This includes the `intermediate_steps` variable because that is needed
            input_variables=["input", "intermediate_steps", "qna_history"]
        )

        self.llm = ChatOpenAI(temperature=0, verbose=self.verbose, callbacks=[FinalStreamingStdOutCallbackHandler()])
        self.qna_chain = LLMChain(llm=self.llm, prompt=self.qna_prompt, verbose=self.verbose, callbacks=[FinalStreamingStdOutCallbackHandler()])
        tool_names = [tool.name for tool in self.tools]
        self.agent = LLMSingleActionAgent(
            llm_chain=self.qna_chain, 
            output_parser=self.output_parser,
            stop=["\nObservation:"], 
            allowed_tools=tool_names
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=self.tools, verbose=self.verbose)

    def run(self, question, qna_history):
        input_dict = self.parse_input(question, qna_history)
        result = self.agent_executor.run(input_dict=input_dict)
        return result

    async def arun(self, question, qna_history):
        input_dict = self.parse_input(question, qna_history)
        result = await self.agent_executor.arun(input_dict=input_dict)
        return result
    
    def parse_input(self, question, qna_history):
        input_qna_history = qna_history[:2]
        input_dict = {'input': question, 'qna_history': input_qna_history}
        return input_dict