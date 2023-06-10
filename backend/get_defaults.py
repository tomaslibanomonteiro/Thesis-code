import inspect                
import re
import numpy as np
from backend.get import get_mutation_options, get_crossover_options, get_selection_options, get_decomposition_options, \
                    get_sampling_options, get_reference_direction_options, get_algorithm_options, get_problem_options,\
                    get_termination_options, get_performance_indicator_options                    
from backend.get import get_mutation, get_crossover, get_selection, get_decomposition, get_sampling, get_reference_directions 

from utils.debug import debug_print
from utils.defines import VALUE_TYPES, NO_DEFAULT, OPERATORS
                    
class Defaults():
    def __init__(self, obj = 'all'):
        
        self.obj = obj
                        
        self.mutation = self.get_class_list(get_mutation_options(self.obj))
        self.crossover = self.get_class_list(get_crossover_options(self.obj))
        self.selection = self.get_class_list(get_selection_options(self.obj))
        self.decomposition = self.get_class_list(get_decomposition_options(self.obj))
        self.sampling = self.get_class_list(get_sampling_options(self.obj))
        self.ref_dirs = self.get_class_list(get_reference_direction_options(self.obj))
        self.prob = self.get_class_list(get_problem_options(self.obj))
        self.term = self.get_class_list(get_termination_options(self.obj))
        self.pi = self.get_class_list(get_performance_indicator_options(self.obj))
        self.algo = self.get_class_list(get_algorithm_options(self.obj))
        
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
        
                
        # some classes have arguments with the same name as operators, but they are different
        FAKE_OPERATORS = ['ReductionBasedReferenceDirectionFactory', 'RieszEnergyReferenceDirectionFactory']

        arg_tuples = []
        sig = inspect.signature(cls.__init__)
        for arg in sig.parameters.keys():
            if arg not in ["self", "args", "kwargs"]:
                
                value = NO_DEFAULT if sig.parameters[arg].default == inspect._empty else sig.parameters[arg].default 
                
                # arg is an operator, value is an object. Get the operator id from the object
                if arg in OPERATORS and cls.__name__ not in FAKE_OPERATORS:
                    value = self.getOperators(arg, value)
                    
                # check if value is a valid type, otherwise remove it from the list of arguments    
                if type(value) not in VALUE_TYPES:
                    debug_print(f"Warning: supressing arg \"{arg}\" of class {cls.__name__} because of invalid type")
                else:
                    arg_tuples.append((arg, value))
            
        return arg_tuples

    def getOperators(self, arg: str, obj):

        if arg == "mutation":   
            return self.getOperator(obj, self.mutation, get_mutation_options(self.obj))
        elif arg == "crossover":
            return self.getOperator(obj, self.crossover, get_crossover_options(self.obj))    
        elif arg == "selection":
            return self.getOperator(obj, self.selection, get_selection_options(self.obj))                                    
        elif arg == "decomposition":
            return self.getOperator(obj, self.decomposition, get_decomposition_options(self.obj))
        elif arg == "sampling":
            return self.getOperator(obj, self.sampling, get_sampling_options(self.obj))
        elif arg == "ref_dirs":
            return self.getOperator(obj, self.ref_dirs, get_reference_direction_options(self.obj))
        else:
            raise Exception("unknown operator", arg)
        
    def getOperator(self, obj: str, operators_list: list, get_list: list):
        
        # if operator has no default value, return the first operator in the list
        if obj in [None, NO_DEFAULT]:
            return get_list[0][0] + "_default"
        
        # get object class name    
        for get_name, cls in get_list:
            if obj.__class__.__name__ == cls.__name__:
                for row in operators_list:
                    op_id, op_get_name = row[0]
                    if get_name == op_get_name:
                        return op_id
                
        raise Exception("unknown operator", obj)                
