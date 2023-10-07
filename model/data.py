'''Supports data logging.'''
import csv
from typing import List, Tuple, Dict, Callable, Any
from dataclasses import dataclass, field

# from model.node import Node

@dataclass
class Log:
    '''
    Stores data for a log file.
    '''
    csv_path: str = ''
    data: List[Any] = field(default_factory=list)
    data_headers: Tuple[str] = field(default_factory=tuple)

    def flush(self, csv_path: str) -> None:
        '''Write the data to a log file.'''
        with open(csv_path, 'w', newline='', encoding='utf-8') as log_file:
            writer = csv.writer(log_file)
            writer.writerow(self.data_headers)
            for row in self.data:
                if isinstance(row, (tuple, list)):
                    writer.writerow(row)
                else:
                    writer.writerow((row,))

def logger(function: Callable[...,Any]) -> Callable[..., Any]:
    '''Logging decorator that wraps func (i.e. Reservoir.operate()) and stores the output.'''
    is_initialized: bool = False
    def wrapper(*args, log: Log = Log(), **kwargs):
        output = function(*args, **kwargs)
        if not is_initialized:
            log.data_headers = args[0].output_headers
            REGISTRY[args[0].name] = log
        log.data.append(output)
        return output
    return wrapper

# def logger_factory(log: Log = Log()) -> Callable[..., Any]:
#     '''Returns a logging decorator with a specific log.'''
#     def _logger(function: Callable[...,Any]) -> Callable[..., Any]:
#         '''Logging decorator that wraps func (i.e. Reservoir.operate()) and stores the output.'''
#         def wrapper(*args, **kwargs):
#             output = function(*args, **kwargs)
#             if log:
#                 log.data.append(output)
#             return output
#         return wrapper
#     return _logger

REGISTRY: Dict[str, Log]  = {}
