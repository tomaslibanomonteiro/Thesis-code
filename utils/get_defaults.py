import inspect                
import re
import numpy as np
from utils.get import get_mutation_options, get_crossover_options, get_selection_options, get_decomposition_options, \
                    get_sampling_options, get_reference_direction_options, get_algorithm_options, get_problem_options,\
                    get_termination_options, get_performance_indicator_options                    
from utils.get import get_mutation, get_crossover, get_selection, get_decomposition, get_sampling, get_reference_directions 

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
            return self.getOperator(object, algo_name, self.mutation, get_mutation)
        elif arg == "crossover":
            return self.getOperator(object, algo_name, self.crossover, get_crossover)
        elif arg == "selection":
            return self.getOperator(object, algo_name, self.selection, get_selection)
        elif arg == "decomposition":
            return self.getOperator(object, algo_name, self.decomposition, get_decomposition)
        elif arg == "sampling":
            return self.getOperator(object, algo_name, self.sampling, get_sampling)
        elif arg == "ref_dirs":
            return self.getOperator(object, algo_name, self.ref_dirs, get_reference_directions)
        else:
            raise Exception("unknown operator", arg)
        
    def getOperator(self, obj, algo_name: str, operators_list: list, get_function):
        # get object class name
        for row in operators_list:
            op_id, op_get_name = row[0]
            op_args = row[1:]
            op_args_dict = {arg: value for arg, value in op_args}
            try:
                op_obj = get_function(op_get_name, **op_args_dict)
            except:
                # debug_print("could not get operator", op_get_name, "with args", op_args, "trying without args")
                try: 
                    op_obj = get_function(op_get_name)
                except:
                    raise Exception("could not get operator", op_get_name, "with args", op_args)             
            
            debug_print(f"Comparing {op_obj} with {obj}")
            
            if op_obj.__class__.__name__ == obj.__class__.__name__:
                # if the operator is the same class, compare the arguments
                obj_args = self.extract_arguments(obj)
                debug_print(f"Comparing {op_args} with {obj_args}")
                if op_args == obj_args:
                    # if the arguments are the same, return the operator id
                    return op_id

        raise Exception("unknown operator", obj)                
