import inspect                
import re
import numpy as np
from utils.get import get_mutation_options, get_crossover_options, get_selection_options, get_decomposition_options, \
                    get_sampling_options, get_reference_direction_options, get_algorithm_options, get_problem_options,\
                    get_termination_options, get_performance_indicator_options                    
from utils.get import get_mutation, get_crossover, get_selection, get_decomposition, get_sampling, get_reference_directions 

ARG_TYPES = (int, float, str, bool, tuple, type(None))
NO_DEFAULT = "No default, needs to be set"

OPERATORS = ["mutation", "crossover", "selection", "decomposition", "sampling", "ref_dirs"] 

def list_print(name,list):
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
        self.term = self.get_class_list(get_termination_options())
        self.pi = self.get_class_list(get_performance_indicator_options())
        self.algo = self.get_class_list(get_algorithm_options())
        
        list_print("prob", self.prob)
        list_print("term", self.term)
        list_print("pi", self.pi)
        
    def get_class_list(self, options_list):
        return [self.classInpection(name, obj) for name, obj in options_list]
    
                
    def classInpection(self, class_name: str, cls: type, object_id = "default"):
        """ get a list with the class name, the object id and the arguments with their default values.
        If the argument is an operator, get the operator id """
        
        if object_id == "default": object_id =  class_name + "_default" 
        sig = inspect.signature(cls.__init__)

        args = self.extract_arguments(cls)
            
        return [(object_id, class_name)] + args                        
    
    def extract_arguments(self, cls: type):
        init_source = None
        for line in inspect.getsourcelines(cls)[0]:
            if line.strip().startswith("def __init__"):
                init_source = line
                break
        if init_source is None:
            return []
        match = re.search(r"def __init__\(self, (.*)\):", init_source)
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
                if arg_name in OPERATORS:
                    self.getOperators(cls.__name__, arg_name, cls)
                else:
                    default_value = match.group(3)
                    if default_value is not None:
                        try:
                            default_value = eval(default_value)
                            if not isinstance(default_value, ARG_TYPES):
                                default_value = match.group(3)
                        except:
                            print("could not evaluate default value", default_value, "for argument", arg_name, "in class", cls.__name__)
                            pass
                if 'default_value' in locals():
                    arg_tuples.append((arg_name, default_value))
                else:
                    arg_tuples.append((arg_name, None))
        return arg_tuples

    def getOperators(self, algo_name: str, arg: str, object):

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
        
    def getOperator(self, object, algo_name: str, operators_list: list, get_function):
        # get object class name
        for operator in operators_list:
            operator_id = operator[0]
            operator_class_name = operator[1]
            operator_args = {item[0]: item[1] for item in operator[2:]}
            try:
                compare_operator = get_function(operator_class_name, **operator_args)
            except:
                continue
            print(f"Comparing {object} with {compare_operator}")
            
            if object.__class__.__name__ == compare_operator.__class__.__name__ :
                if inspect.signature(object.__init__) == inspect.signature(compare_operator.__init__):
                    print("same signature")
                    return operator_id
                else:
                    print("different signature")
                    print(inspect.signature(object.__init__))
                    print(inspect.signature(compare_operator.__init__))
            # for arg in inspect.signature(object.__init__).parameters.keys(): 
            #     obj_arg_value = getattr(object, arg)
            #     cmp_arg_value = getattr(compare_operator, arg)
            #     if obj_arg_value != cmp_arg_value:
            #         print(f"Difference in argument {arg}: {obj_arg_value} vs {cmp_arg_value}")
            # if compare_operator == object:
            #     return operator_id
            # elif compare_operator.__class__.__name__ == object.__class__.__name__:
            #     # if the operator is not in the list, add it
            #     operators_list.append(self.classInpection(operator_class_name, object, operator_class_name + "_" + algo_name))

        raise Exception("unknown operator", object)                
