import re
from typing import List, Union

from langchain import LLMChain, OpenAI
from langchain.agents import AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI

# Set up a prompt template
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[BaseTool]

    def format(self, **kwargs) -> str:
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
        return self.template.format(**kwargs)

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
            raise OutputParserException(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
    
class DraftEditAgent:
    def __init__(self, tools, draft_edit_prompt_path='../openai_skt/models/templates/draft_edit_prompt_template.txt', verbose=False, model='gpt-3.5-turbo-16k') -> None:
        with open(draft_edit_prompt_path, 'r') as f:
            self.draft_edit_prompt_template = f.read()
        
        self.output_parser = CustomOutputParser()
        self.verbose = verbose

        self.draft_edit_prompt = CustomPromptTemplate(
            template=self.draft_edit_prompt_template,
            tools=tools,
            # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
            # This includes the `intermediate_steps` variable because that is needed
            input_variables=["user_query", "draft", "intermediate_steps"]
        )

        self.llm = ChatOpenAI(temperature=0, verbose=self.verbose)
        self.draft_edit_chain = LLMChain(llm=self.llm, prompt=self.draft_edit_prompt, verbose=self.verbose)
        tool_names = [tool.name for tool in tools]
        self.agent = LLMSingleActionAgent(
            llm_chain=self.draft_edit_chain, 
            output_parser=self.output_parser,
            stop=["\nObservation:"], 
            allowed_tools=tool_names
        )

    def run(self, tools, draft:str, query):
        input_dict = self.parse_input(draft, query)
        agent_executor = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=tools, verbose=self.verbose)
        result = agent_executor.run(input_dict)
        return result

    async def arun(self, tools, draft, query):
        input_dict = self.parse_input(draft, query)
        agent_executor = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=tools, verbose=self.verbose)
        result = await agent_executor.arun(input_dict)
        return result
    
    def parse_input(self, draft, query):
        input_dict = {'user_query': query, 'draft': draft}
        return input_dict