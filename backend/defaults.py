import inspect

from utils.defines import (NO_DEFAULT, OPERATORS, VALUE_TYPES, KEY_ARGS_DICT, MUT_KEY, CROSS_KEY, CLASS_KEY, MOO_KEY,
                           SEL_KEY, SAMP_KEY, DECOMP_KEY, REF_DIR_KEY, PROB_KEY, ALGO_KEY, PI_KEY, TERM_KEY, N_SEEDS_KEY)

class Defaults():
    """
    This class is used to set up default values for various parameters in an optimization problem. 
    
    It gets single or multi objective parameters according to the boolean parameter 'moo'

    Attributes
    ----------
    'self.parameters' will hold the default values for various parameters 

    The class also modifies some default values based on whether the problem is a MOO or SOO problem for the exceptions,
    namely to get the Pareto Front or Reference Directions depending on the problem at hand.

    Class arguments that call as a default value a function or other class are ommited in the app, and then called with their default value.
    The exception is if the argument is an operator the OPERATORS list. In that case, the value will be set to the ID of the
    correspondent operator, so it later can be retrived.
    """
    def __init__(self, moo: bool): 
        
        self.get_str = 'moo' if moo else 'soo' 
        key_get_pairs = [(key, get_options_function) for key, (_, _, _, get_options_function) in KEY_ARGS_DICT.items()]
        
        self.parameters = {}
        self.parameters[MOO_KEY] = moo
        self.get_dict = {}
        for key, get_options_function in key_get_pairs:
            self.parameters[key] = self.get_table_dict(get_options_function(self.get_str))
            self.get_dict[key] = get_options_function
                            
        # changed defaults
        if self.parameters[MOO_KEY]:
            self.parameters[PI_KEY]['gd']['pf'] = 'get from problem'
            self.parameters[PI_KEY]['igd']['pf'] = 'get from problem'
            self.parameters[PI_KEY]['igd+']['pf'] = 'get from problem'
            self.parameters[PI_KEY]['gd+']['pf'] = 'get from problem'
            self.parameters[PI_KEY]['hv']['pf'] = 'get from problem'
            self.parameters[ALGO_KEY]['nsga2']['selection'] = 'binary_tournament'
            self.parameters[ALGO_KEY]['nsga3']['selection'] = 'tournament_by_cv_then_random'
            self.parameters[ALGO_KEY]['unsga3']['selection'] = 'tournament_by_rank_and_ref_line_dist'
            self.parameters[ALGO_KEY]['ctaea']['selection'] = 'restricted_mating_ctaea'
            self.parameters[ALGO_KEY]['rnsga3']['selection'] = 'tournament_by_cv_then_random'
        else:
            self.parameters[ALGO_KEY]['ga']['selection'] = 'tournament_by_cv_and_fitness'
            
        self.parameters[TERM_KEY]['n_eval']['n_max_evals'] = 4000
        self.parameters[TERM_KEY]['n_gen']['n_max_gen'] = 10
        self.parameters[TERM_KEY]['fmin']['fmin'] = 1
        self.parameters[TERM_KEY]['time']['max_time'] = 100
        
        self.parameters[REF_DIR_KEY]['(das-dennis|uniform)']['n_dim'] = 'n_obj*1'
        self.parameters[REF_DIR_KEY]['(das-dennis|uniform)']['n_points'] = 'n_obj*2'
        self.parameters[REF_DIR_KEY]['(energy|riesz)']['n_dim'] = 'n_obj*1'
        self.parameters[REF_DIR_KEY]['(energy|riesz)']['n_points'] = 'n_obj*2'
        self.parameters[REF_DIR_KEY]['(layer-energy|layer-riesz)']['n_dim'] = 'n_obj*2'
        self.parameters[REF_DIR_KEY]['(layer-energy|layer-riesz)']['partitions'] = 'n_obj*2'
        self.parameters[REF_DIR_KEY]['red']['n_dim'] = 'n_obj*1'
        self.parameters[REF_DIR_KEY]['red']['n_points'] = 'n_obj*2'
            
    def return_dict(self):
        return self.parameters
    
    def get_table_dict(self, options_list):
        return {name: self.get_class_dict(name, obj) for name, obj in options_list}
                
    def get_class_dict(self, get_name: str, cls: type):
        """ get a dict with the class name, the object id and the arguments with their default values.
        If the argument is an operator, get the operator id """
        
        # some classes have arguments with the same name as operators, but they are different
        FAKE_OPERATORS = ['ReductionBasedReferenceDirectionFactory', 'RieszEnergyReferenceDirectionFactory']
        
        sig = inspect.signature(cls.__init__)
        args_dict = {arg: param.default for arg, param in sig.parameters.items()}
        
        ret_dict = {CLASS_KEY: get_name}    
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
        if arg == SEL_KEY: # selection must be 'by hand' because one arg is a function
            return 'by hand'                                  
        elif arg not in OPERATORS: 
            raise Exception("unknown operator", arg)
        else:
            return self.getOperator(obj, self.parameters[arg], self.get_dict[arg](self.get_str))
        
    def getOperator(self, obj: str, op_table: dict, get_list: list):
        
        # if operator has no default value, return the first operator in the list
        if obj in [None, NO_DEFAULT]:
            return get_list[0][0]
        # get object class name    
        for get_name, cls in get_list:
            if obj.__class__.__name__ == cls.__name__:
                for op_id, op_dict in op_table.items():
                    if get_name == op_dict[CLASS_KEY]:
                        return op_id
                
        raise Exception("unknown operator", obj)                
