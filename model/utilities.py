'''Functional utilities for the model.'''

from enum import Enum
from typing import List, Tuple, Callable

import numpy as np

def is_not_negative(*args: float) -> bool:
    '''Tests if all arguments are not negative.

    Returns:
        bool: True if arguments are not negative, False otherwise.
    '''
    for x in args:  #pylint: disable=invalid-name
        if x < 0:
            return False
    return True

def is_positive(*args: float) -> bool:
    '''Tests if all arguments are positive.

    Returns:
        bool: True if arguments are positive, False otherwise.
    '''
    for x in args:  #pylint: disable=invalid-name
        if x <= 0:
            return False
    return True

def is_range(rng: Tuple[float, float]) -> bool:
    '''Tests if a range is valid.

    Returns:
        bool: True if range is valid, False otherwise.
    '''
    if len(rng) != 2:
        return False
    return rng[0] < rng[1]

def linear_function(slope: float = 0, intercept: float = 0) -> Callable[[float], float]:
    '''Returns a linear function of the form: f(x) = slope * x + intercept.'''
    def fx(x: float) -> float:  # pylint: disable=invalid-name
        return slope * x + intercept
    return fx

def exponential_function(base: float = 1, rate_of_change: float = 0) -> Callable[[float], float]:
    '''
    Returns an exponential function of the form: f(x) = base * (1 + rate_of_change) ** x.

    Arguments:
        base: float ~ initial value
        rate_of_change: float ~ exponential rate of growth or decay
    Returns:
        fx: Callable[[float], float] ~ exponential function
    '''
    def fx(x: float) -> float: #pylint: disable=invalid-name
        '''
        Arguments:
            x: float ~ independent variable
        Returns:
            y: float ~ dependent variable
        '''
        return base * (1 + rate_of_change) ** x
    return fx

def unit_sigmoid_function(k: float = 1) -> Callable[[float], float]:
    '''
    Returns a sigmoid function of the form: f(x) = 1 / (1 + ((1 / x) - 1) **k).

    Arguments:
        k: float ~ steepness of the curve
    Returns:
        fx: Callable[[float], float] ~ sigmoid function
    '''
    def fx(x: float) -> float:  #pylint: disable=invalid-name
        '''
        Arguments:
            x: float ~ independent variable
        Returns:
            y: float ~ dependent variable
        '''
        return 0 if x <= 0 else 1 / (1 + ((1 / x) - 1) ** k) if x < 1 else 1
    return fx

def expected_value(time_series: List[float], rate_of_depreciation: float = 0) -> float:
    '''
    Returns the expected value of a time series,
    given a constant rate of depreciation of information.

    Arguments:
        time_series: List[float] ~ time series of values
        rate_of_depreciation: float ~ discount rate
    Returns:
        expected_value: float ~ expected value
    '''
    @np.vectorize
    def partial_weight(t: int) -> float:    #pylint: disable=invalid-name
        '''
        Arguments:
            t: int ~ time period
        Returns:
            weight: float ~ weight of time period
        '''
        return (1 - rate_of_depreciation) ** t
    weights = partial_weight(np.arange(len(time_series) - 1, -1, -1))
    return np.dot(time_series, weights) / np.sum(weights)

class ReimannMethod(Enum):
    '''
    Enumeration of reimann sum methods.
    '''
    LEFT = 0
    RIGHT = 1
    MIDPOINT = 2
    TRAPEZOID = 3

def reimann_fx(fx: Callable[[float], float], #pylint: disable=invalid-name
               method: ReimannMethod = ReimannMethod.TRAPEZOID,
               n: int = 1) -> Callable[[Tuple[float, float]], float]: #pylint: disable=invalid-name
    '''
    Closure for reimann sum function.
    
    Arguments:
        fx: Callable[[float], float] ~ function to integrate
        method: ReimannMethod ~ reimann sum method
        n: int ~ number of subintervals
    
    Returns:
        reimann_sum: Callable[[Tuple[float, float]], float] ~ reimann sum function
    '''
    def closure_fx(interval: Tuple[float, float]) -> float:
        return reimann_sum(fx=fx, interval=interval, method=method, n=n)
    return closure_fx

def reimann_sum(fx: Callable[[float], float], interval: Tuple[float, float],
                method: ReimannMethod = ReimannMethod.TRAPEZOID, n: int = 100) -> float:
    #pylint: disable=invalid-name
    '''
    Computes the reimann sum of a function over an interval.
    
    Arguments:
        fx: Callable[[float], float] ~ function to integrate
        interval: Tuple[float, float] ~ interval over which to integrate
        method: ReimannMethod ~ reimann sum method
        n: int ~ number of subintervals
        
    Returns:
        reimann_sum: float ~ reimann sum
    '''
    if not is_range(interval):
        raise ValueError('Interval must be a valid range.')
    a, b = interval
    dx = (b - a) / n
    match method:
        case ReimannMethod.LEFT:
            return sum(fx(a + i * dx) for i in range(0, n)) * dx
        case ReimannMethod.RIGHT:
            return sum(fx(a + (i + 1) * dx) for i in range(0, n)) * dx
        case ReimannMethod.MIDPOINT:
            return sum(fx(a + (i + 0.5) * dx) for i in range(0, n)) * dx
        case ReimannMethod.TRAPEZOID:
            return (sum(fx(a + i * dx) for i in range(0, n)) +
                    sum(fx(a + (i + 1) * dx) for i in range(0, n))) * dx / 2
        case _:
            raise ValueError('Invalid method.')
