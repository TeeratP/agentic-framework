from langgraph.graph import Graph, START, END
from agentic_framework.nodes.agent_node import AgentNode
from agentic_framework.nodes.decision_node import DecisionNode

class AgenticGraph(Graph):
    def __init__(self, start_node, end_nodes):
        super().__init__()
        
        self.start_node = start_node
        self.end_nodes = end_nodes
        
        self.registerd_node = set()
        self.prev_node = START
        
    def build_graph(self):
        self._build_graph(self.start_node, START)
        
    def _build_graph(self, node, prev_node):
        if node in self.registerd_node:
            return
        
        self.registerd_node.add(node)
        
        if isinstance(node, AgentNode):
            self.add_node(node, node.name)
            if isinstance(prev_node, DecisionNode): # normal case
                self.add_edge(prev_node, node.name)
            else: 
                pass # edge from decision node is already added in DecisionNode
            
            if node in self.end_nodes: 
                self.add_edge(node, END) # only case that create forward edge is when node is end node
            else:
                self._build_graph(node.child, node) # recursively build graph
            
        elif isinstance(node, DecisionNode):
            self.add_conditional_edges(prev_node, node) # node perform as function that return name of next node
            for choice in node.choices:
                self._build_graph(choice.child, node)