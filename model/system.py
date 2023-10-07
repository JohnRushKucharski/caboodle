'''A system of nodes and edges describing a water resources system.'''
from typing import Set, List

from model.data import REGISTRY
from model.node import Node, Tag

class System:
    '''A system of nodes and edges describing a water resources system.'''
    def __init__(self, nodes: List[Node], log_directory: str) -> None:
        self.nodes = nodes
        self.data_path = log_directory

    def outlet(self) -> Node:
        '''Finds the outlet node.

        Raises:
            NotImplementedError: If there is not exactly one outlet node.

        Returns:
            Node: The outlet node.
        '''
        outlets = tuple(node for node in self.nodes if node.tag == Tag.OUTLET)
        if len(outlets) != 1:
            raise NotImplementedError('Only one outlet is supported.')
        return outlets[0]

    def simulate(self, time_periods: int = 1) -> None:
        '''Simulate the system.'''
        for _ in range(time_periods):
            self.step_forward()
        for k, v in REGISTRY.items():
            v.flush(csv_path=f'{self.data_path}/{k}.csv')

    def step_forward(self) -> None:
        '''Step the system forward one time period.'''
        self.outlet().send()

def format_node_names(nodes: List[Node]) -> Set[Node]:
    '''Create unique names for nodes.'''
    names = []
    output = set()
    for node in nodes:
        i: int = 1
        name = node.name
        while name in names:
            name += str(i)
        names.append(name)
        node.name = name
        output.add(node)
    return output

# pylint: disable=line-too-long
# from typing import List, Set, Tuple
# from dataclasses import dataclass, field

# import networkx as nx

# from model.node import Tag, Node

# @dataclass
# class System:
#     nodes: Set[Node] = field(default_factory=set)
#     graph: nx.DiGraph = field(default_factory=nx.DiGraph)

    # def add_node(self, node: Node) -> None:
    #     '''Add a node to the system.'''
    #     self.graph.add_node(node)

    # def build_graph(self) -> None:
    #     # todo: test I don't mutated self.nodes
    #     nodes = tuple(self.nodes)
    #     recievers: Tuple[Node] = (node for node in nodes if node.tag == Tag.OUTLET)
    #     if len(outlets) != 1:
    #         raise NotImplementedError('Only one outlet is supported.')
    #     for receiver in recievers:
    #         senders: Set[Node] = receiver.senders()
    #         if not senders and receiver.tag != Tag.INFLOW:
    #             raise NotImplementedError(f'The node {receiver.name} is missing an inflow node.')
    #         for sender in senders:
    #             self.graph.add_edge(sender, receiver)


    #     if outlets := (node for node in nodes if node.tag == Tag.OUTLET):


    #     outlets = (node for node in nodes if node.tag == Tag.OUTLET)[0] if len(node for node in nodes if node.tag == Tag.OUTLET) == 1 else raise NotImplementedError('Only one outlet is supported.')
    #     if len(outlets) != 1:
    #         raise NotImplementedError('Only one outlet is supported.')



# def system_from_outlet(node: Node) -> List[Node]:
#     recievers: List[Node] =

# def graph_from_outlet(outlet: Node) -> System:
#     '''Return a system with nodes and edges from an outlet.'''
#     nodes: List[Node] = []
#     graph = nx.DiGraph()
#     if outlet.tag != Tag.OUTLET:
#         raise ValueError('The outlet must be an outlet node.')
#     names: Set[str] = {outlet.name}
#     recievers: Tuple[Node] = (outlet,)
#     for reciever in recievers:
#         senders: Set[Node] = reciever.senders()
#         if not senders and reciever.tag != Tag.INFLOW:
#             raise NotImplementedError(f'The node {reciever.name} is missing an inflow node.')
#         for sender in senders:
#             graph.add_edge(sender, reciever)
      