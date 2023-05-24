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
        
    

""" My class init arguments:
    [('a', None), ('b', 2), ('c', '"hello"'), ('d', 3), ('e', 4), ('other_class', 'MyClass2(d=2)')]
"""

class MyClassWithNoInit:
    pass

def extract_arguments(cls: type):
    init_source = None
    for line in inspect.getsourcelines(cls)[0]:
        if re.match(r"^\s*def\s+__init__\s*\(.*\)", line):
            init_source = line
            break

    if init_source is None:
        return []

    match = re.match(r"def\s+__init__\s*\((.*)\)", init_source)
    if match is None:
        return []

    arg_list = match.group(1)
    args = [arg.strip() for arg in arg_list.split(",")]
    arg_tuples = []
    for arg in args:
        match = re.match(r"(\w+)(\s*=\s*(.*))?", arg)
        if match is None and arg not in ["self", "*args", "**kwargs"]:
            arg_tuples.append((arg, None))
        elif match is not None:
            arg_name = match.group(1)
            default_value = match.group(3)
            if default_value is not None:
                try:
                    default_value = eval(default_value)
                except Exception:
                    pass
            arg_tuples.append((arg_name, default_value))
    return arg_tuples

print("MyClass:" + str(extract_arguments(MyClass)))
print("MyClass2:" + str(extract_arguments(MyClass2)))
print("MyOtherClass:" + str(extract_arguments(MyClass3)))
print("MyClassWithNoInit:" + str(extract_arguments(MyClassWithNoInit)))
