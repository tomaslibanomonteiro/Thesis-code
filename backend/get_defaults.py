import inspect                
import re
import numpy as np
from backend.get import get_mutation_options, get_crossover_options, get_selection_options, get_decomposition_options, \
                    get_sampling_options, get_reference_direction_options, get_algorithm_options, get_problem_options,\
                    get_termination_options, get_performance_indicator_options                    
from backend.get import get_mutation, get_crossover, get_selection, get_decomposition, get_sampling, get_reference_directions 

from utils.debug import debug_print

ARG_TYPES = (int, float, str, bool, type(None))
NO_DEFAULT = "No def"

# OPERATORS = ["mutation", "crossover", "selection", "decomposition", "sampling", "ref_dirs"] 
OPERATORS = ["mutation", "crossover", "decomposition", "sampling", "ref_dirs"] 
PRINT_LISTS = False

def list_print(name,list):
    if PRINT_LISTS:
        print("\n\n  ", name, "\n")
        for item in list:
            print("           ", item)
                    
class Defaults():
    def __init__(self):
        
        # self.other_classes = self.get_class_list(get_other_class_options())
                
        self.mutation = self.get_class_list(get_mutation_options())
        list_print("mutation", self.mutation)

        self.crossover = self.get_class_list(get_crossover_options())
        list_print("crossover", self.crossover)

        self.selection = self.get_class_list(get_selection_options())
        list_print("selection", self.selection)

        self.decomposition = self.get_class_list(get_decomposition_options())
        list_print("decomposition", self.decomposition)
        
        self.sampling = self.get_class_list(get_sampling_options())
        list_print("sampling", self.sampling)
        
        self.ref_dirs = self.get_class_list(get_reference_direction_options())
        list_print("ref_dirs", self.ref_dirs)

        self.prob = self.get_class_list(get_problem_options())
        list_print("prob", self.prob)

        self.term = self.get_class_list(get_termination_options())
        list_print("term", self.term)

        self.pi = self.get_class_list(get_performance_indicator_options())
        list_print("pi", self.pi)

        self.algo = self.get_class_list(get_algorithm_options())
        list_print("algo", self.algo)        
        
    def get_class_list(self, options_list):
        return [self.classInpection(name, obj) for name, obj in options_list]
                
    def classInpection(self, get_name: str, cls: type, object_id = "default"):
        """ get a list with the class name, the object id and the arguments with their default values.
        If the argument is an operator, get the operator id """
        
        if object_id == "default": object_id =  get_name + "_default" 
        sig = inspect.signature(cls.__init__)

        args = self.extract_arguments(cls)
            
        return [(object_id, get_name)] + args                        
    
    def extract_arguments(self, cls: type):
        """ get a list with the arguments with their values."""
        
        # some classes have arguments with the same name as operators, but they are different
        FAKE_OPERATORS = ['ReductionBasedReferenceDirectionFactory', 'RieszEnergyReferenceDirectionFactory']
        
        arg_tuples = []
        sig = inspect.signature(cls.__init__)
        for arg in sig.parameters.keys():
            if arg not in ["self", "args", "kwargs"]:
                if sig.parameters[arg].default == inspect._empty:
                    value = NO_DEFAULT
                elif arg in OPERATORS and cls.__name__ not in FAKE_OPERATORS:
                    value = self.getOperators(cls.__name__, arg, sig.parameters[arg].default)
                else:
                    value = sig.parameters[arg].default
                    if type(value) not in ARG_TYPES:
                        debug_print(f"Warning: {arg} has a value of type {type(value)} regarding class {cls}")
                        continue
                arg_tuples.append((arg, value))
            
        return arg_tuples

    def getOperators(self, algo_name: str, arg: str, object):

        if object == None:
            return None
        if arg == "mutation":   
            return self.getOperator(object, self.mutation, get_mutation_options())
        elif arg == "crossover":
            return self.getOperator(object, self.crossover, get_crossover_options())    
        elif arg == "selection":
            return self.getOperator(object, self.selection, get_selection_options())                                    
        elif arg == "decomposition":
            return self.getOperator(object, self.decomposition, get_decomposition_options())
        elif arg == "sampling":
            return self.getOperator(object, self.sampling, get_sampling_options())
        elif arg == "ref_dirs":
            return self.getOperator(object, self.ref_dirs, get_reference_direction_options())
        else:
            raise Exception("unknown operator", arg)
        
    def getOperator(self, obj: str, operators_list: list, get_list: list):
        # get object class name    
        for get_name, cls in get_list:
            if obj.__class__.__name__ == cls.__name__:
                for row in operators_list:
                    op_id, op_get_name = row[0]
                    if get_name == op_get_name:
                        return op_id
                
        raise Exception("unknown operator", obj)                