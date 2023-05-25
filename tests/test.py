import inspect
import re
from typing import Any, List, Tuple
getcallargs = inspect.getcallargs

class MyClass:
    def __init__(self, a,b=2, 
                 c="hello",
                 d=3, e=4
                ):
        self.h = d + e

def extract_arguments(cls: type):
    """ get a list with the arguments with their values."""
            
    arg_tuples = []
    sig = inspect.signature(cls.__init__)
    for arg in sig.parameters.keys():
        # get the default value
        default = sig.parameters[arg].default
        continue

a = extract_arguments(MyClass)
b = extract_arguments(MyClass(a=3, b=4))