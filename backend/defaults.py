import inspect

from utils.defines import (NO_DEFAULT, OPERATORS, VALUE_TYPES, KEY_ARGS_DICT, MUT_KEY, CROSS_KEY, CLASS_KEY, MOO_KEY,
                           SEL_KEY, SAMP_KEY, DECOMP_KEY, REF_DIR_KEY, PROB_KEY, ALGO_KEY, PI_KEY, TERM_KEY, SEEDS_KEY, 
                           CONVERT_KEY)

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
        
        self.get_str = 'moo_options' if moo else 'soo_options' 
        
        self.parameters = {}
        self.parameters[MOO_KEY] = moo
        self.get_dict = {}
        for key, (_, _, get_function) in KEY_ARGS_DICT.items():
            self.parameters[key] = self.get_table_dict(get_function(self.get_str))
            self.get_dict[key] = get_function
                                      
        # manualy changed MOO defaults
        if self.parameters[MOO_KEY]:
            self.parameters[PI_KEY]['gd']['pf'] = 'get_problem_pf' + CONVERT_KEY
            self.parameters[PI_KEY]['igd']['pf'] = 'get_problem_pf' + CONVERT_KEY
            self.parameters[PI_KEY]['igd+']['pf'] = 'get_problem_pf' + CONVERT_KEY
            self.parameters[PI_KEY]['gd+']['pf'] = 'get_problem_pf' + CONVERT_KEY
            self.parameters[PI_KEY]['-hv']['pf'] = 'get_problem_pf' + CONVERT_KEY
            self.parameters[ALGO_KEY]['nsga2']['selection'] = 'binary_tournament'
            self.parameters[ALGO_KEY]['nsga3']['selection'] = 'tournament_by_cv_then_random'
            self.parameters[ALGO_KEY]['unsga3']['selection'] = 'tournament_by_rank_and_ref_line_dist'
            self.parameters[ALGO_KEY]['ctaea']['selection'] = 'restricted_mating_ctaea'
            self.parameters[ALGO_KEY]['moead']['decomposition'] = 'pbi'
            self.parameters[REF_DIR_KEY]['das-dennis']['n_dim'] = 'n_obj' + CONVERT_KEY
            self.parameters[REF_DIR_KEY]['das-dennis']['n_partitions'] = 12
            self.parameters[REF_DIR_KEY]['energy']['n_dim'] = 'n_obj*1' + CONVERT_KEY
            self.parameters[REF_DIR_KEY]['layer-energy']['n_dim'] = 'n_obj' + CONVERT_KEY
            self.parameters[REF_DIR_KEY]['red']['n_dim'] = 'n_obj' + CONVERT_KEY
            for i in range(1, 10):
                arg = 'difficulty_factors' if i in [7,8,9] else 'difficulty' 
                self.parameters[PROB_KEY][f'dascmop' + str(i)][arg] = 1 
            
        # manualy changed SOO defaults
        else:
            self.parameters[ALGO_KEY]['ga']['selection'] = 'tournament_by_cv_and_fitness'
            
        self.parameters[TERM_KEY]['n_eval']['n_max_evals'] = 200
        self.parameters[TERM_KEY]['n_gen']['n_max_gen'] = 10
        self.parameters[TERM_KEY]['fmin']['fmin'] = 1
        self.parameters[TERM_KEY]['time']['max_time'] = 100
        
    
    def get_table_dict(self, options_dict):
        return {name: self.get_class_dict(name, obj) for name, obj in options_dict.items()}
                
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
                ret_dict[arg] = self.getOperator(arg, value)
            # check if arg and value are valid, otherwise remove it from the dict     
            elif arg not in ["self", "args", "kwargs"] and type(value) in VALUE_TYPES: 
                ret_dict[arg] = value
                
        return ret_dict

    def getOperator(self, arg: str, operator_obj):
        operator_dict = self.get_dict[arg](self.get_str)
        
        if arg == SEL_KEY: # selection must be 'by hand' because one arg is a function
            return 'by hand'                                  
        elif operator_obj in [None, NO_DEFAULT]: # if has no default value, return the first operator in the list
            return list(operator_dict.keys())[0]
        else:
            for op_id, op_class in operator_dict.items():
                # compare class names
                if operator_obj.__class__.__name__ == op_class.__name__: 
                    return op_id
            raise Exception("unknown operator", operator_obj)
        