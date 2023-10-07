'''
Reservoir objects.
'''
import math
import copy
from enum import Enum, StrEnum
from dataclasses import dataclass
from typing import Self, List, Tuple, Dict, NamedTuple, Callable, Protocol, Any

import numpy as np

from model.asset import Asset

ReleaseRange = NamedTuple('ReleaseRange', [('min', float), ('max', float)])

class Outlet(Protocol):
    '''Template for an outlet at a reservoir.'''
    name: str
    location: float
    design_range: ReleaseRange
    _release_function: Callable[[Self, float], ReleaseRange]

    def release_range(self, volume: float) -> ReleaseRange:  # type: ignore
        '''Returns the minumum and maximum possible release given a volume of water in reservoir and condition of the outlet.'''  #pylint: disable=line-too-long

    # def __eq__(self, other: object) -> bool:
    #     if not isinstance(other, type(self)):
    #         return False
    #     return (self.name == other.name and
    #             self.location == other.location and
    #             self.design_range == other.design_range and
    #             self._release_function == other._release_function)

    # def __hash__(self) -> int:
    #     return hash((self.name, self.location, self.design_range, self._release_function))

def basic_gate(outlet: 'Outlet', volume: float):
    '''Return the release range from a given outlet and reservoir volume.'''
    volume_over = volume - outlet.location
    # if volume < outlet.location max release is 0
    if volume_over < 0:
        return ReleaseRange(0.0, 0.0)
    return ReleaseRange(min=min(outlet.design_range.min, volume_over),
                        max=min(volume_over, outlet.design_range.max))

@dataclass
class BasicOutlet(Outlet):
    '''A basic gate or other release outlet at a reservoir.'''
    name: str = ''
    '''The name of the outlet.'''
    location: float = 0.0
    '''The location of the outlet in the reservoir. Same units as reservoir volume.'''
    design_range: ReleaseRange = ReleaseRange(0.0, np.inf)
    '''Min and max release in non-failure state. Same units as reservoir volume.'''
    _release_function: Callable[[Self, float], ReleaseRange] = basic_gate

    def release_range(self, volume: float) -> ReleaseRange:
        '''Returns  the minumum and maximum possible release given a volume of water in reservoir and condition of gate.'''  # pylint: disable=line-too-long
        return self._release_function(self, volume)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BasicOutlet):
            return False
        return (self.name == other.name and
                self.location == other.location and
                self.design_range == other.design_range and
                self._release_function == other._release_function)

    def __hash__(self) -> int:
        return hash((self.name, self.location, self.design_range, self._release_function))

class FailureState(Enum):
    '''The state of a reservoir failure.'''
    NONE = 0
    '''No failure.'''
    OPEN = 1
    '''Outlet failed in open position, releases without control.'''
    CLOSED = 2
    '''Outlet failed in closed position, cannot make releases.'''

def basic_gate_with_failure(outlet: 'OutletAsset', volume: float) -> ReleaseRange:
    '''Return the failure modified release range from an outlet and reservoir volume.'''
    no_failure_release = basic_gate(outlet, volume)
    match outlet.failure_state:
        case FailureState.NONE:
            return no_failure_release
        case FailureState.OPEN:
            return ReleaseRange(no_failure_release.max, no_failure_release.max)
        case FailureState.CLOSED:
            return ReleaseRange(0.0, 0.0)
        case _:
            raise NotImplementedError(f'{outlet.failure_state} failure state not implemented.')

def update_condition(outlet: 'OutletAsset',
                     asset_value: float, volume: float) -> 'OutletAsset':
    '''
    Updates failure state of an outlet given its asset value and reservoir volume.
    
    Args:
        outlet (OutletAsset): The outlet to update.
        asset_value (float): The asset value of the outlet.
        volume (float): The volume of water in the reservoir.
    
    Returns:
        OutletAsset: The updated outlet.
    '''
    pval: float = outlet.asset.portion_remaining(asset_value)
    if pval > 0.0 or outlet.failure_state is not FailureState.NONE:
        return outlet
    # else:
    # pylint: disable=protected-access
    if volume <= outlet.location:
        # assumed to break in closed position
        return OutletAsset(outlet.asset, outlet.name, outlet.location,
                           FailureState.CLOSED, outlet.design_range, outlet._release_function)
    # assumed to break in operating position
    return OutletAsset(outlet.asset, outlet.name, outlet.location,
                       FailureState.OPEN, outlet.design_range, outlet._release_function)

StateAssessment = NamedTuple('StateAssessment', [('probability', float), ('outlet', Outlet)])

@dataclass
class OutletAsset(Outlet):
    '''A gate or other release outlet at a reservoir.'''
    asset: Asset
    '''Models outlet value and depreciation.'''
    name: str = ''
    '''The name of the outlet.'''
    location: float = 0.0
    '''The location of the outlet in the reservoir. Same units as reservoir volume.'''
    failure_state: FailureState = FailureState.NONE
    '''The state of the outlet failure.'''
    design_range: ReleaseRange = ReleaseRange(0.0, np.inf)
    '''Min and max release in non-failure state. Same units as reservoir volume.'''
    _release_function: Callable[[Self, float], ReleaseRange] = basic_gate_with_failure
    '''Function to calculate release range given outlet and reservoir volume.'''
    _failure_function: Callable[[Self, float, float], Self] = update_condition

    def release_range(self, volume: float) -> ReleaseRange:
        '''Returns  the minumum and maximum possible release given a volume of water in reservoir and condition of gate.'''  # pylint: disable=line-too-long
        return self._release_function(self, volume)

    def assess_condition(self, estimated_asset_value: float, volumes: List[float]) -> List[StateAssessment]:  # pylint: disable=line-too-long
        '''Returns a list of possible outlet failure states and their probabilities given an estimated asset value.''' # pylint: disable=line-too-long
        states: Dict[FailureState, StateAssessment] = {}
        dp: float = 1 / len(volumes)  # always floting point division # pylint: disable=invalid-name
        for volume in volumes:
            state = self._failure_function(self, estimated_asset_value, volume)
            states[state.failure_state] = StateAssessment(states[state.failure_state].probability + dp, state)  # pylint: disable=line-too-long
        return list(states.values())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OutletAsset):
            return False
        return (self.asset == other.asset and
                self.name == other.name and
                self.location == other.location and
                self.failure_state == other.failure_state and
                self.design_range == other.design_range and
                self._release_function == other._release_function and
                self._failure_function == other._failure_function)

    def __hash__(self) -> int:
        return hash((self.asset, self.name, self.location, self.failure_state,
                     self.design_range, self._release_function, self._failure_function))

def outlet_index_sorter(sorting_attribute: str = 'location', reverse: bool=True) -> Callable[[Tuple[Outlet,...]], Tuple[int,...]]:  # pylint: disable=line-too-long
    '''
    Sorts a tuple of outlets by a named attribute.
    Default sorts outlets by location in descending order.

    Args:
        sorting_attribute (str, optional): name of attribute to sort on. Defaults to 'location'.
        reverse (bool, optional): reverse sort order. Defaults to True.

    Returns:
        Tuple[int,...]: The list of the outlets indices in sorted order.
    '''
    def index_sorter(outlets: Tuple[Outlet,...]) -> Tuple[int,...]:
        sorted_indices: List[int] = []
        _outlets = copy.deepcopy(list(outlets))
        sorted_outlets = sorted(_outlets,
                                key=lambda outlet: getattr(outlet, sorting_attribute),
                                reverse=reverse)
        for sorted_outlet in sorted_outlets:
            for i, outlet in enumerate(_outlets):
                if sorted_outlet == outlet:
                    sorted_indices.append(i)
                    #outlets.pop(i)
                    break
        return tuple(sorted_indices)
    return index_sorter

def outlet_sorter(outlets: Tuple[Outlet,...],
                  sorting_attribute: str = 'location') -> Tuple[Outlet,...]:
    '''Sorts a tuple of outlest by a named attribute.

    Args:
        outlets (Tuple[Outlet,...]): outlets to sort.
        sorting_attribute (str, optional): name of attribute to sort on. Defaults to 'location'.

    Returns:
        Tuple[Outlet,...]: The sorted outlets.
    '''
    sorted_outlets: List[Outlet] = []
    sorted_indices: Tuple[int,...] = outlet_index_sorter(sorting_attribute)(outlets)
    for i in sorted_indices:
        sorted_outlets.append(outlets[i])
    return tuple(sorted_outlets)

def format_outlets(outlets: Tuple[Outlet,...]) -> Tuple[Outlet,...]:
    '''
    Modifies input tuple with unique names. Sorts output tuple by location, and unique name.
        new_name = '<old_name><duplicate_number>@<location>'
    
    Args:
        outlets (Tuple[Outlet,...]): outlets to format.
        
    Returns:
        Tuple[Outlet,...]: The formatted outlets.
    '''
    names = set()
    output: List[Outlet] = []
    for outlet in outlets:
        i: int = 1
        location: str = f'@{str(math.floor(outlet.location))}'
        name: str = f'{outlet.name}{i}{location}' if outlet.name else f'outlet{i}{location}'
        while name in names:
            i += 1
            name = name[:name.index('@') - 1] + str(i) + name[name.index('@'):]
        names.add(name)
        outlet = copy.deepcopy(outlet)
        outlet.name = name
        output.append(outlet)
    sorted_output = sorted(output, key=lambda outlet: (outlet.location, outlet.name))
    for i, outlet in enumerate(sorted_output):
        if outlet.name[outlet.name.index('@') - 1] == '1':
            name = outlet.name[:outlet.name.index('@') - 1] + outlet.name[outlet.name.index('@'):]
            outlet.name = name
    return tuple(sorted_output)

class OutputTag(StrEnum):
    '''The type of output from a reservoir.'''
    INFLOW = 'inflow'
    '''The inflow to the reservoir.'''
    STORAGE = 'storage'
    '''Reservoir storage.'''
    OUTLFLOW = 'outflow'
    '''Outflow from the reservoir.'''
    SPILLED = 'spilled'
    '''Uncontrolled release made by reservoir exceeding capacity.'''
    OTHER = 'other'
    '''Other output from the reservoir.'''

def passive_management(reservoir: 'Reservoir',
                       sorter: Callable[[Tuple[Outlet,...]], Tuple[int,...]] = outlet_index_sorter()) -> Callable[[float], Tuple[float,...]]:  # pylint: disable=line-too-long
    '''Returns storage and releases from a reservoir with passive management.
    
    Args:
        # pylint: disable=line-too-long
        reservoir (Reservoir): The reservoir to operate.
        sorter (Callable[[List[Outlet]], List[int]], optional): Function that sorts outlet indices in operating order. Defaults to outlet_index_sorter().
        
    Returns:
        Callable[[float, float], List[NamedOutput]]: 
            A function that returns storage and releases from a reservoir given inflow and storage.
    '''
    def operate(volume: float) -> Tuple[float,...]:
        '''Returns storage and releases from a reservoir given a starting volume.

        Args:
            volume (float): Volume of water to manage at beginning of timestep.
                volume = previous_storage + inflow.

        Returns:
            Tuple[float,...]: Outflow, spill and storage volumes in order specified in reservoir.outputs. # pylint: disable=line-too-long
        '''
        output: List[float] = []
        release = 0.0
        order: Tuple[int,...] = sorter(reservoir.outlets)
        for idx in order:
            release = reservoir.outlets[idx].release_range(volume).max
            output.append(release)
            volume -= release
        store, spill = min(volume, reservoir.capacity), max(0.0, volume - reservoir.capacity)
        output.append(spill)
        output.append(store)
        return tuple(output)
    return operate

class Reservoir:
    '''A reservoir.'''
    def __init__(self, name: str = '',
                 capacity: float = 1.0,
                 outlets: None | Tuple[Outlet] = None,
                 operations_fx: Callable[[Self], Callable[..., Tuple[float,...]]] = passive_management) -> None:  # pylint: disable=line-too-long
        self.name = name
        self.capacity = capacity
        self.outlets = format_outlets(outlets) if outlets else format_outlets((BasicOutlet(location=1.0),)) # pylint: disable=line-too-long
        self.output_headers = tuple([(outlet.name, OutputTag.OUTLFLOW) for outlet in self.outlets] + [(OutputTag.SPILLED.value, OutputTag.SPILLED), (OutputTag.STORAGE.value, OutputTag.STORAGE)])  # pylint: disable=line-too-long
        '''Describes the outputs produced by the oeprations function.'''
        self.__operations = operations_fx(self)

    def operate(self, inputs: Any) -> Tuple[float,...]:
        '''
        Returns outflows, spill and storage from a reservoir given inputs.
        
        Args:
            inputs (Any): inputs to the reservoir operations function.
            
        Returns:
            Tuple[float,...]: outflows, spill and storage from a reservoir in order defined by reservoir.outputs. # pylint: disable=line-too-long
        '''
        return self.__operations(inputs)
