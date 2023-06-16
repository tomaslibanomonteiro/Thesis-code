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
        """obj can be 'soo', 'moo' or 'all'        
            what is changed in the defaults set by the code?
            - if the algorithm has no default operator value, the first operator in the 
            list is assumed as the default
            - the list of specific arguments changed is at the end 
        """                
        self.obj = obj

        self.mutation = self.get_table_dict(get_mutation_options(self.obj))
        self.crossover = self.get_table_dict(get_crossover_options(self.obj))
        self.selection = self.get_table_dict(get_selection_options(self.obj))
        self.decomposition = self.get_table_dict(get_decomposition_options(self.obj))
        self.sampling = self.get_table_dict(get_sampling_options(self.obj))
        self.ref_dirs = self.get_table_dict(get_reference_direction_options(self.obj))
        self.prob = self.get_table_dict(get_problem_options(self.obj))
        self.term = self.get_table_dict(get_termination_options(self.obj))
        self.pi = self.get_table_dict(get_performance_indicator_options(self.obj))
        self.algo = self.get_table_dict(get_algorithm_options(self.obj))
        
        # changed defaults
        self.term['n_evals_default']['n_max_evals'] = 1000 
        self.term['n_gen_default']['n_max_gen'] = 100
        self.term['fmin_default']['fmin'] = 1
        self.term['time_default']['max_time'] = 10 
        
        self.ref_dirs['(das-dennis|uniform)_default']['n_dim'] = 'n_obj*1'
        self.ref_dirs['(das-dennis|uniform)_default']['n_points'] = 'n_obj*2'
        self.ref_dirs['(energy|riesz)_default']['n_dim'] = 'n_obj*1'
        self.ref_dirs['(energy|riesz)_default']['n_points'] = 'n_obj*2'
        self.ref_dirs['(layer-energy|layer-riesz)_default']['n_dim'] = 'n_obj*2'
        self.ref_dirs['(layer-energy|layer-riesz)_default']['partitions'] = 'n_obj*2'
        self.ref_dirs['red_default']['n_dim'] = 'n_obj*1'
        self.ref_dirs['red_default']['n_points'] = 'n_obj*2'
        
        if self.obj != 'soo':                
            self.pi['gd_default']['pf'] = 'get from problem'
            self.pi['igd_default']['pf'] = 'get from problem'
            self.pi['igd+_default']['pf'] = 'get from problem'
            self.pi['gd+_default']['pf'] = 'get from problem'
        
        
    def get_table_dict(self, options_list):
        return {name + '_default' : self.get_class_dict(name, obj) for name, obj in options_list}
                
    def get_class_dict(self, get_name: str, cls: type):
        """ get a dict with the class name, the object id and the arguments with their default values.
        If the argument is an operator, get the operator id """
        
        # some classes have arguments with the same name as operators, but they are different
        FAKE_OPERATORS = ['ReductionBasedReferenceDirectionFactory', 'RieszEnergyReferenceDirectionFactory']
        
        sig = inspect.signature(cls.__init__)
        args_dict = {arg: param.default for arg, param in sig.parameters.items()}
        
        ret_dict = {"class": get_name}    
        for arg, value in args_dict.items():   
            if value == inspect._empty:
                value = NO_DEFAULT
                
            # if arg is an operator, value is an object. Get the operator id from the object
            if arg in OPERATORS and cls.__name__ not in FAKE_OPERATORS:
                ret_dict[arg] = self.getOperators(arg, value)
            # check if arg and value are valid, otherwise remove it from the dict     
            elif arg not in ["self", "args", "kwargs"] and type(value) in VALUE_TYPES: 
                ret_dict[arg] = value
                
        return ret_dict

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
        
    def getOperator(self, obj: str, op_table: list, get_list: list):
        
        # if operator has no default value, return the first operator in the list
        if obj in [None, NO_DEFAULT]:
            return get_list[0][0] + "_default"
        
        # get object class name    
        for get_name, cls in get_list:
            if obj.__class__.__name__ == cls.__name__:
                for op_id, op_dict in op_table.items():
                    if get_name == op_dict['class']:
                        return op_id
                
        raise Exception("unknown operator", obj)                
