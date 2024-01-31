import inspect

from utils.defines import (NO_DEFAULT, OPERATORS, VALUE_TYPES, KEY_ARGS_DICT, MUT_KEY, CROSS_KEY, CLASS_KEY,
                           SEL_KEY, SAMP_KEY, DECOMP_KEY, REF_DIR_KEY, PROB_KEY, ALGO_KEY, PI_KEY, TERM_KEY, N_SEEDS_KEY)

class Defaults():
    def __init__(self, obj = 'all'):
        """obj can be 'soo', 'moo' or 'all'        
            what is changed in the defaults set by the code? #!
            - if the algorithm has no default operator value, the first operator in the 
            list is assumed as the default
            - the list of specific arguments changed is at the end 
        """                
        self.obj = obj
        
        key_get_pairs = [(key, get_options_function) for key, (tab_name, label, get_function, get_options_function) in KEY_ARGS_DICT.items()]
        
        self.dict = {}
        self.get_dict = {}
        for key, get_options_function in key_get_pairs:
            self.dict[key] = self.get_table_dict(get_options_function(self.obj))
            self.get_dict[key] = get_options_function
                            
        # changed defaults
        if obj != 'moo':
            self.dict[ALGO_KEY]['ga']['selection'] = 'tournament_by_cv_and_fitness'
        if obj != 'soo':
            self.dict[ALGO_KEY]['nsga2']['selection'] = 'binary_tournament'
            self.dict[ALGO_KEY]['nsga3']['selection'] = 'tournament_by_cv_then_random'
            self.dict[ALGO_KEY]['unsga3']['selection'] = 'tournament_by_rank_and_ref_line_dist'
            self.dict[ALGO_KEY]['ctaea']['selection'] = 'restricted_mating_ctaea'
            self.dict[ALGO_KEY]['rnsga3']['selection'] = 'tournament_by_cv_then_random'
        
        self.dict[TERM_KEY]['n_eval']['n_max_evals'] = 5000
        self.dict[TERM_KEY]['n_gen']['n_max_gen'] = 40
        self.dict[TERM_KEY]['fmin']['fmin'] = 1
        self.dict[TERM_KEY]['time']['max_time'] = 10
        
        self.dict[REF_DIR_KEY]['(das-dennis|uniform)']['n_dim'] = 'n_obj*1'
        self.dict[REF_DIR_KEY]['(das-dennis|uniform)']['n_points'] = 'n_obj*2'
        self.dict[REF_DIR_KEY]['(energy|riesz)']['n_dim'] = 'n_obj*1'
        self.dict[REF_DIR_KEY]['(energy|riesz)']['n_points'] = 'n_obj*2'
        self.dict[REF_DIR_KEY]['(layer-energy|layer-riesz)']['n_dim'] = 'n_obj*2'
        self.dict[REF_DIR_KEY]['(layer-energy|layer-riesz)']['partitions'] = 'n_obj*2'
        self.dict[REF_DIR_KEY]['red']['n_dim'] = 'n_obj*1'
        self.dict[REF_DIR_KEY]['red']['n_points'] = 'n_obj*2'
        
        if self.obj != 'soo':                
            self.dict[PI_KEY]['gd']['pf'] = 'get from problem'
            self.dict[PI_KEY]['igd']['pf'] = 'get from problem'
            self.dict[PI_KEY]['igd+']['pf'] = 'get from problem'
            self.dict[PI_KEY]['gd+']['pf'] = 'get from problem'
            self.dict[PI_KEY]['hv']['pf'] = 'get from problem'
    
    def return_dict(self):
        return self.dict
    
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
            return self.getOperator(obj, self.dict[arg], self.get_dict[arg](self.obj))
        
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
