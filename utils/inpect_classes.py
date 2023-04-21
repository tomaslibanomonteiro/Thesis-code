import inspect                
from utils.get import get_mutation_options, get_crossover_options, get_selection_options, get_decomposition_options, get_sampling_options, get_reference_direction_options

from utils.get import get_algorithm_options, get_problem_options, get_termination_options, get_performance_indicator_options

NO_DEFAULT = "no default (need to be set)"
class Defaults():
    def __init__(self):
        
        self.mutation = self.get_class_list(get_mutation_options())
        self.crossover = self.get_class_list(get_crossover_options())
        self.selection = self.get_class_list(get_selection_options())
        self.decomposition = self.get_class_list(get_decomposition_options())
        self.sampling = self.get_class_list(get_sampling_options())
        self.ref_dirs = self.get_class_list(get_reference_direction_options())
                
        self.prob = self.get_class_list(get_problem_options())
        self.term = self.get_class_list(get_termination_options())
        self.pi = self.get_class_list(get_performance_indicator_options())
        self.algo = self.get_class_list(get_algorithm_options(), algo_inspection=True)

    def get_class_list(self, options_list, algo_inspection = False):
        return [self.classInpection(name, obj, algo_inspection=algo_inspection) for name, obj in options_list]
    
    def nestedClass(self, prev_object_id: str, args: list, i: int, options_list: list, list_to_append: list):
        
        arg, value = args[i]
        
        nested_object_id = prev_object_id + "_" + arg
        args[i] = (arg, nested_object_id)
        
        for class_name, obj in options_list:
            if isinstance(obj, value.__class__):
                break
        list_to_append.append(self.classInpection(class_name, value, nested_object_id))
            
    def classInpection(self, class_name: str, cls: type, object_id = "default", algo_inspection = False):
        
        if object_id == "default": object_id =  class_name + "_default" 
        sig = inspect.signature(cls.__init__)
        
        args = []
        for arg in sig.parameters.keys():
            if arg in ["self", "args", "kwargs"]: continue
            if sig.parameters[arg].default is inspect.Parameter.empty:
                value = NO_DEFAULT
            else:
                value = sig.parameters[arg].default
            args.append((arg, value))
        
        if algo_inspection:
            # deal with nested classes
            for i, (arg, value) in enumerate(args):
                if arg == "mutation":   
                    self.nestedClass(object_id, args, i, get_mutation_options(), self.mutation)
                elif arg == "crossover":
                    self.nestedClass(object_id, args, i, get_crossover_options(), self.crossover)
                elif arg == "selection":
                    self.nestedClass(object_id, args, i, get_selection_options(), self.selection)
                elif arg == "decomposition":
                    self.nestedClass(object_id, args, i, get_decomposition_options(), self.decomposition)
                elif arg == "sampling":
                    self.nestedClass(object_id, args, i, get_sampling_options(), self.sampling)
                elif arg == "ref_dirs":
                    self.nestedClass(object_id, args, i, get_reference_direction_options(), self.ref_dirs)
            
        final_list = [object_id, class_name] + [item for tpl in args for item in tpl]                
        return final_list