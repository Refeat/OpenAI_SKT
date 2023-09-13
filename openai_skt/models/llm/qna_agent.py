import re
import sys
from typing import List, Union, Optional, Dict, Any

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout_final_only import (
    FinalStreamingStdOutCallbackHandler,
)

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
            # print(f"Could not parse LLM output: `{llm_output}`")
            # return
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
    
class CustomStreamingStdOutCallbackHandler(FinalStreamingStdOutCallbackHandler):
    """Callback handler for streaming in agents.
    Only works with agents using LLMs that support streaming.

    The output will be streamed until "<END" is reached.
    """

    def __init__(
        self,
        *,
        answer_prefix_tokens: Optional[List[str]] = None,
        strip_tokens: bool = True,
        stream_prefix: bool = False,
        queue,
    ) -> None:
        """Instantiate EofStreamingStdOutCallbackHandler.

        Args:
            answer_prefix_tokens: Token sequence that prefixes the anwer.
                Default is ["Final", "Answer", ":"]
            end_of_file_token: Token that signals end of file.
                Default is "END"
            strip_tokens: Ignore white spaces and new lines when comparing
                answer_prefix_tokens to last tokens? (to determine if answer has been
                reached)
            stream_prefix: Should answer prefix itself also be streamed?
        """
        super().__init__(
            answer_prefix_tokens=answer_prefix_tokens,
            strip_tokens=strip_tokens,
            stream_prefix=stream_prefix,
        )
        self.queue = queue

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""

        # Remember the last n tokens, where n = len(answer_prefix_tokens)
        self.append_to_last_tokens(token)
        # Check if the last n tokens match the answer_prefix_tokens list ...
        if self.check_if_answer_reached():
            self.answer_reached = True
            if self.stream_prefix:
                for t in self.last_tokens:
                    sys.stdout.write(t)
                sys.stdout.flush()
            return

        # ... if yes, then print tokens from now on
        if self.answer_reached:
            # sys.stdout.write(token)
            # sys.stdout.flush()
            self.queue.append(token)
    
class QnAAgent:
    def __init__(self, tools, qna_prompt_path='../openai_skt/models/templates/qna_prompt_template.txt', verbose=False, model='gpt-3.5-turbo-16k') -> None:
        with open(qna_prompt_path, 'r') as f:
            self.qna_prompt_template = f.read()
        
        self.output_parser = CustomOutputParser()
        self.verbose = verbose

        self.qna_prompt = CustomPromptTemplate(
            template=self.qna_prompt_template,
            tools=tools,
            # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
            # This includes the `intermediate_steps` variable because that is needed
            input_variables=["input", "qna_history", "intermediate_steps"]
        )

        self.llm = ChatOpenAI(model=model, temperature=0, verbose=self.verbose, streaming=True)
        self.qna_chain = LLMChain(llm=self.llm, prompt=self.qna_prompt, verbose=self.verbose)
        tool_names = [tool.name for tool in tools]
        self.agent = LLMSingleActionAgent(
            llm_chain=self.qna_chain, 
            output_parser=self.output_parser,
            stop=["\nObservation:"], 
            allowed_tools=tool_names
        )

    def run(self, tools, question, qna_history, queue):
        input_dict = self.parse_input(question, qna_history)
        agent_executor = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=tools, verbose=self.verbose)
        result = agent_executor.run(input_dict, callbacks=[CustomStreamingStdOutCallbackHandler(queue=queue)])
        return result

    async def arun(self, tools, question, qna_history):
        input_dict = self.parse_input(question, qna_history)
        agent_executor = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=tools, verbose=self.verbose)
        result = await agent_executor.arun(input_dict)
        return result
    
    def parse_input(self, question, qna_history):
        input_qna_history = qna_history[-2:] # List[List[str]]
        input_qna_history = ''
        for single_chat in input_qna_history:
            input_qna_history += f'User: {single_chat[0]}'
            input_qna_history += f'AI: {single_chat[1]}'
        input_dict = {'input': question, 'qna_history': input_qna_history}
        return input_dict