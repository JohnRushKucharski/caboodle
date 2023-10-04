'''Supports data logging.'''
import csv
from typing import List, Tuple, Callable, Any
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

    def flush(self) -> None:
        '''Write the data to a log file.'''
        with open(self.csv_path, 'wb') as log_file:
            writer = csv.writer(log_file)
            for row in self.data:
                writer.writerows(row)

def logger(function: Callable[...,Any]):
    '''Logging decorator that wraps func (i.e. Reservoir.operate()) and stores the output.'''
    def wrapper(*args, log: None|Log = Log(), **kwargs):
        output = function(*args, **kwargs)
        if log:
            log.data.append(output)
        return output
    return wrapper
