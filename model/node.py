'''
System nodes.
'''
#TODO: add time-warped nodes.
# by adding a function that breaks recieve into multiple time steps.
# time warp should be a decorator that wraps the recieve function.
# it may be conditional on recieve, external data, or a constant time warp.
#TODO: maybe add performance nodes.
# these would be nodes with an objective function that do not alter the system.
#TODO: add transform/transfer nodes.
# these should be nodes that convert floating point numbers in to smaller integer values for gaming.
# they should wrap a node, like the data nodes do.

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Self, Protocol, Callable, Any

from model.data import Log, logger
from model.reservoir import Reservoir

class Tag(str, Enum):
    '''Types of system nodes.'''
    INFLOW = 'inflow'
    '''Upstream most node, creates new inflows.'''
    STORAGE = 'storage'
    '''Accept upstream inflow, sends flow downstream, can store water.'''
    TRANSFER = 'transfer'
    '''Accept upstream inflow, sends flow downsteam, used for aggregation or rescaling flows.'''  # pylint: disable=line-too-long
    PERFORMANCE = 'performance'
    '''Accept upstream inflow, sends flow downstream, computes performance metrics, does not alter the system.'''  # pylint: disable=line-too-long
    OUTFLOW = 'outflow'
    '''Accept upstream inflow that can be diverted out of the system.'''
    OUTLET = 'outlet'
    '''Downstream most node.'''

class Node(Protocol):
    '''A node in a system.'''
    tag: Tag
    name: str
    #log: Optional[Log] = None

    '''The type of node.'''
    def senders(self) -> Set[Self]:  # type: ignore
        '''Return all nodes that send flow to this node.'''
    def receive(self) -> float:  # type: ignore
        '''Return the flow received from all senders.'''
    def send(self) -> float:  # type: ignore
        '''Return the flow to send to downstream senders.'''
    @property
    def output_headers(self) -> Tuple[str]:  # type: ignore
        '''Returns the headers for output data.'''
    def output_function(self) -> Callable[..., Any]:  # type: ignore
        '''Returns the output function for this node.'''

    # def __eq__(self, other: object) -> bool:
    #     if not isinstance(other, Node):
    #         return False
    #     return self.tag == other.tag and self.name == other.name

    # def __hash__(self) -> int:
    #     return hash((self.tag, self.name))

class Reciever(Protocol):
    '''A node that receives flow.'''
    def add_sender(self, sender: Node) -> None:
        '''Add a node that sends flow to this node.'''
    def remove_sender(self, sender: Node) -> None:
        '''Remove a node that sends flow to this node.'''

class Inflow(Node):
    '''A node that provides inflows from a dataset.'''
    def __init__(self, data: List[float], name: str = '', starting_position: int = 0) -> None:
        # logger: Callable[..., Any] = logger_factory()
        self.tag: Tag = Tag.INFLOW
        self.name: str = name if name else self.tag.value
        self.data: List[float] = data
        #self.logger = logger
        self.__timestep = starting_position

    def senders(self) -> Set[Self]:
        return set()

    def receive(self) -> float:
        self.__timestep += 1
        return self.data[self.__timestep - 1]

    @logger
    def send(self) -> float:
        return self.receive()

    def reset(self) -> None:
        '''Reset the inflow to the starting timestep.'''
        self.__timestep = 0

    @property
    def output_headers(self) -> Tuple[str]:
        return (self.tag.value,)

    def output_function(self) -> Callable[..., Any]:
        return self.send

@dataclass
class Storage(Node, Reciever):
    '''A node that accepts inflows, stores water, and sends flow downstream.

    Args:
        Node (Protocol): A node in a system.
        Reciever (Protocol): A node that receives flow.
    '''
    volume: float = 0
    name: str = Tag.STORAGE.value
    senders: Set[Node] = field(default_factory=set)
    tag: Tag = field(init=False, default=Tag.STORAGE)

    reservoir: Reservoir = field(default_factory=Reservoir)

    # def __post_init__(self) -> None:
    #     self.output_headers = (self.tag.value, *self.reservoir.output_headers)  # type: ignore

    def add_sender(self, sender: Node) -> None:
        '''Add a node that sends flow to this node.'''
        if sender in self.senders:
            raise ValueError(f'Redundant, {sender} already sends flow to {self}.')
        self.senders.add(sender)

    def remove_sender(self, sender: Node) -> None:
        '''Remove a node that sends flow to this node.'''
        self.senders.remove(sender)

    def receive(self) -> float:
        '''Return the flow received from all senders.'''
        return sum(sender.send() for sender in self.senders)

    @logger
    def update(self) -> Tuple[float,...]:
        '''Intermediary between receive and send to gather and log data.'''
        inflow = self.receive()
        output = self.reservoir.operate(inflow + self.volume)
        self.volume = self.storage(output)
        return (inflow,) + output

    def send(self,*args, **kwargs) -> float:
        '''Return the flow to send to downstream senders.'''
        outputs = self.update(*args, **kwargs)
        return self.outflows(outputs)

    def storage(self, output: Tuple[float,...]) -> float:
        '''Returns the storage from a reservoir output.'''
        return output[-1]

    def outflows(self, output: Tuple[float,...]) -> float:
        '''Returns the outflows from a reservoir output.'''
        return sum(output[1:-2])

    @property
    def output_headers(self) -> Tuple[str]:
        return (Tag.INFLOW.value, *self.reservoir.output_headers)  # type: ignore

    def output_function(self) -> Callable[..., Any]:
        return self.update

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Storage):
            return False
        return (self.tag == __value.tag and
                self.name == __value.name and
                self.senders == __value.senders and
                self.reservoir == __value.reservoir)

    def __hash__(self) -> int:
        return hash((self.tag, self.name, self.reservoir))

@dataclass
class Outlet(Node, Reciever):
    '''Node that sends flow out of the system.'''
    name: str = Tag.OUTLET.value
    senders: Set[Node] = field(default_factory=set)
    '''Nodes that send flow to this node.'''
    tag: Tag = field(init=False, default=Tag.OUTLET)

    def add_sender(self, sender: Node) -> None:
        '''Add a node that sends flow to this node.'''
        if sender in self.senders:
            raise ValueError(f'{sender} already sends flow to {self}.')
        self.senders.add(sender)

    def remove_sender(self, sender: Node) -> None:
        '''Remove a node that sends flow to this node.'''
        self.senders.remove(sender)

    def receive(self) -> float:
        '''Return the flow received from all senders.'''
        return sum(sender.send() for sender in self.senders)

    @logger
    def send(self) -> float:
        '''Return the flow to send to downstream senders.'''
        return self.receive()

    @property
    def output_headers(self) -> Tuple[str]:
        return (self.tag.value,)

    def output_function(self) -> Callable[..., Any]:
        return self.send

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Outlet):
            return False
        return (self.tag == __value.tag and
                self.name == __value.name and
                self.senders == __value.senders)

    def __hash__(self) -> int:
        return hash((self.tag, self.name))

class DataNode(Node):
    '''Logging support.'''
    def __init__(self, node: Node, logpath: str) -> None:
        self.node = node
        self.tag = node.tag
        self.name = node.name
        self.log = Log(logpath, data_headers=node.output_headers)

    def send(self) -> float: # type: ignore
        self.node.send(log=self.log) # type: ignore
