import inspect
import re
from typing import Any, List, Tuple


class MyClass:
    def __init__(self, a,b=2, 
                 c="hello",
                 d=3, e=4
                ):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def my_method(self):
        pass

class MyClass2:
    def __init__(self, d=3, e=4):
        self.d = d
        self.e = e

    def my_other_method(self):
        pass

class MyClass3:
    def __init__(self, a,b=2, 
                 c="hello",
                 d=3, e=4, other_class=MyClass2(d=2)
                ) -> None: 
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.other_class = other_class    

import inspect

import inspect

def get_init_args(cls):
    lines = inspect.getsourcelines(cls.__init__)[0]
    init_args = [line.strip() for line in lines if line.strip().startswith("def __init__")][0]
    init_args = init_args[init_args.index("(")+1:init_args.index(")")]
    arg_values = []
    for arg in init_args.split(","):
        arg = arg.strip()
        if "=" in arg:
            arg_name, arg_default = arg.split("=")
            arg_default = arg_default.strip()
            if arg_default.startswith(("'", '"')):
                arg_default = arg_default[1:-1]
            arg_values.append((arg_name, arg_default))
        else:
            arg_values.append((arg, None))
    return arg_values

# Example usage:
my_class_3_args = get_init_args(MyClass3)
print(my_class_3_args)