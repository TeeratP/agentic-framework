from agentic_framework.node import Node
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from typing import Literal, Union

class Choice:
    def __init__(self, name:str):
        self.name = name
        self.child = None
        
    def __gt__(self, other):
        """
        Return the other node so that the graph can be built in a chain.
        """
        self.child = other
        return other
        
class DecisionNode(Node):
    def __init__(self, 
                 name:str = 'decision_node', 
                 llm:str = None, 
                 node_prompt:str = "", 
                 choices: list[str] = []):
        
        assert node_prompt, "DecisionNode requires a node_prompt to be set."
        assert choices, "DecisionNode requires choices to be set."
        super().__init__(name, llm, node_prompt)
        self.choices_name = choices
        self.choices_created = False
        
    def _create_choices(self):
        class OutputModel(BaseModel):
            choice: Union[Literal[tuple(self.choices_name)]]
        self.llm = self.llm.with_structured_output(OutputModel)
        self.child = None
        self.choices = [Choice(name) for name in self.choices_name]
        self.choices_created = True
        
    def __call__(self, state):
        if self.llm is None:
            raise ValueError(f"{self.name} requires a LLM to be set before call.")
        
        if not self.choices_created:
            self._create_choices()
        
        message_w_prompt = state['message']
        message_w_prompt.append(SystemMessage(content=self.node_prompt))
        response = self.llm.invoke(message_w_prompt) # use llm to decide which choice to make
        if response['choice'] in self.choices_name:
            for choice in self.choices:
                if response['choice'] == choice.name:
                    try:
                        return choice.child.name
                    except AttributeError:
                        raise ValueError(f"Choice {response['choice']} does not have a child. Please create an edge from this choice to another node. For example: `decision_node['abc'] > other_node`")
        else:
            raise ValueError(f"Choice {response['choice']} not found in choices")
        
    def __gt__(self, other):
        raise ValueError("You must create edge from choices to other nodes. For example: `decision_node['choice'] > other_node`")
    
    def __getitem__(self, key):
        for choice in self.choices:
            if key == choice.name:
                return choice # return the choice object
        raise ValueError(f"Choice {key} not found in choices.")