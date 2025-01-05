from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, name, llm=None, node_prompt = ""):
        self.name = name
        self.llm = llm
        self.node_prompt = node_prompt

    @abstractmethod
    def __call__(self, *args, **kwargs):
        if self.llm is None:
            raise ValueError("ChatNode requires a LLM to be set.")
        pass
    
    def set_llm(self, llm):
        self.llm = llm