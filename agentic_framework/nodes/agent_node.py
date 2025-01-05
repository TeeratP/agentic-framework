from agentic_framework.node import Node
from langchain_core.messages import SystemMessage

class AgentNode(Node):
    def __init__(self, 
                 name:str = 'agent_node', 
                 llm:str = None, 
                 node_prompt:str = "you are a helpful assistant"):
        super().__init__(name, llm, node_prompt)
        
    def __call__(self, state):
        if self.llm is None:
            raise ValueError(f"{self.name} requires a LLM to be set before call.")
        
        message_w_prompt = state['message']
        message_w_prompt.append(SystemMessage(content=self.node_prompt))
        response = self.llm.invoke(message_w_prompt)
        new_state = state
        new_state['message'].append(response)
        return new_state
    
    def __gt__(self, other):
        """
        Create edge from this node to another node.
        Return the other node so that the graph can be built in a chain.
        """
        self.child = other
        return other