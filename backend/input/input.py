import pandas as pd
from utils.get import get_algorithm, get_problem, get_termination, get_performance_indicator 
                 
ARGS = ['arg1', 'arg2', 'arg3', 'arg4', 'arg5', 'arg6', 'arg7']
ARGS_VALUES = ['arg1_value', 'arg2_value', 'arg3_value', 'arg4_value', 'arg5_value', 'arg6_value', 'arg7_value']

class Tables():
    def __init__(self, run_csv, prob_csv, term_csv, pi_csv, algo_csv, cross_csv, mut_csv, samp_csv, sel_csv, ref_csv, dec_csv):
        # read csv files and drop empty rows 
        self.run = pd.read_csv(run_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.prob = pd.read_csv(prob_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.term = pd.read_csv(term_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.pi = pd.read_csv(pi_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.algo = pd.read_csv(algo_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.cross = pd.read_csv(cross_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.mut = pd.read_csv(mut_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.samp = pd.read_csv(samp_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.selec = pd.read_csv(sel_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.ref_dirs = pd.read_csv(ref_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
        self.decomp = pd.read_csv(dec_csv).dropna(how='all').applymap(lambda s:s.lower() if type(s) == str else s)
class RunArgs():
    def __init__(self, prob_id: str, prob_object, algo_id: str, algo_object, pi_dict: dict): 
        self.prob_id = prob_id
        self.prob_object = prob_object
        self.algo_id = algo_id
        self.algo_object = algo_object
        self.pi_dict = pi_dict
class Input():
    def __init__(self, tables: Tables):
        self.run_args_list = []
        self.n_seeds = None
        self.term_object = None
        
        self.read_tables(tables)
        
    def read_tables(self, tables: Tables):
        
        n_obj_list = []
        #! TODO: estou a assumir que seed e term estão na linha 0
        # get number of seeds
        self.n_seeds = int(tables.run['number_seeds'][0])
        
        # get termination 
        term_id = tables.run['termination_id'][0]
        term_type, args = self.get_args_from_row_id('termination_id', 'termination_type', term_id, tables.term)
        self.term_object = get_termination(term_type, **args) 
        
        # get problem 
        for prob_id in tables.run['problem_id'].dropna():
            prob_type, args = self.get_args_from_row_id('problem_id', 'problem_type', prob_id, tables.prob)
            prob_object = get_problem(prob_type, **args)
            n_obj = prob_object.n_obj
            n_obj_list.append(n_obj)
            # get performance metrics dictionary
            pi_dict = {}
            if n_obj == 1: # if single objective, get the best value
                pi_dict['best'] = None
            else:
                for pi_id in tables.run['performance_indicator_id'].dropna():
                    pi_type, args = self.get_args_from_row_id('performance_indicator_id', 'performance_indicator_type', pi_id, tables.pi)
                    args['pf'] = prob_object.pareto_front()
                    pi_object = get_performance_indicator(pi_type, **args)
                    pi_dict[pi_id] = pi_object
                    
            # get algorithm 
            for algo_id in tables.run['algorithm_id'].dropna():
                algo_type, args = self.get_algo_from_row_id('algorithm_id', 'algorithm_type', algo_id, tables, n_obj)
                algo_object = get_algorithm(algo_type, **args)
    
                # save to RunArgs
                self.run_args_list.append(RunArgs(prob_id, prob_object, algo_id, algo_object, pi_dict))
                
        if 1 in n_obj_list and not all(x == 1 for x in n_obj_list):
            raise ValueError("Problems must be all single-objective or all multi-objective.")
            
    def get_args_from_row_id(self, id_column: str, type_column: str, row_id: str, table: pd.DataFrame):
                
        # get the first row of the table that matches the termination id in the 'termination_id' column
        row = table.loc[table[id_column] == row_id].iloc[0]
        
        # get arguments 
        args = {}
        for arg, arg_value in zip(ARGS, ARGS_VALUES):
            if not pd.isna(row[arg]):
                args[row[arg]] = self.try_convert( row[arg_value] )
        
        # get the class type
        class_type = row[type_column]

        return class_type, args
    
    def get_algo_from_row_id(self, id_column: str, type_column: str, row_id: str, tables: Tables, n_obj: int):
        
        from utils.get import get_reference_directions, get_decomposition, get_sampling, get_selection, get_crossover, get_mutation

        # get the row of the table that matches the algo id in the 'algo_id' column
        row = tables.algo.loc[tables.algo[id_column] == row_id].iloc[0]
        
        # get the arguments for the algorithm, and in case it is an object, get the arguments for that object
        args = {}
        for arg, arg_value in zip(ARGS, ARGS_VALUES):
            if not pd.isna(row[arg]):
                if row[arg] == 'reference_directions_id':
                    ref_dirs_type, ref_dirs_args = self.get_args_from_row_id('reference_directions_id', 'reference_directions_type', row[arg_value], tables.ref_dirs)
                    
                    # get the number of objectives from the problem
                    ref_dirs_args['n_dim'] = n_obj
                    ref_dirs_args['n_points'] = n_obj 
                    
                    args['ref_dirs'] = get_reference_directions(ref_dirs_type, **ref_dirs_args)
                    
                elif row[arg] == 'decomposition_id': 
                    decomp_type, decomp_args = self.get_args_from_row_id('decomposition_id', 'decomposition_type', row[arg_value], tables.decomp)
                    args['decomposition'] = get_decomposition(decomp_type, **decomp_args)
                    
                elif row[arg] == 'sampling_id':
                    samp_type, samp_args = self.get_args_from_row_id('sampling_id', 'sampling_type', row[arg_value], tables.decomp)
                    args['sampling'] = get_sampling(samp_type, **samp_args)
                    
                elif row[arg] == 'selection_id':
                    sel_type, sel_args = self.get_args_from_row_id('selection_id', 'selection_type', row[arg_value], tables.decomp)
                    args['selection'] = get_selection(sel_type, **sel_args)
                    
                elif row[arg] == 'crossover_id':
                    cross_type, cross_args = self.get_args_from_row_id('crossover_id', 'crossover_type', row[arg_value], tables.decomp)
                    args['crossover'] = get_crossover(cross_type, **cross_args)
                    
                elif row[arg] == 'mutation_id':
                    mut_type, mut_args = self.get_args_from_row_id('mutation_id', 'mutation_type', row[arg_value], tables.mut)
                    args['mutation'] = get_mutation(mut_type, **mut_args)
                    
                else:
                    args[row[arg]] = self.try_convert( row[arg_value] )
        # get the class type
        class_type = row[type_column]

        return class_type, args
    
    def try_convert(self, value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value