import inspect                
from utils.get import get_mutation_options, get_crossover_options, get_selection_options, get_decomposition_options, get_sampling_options, get_reference_direction_options

from utils.get import get_algorithm_options, get_problem_options, get_termination_options, get_performance_indicator_options

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
        self.algo = self.get_class_list(get_algorithm_options())

    def get_class_list(self, options_list):
        return [self.classInpection(name, obj) for name, obj in options_list]
    
    def nestedClass(self, prev_object_id, args, i, options_list):
        
        arg, value = args[i]
        
        nested_object_id = prev_object_id + "_" + arg
        args[i] = (arg, nested_object_id)
        
        for class_name, obj in options_list:
            if isinstance(obj, value.__class__):
                break
        self.mutation.append(self.classInpection(class_name, value, nested_object_id))
            
    def classInpection(self, class_name: str, cls: type, object_id = "default"):
        
        if object_id == "default": object_id = "default_" + class_name
        sig = inspect.signature(cls.__init__)
        
        args = [(arg, sig.parameters[arg].default) for arg in sig.parameters.keys() if arg not in ["self", "args", "kwargs"]]

        # deal with nested classes
        for i, (arg, value) in enumerate(args):
            if arg == "mutation":
                self.nestedClass(object_id, args, i, get_mutation_options())
                
        
        return [(object_id, class_name)] + args 