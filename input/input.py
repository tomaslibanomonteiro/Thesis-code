import pandas as pd
from pymoo.problems import get_problem
from pymoo.termination import get_termination
from utils.get import get_algorithm, get_reference_directions
from .check_PM import check_PM

# Required Columns in input file
INPUT_COLUMNS = ['N_seeds', 'PM1', 'PM2', 'PM3', 'Termination_type', 'Termination_value', 'Problem', 'Problem_arg1', 'Problem_arg1_value', 'Problem_arg2', 'Problem_arg2_value', 'Problem_arg3', 'Problem_arg3_value', 'Algorithm', 'Algorithm_arg1', 'Algorithm_arg1_value', 'Algorithm_arg2', 'Algorithm_arg2_value', 'Algorithm_arg3', 'Algorithm_arg3_value'] 
                 
ALGO_NAME = 'Algorithm' 
ALGO_ARGS = ['Algorithm_arg1', 'Algorithm_arg2', 'Algorithm_arg3']
ALGO_ARGS_VALUES = ['Algorithm_arg1_value', 'Algorithm_arg2_value', 'Algorithm_arg3_value']
 
PROB_NAME = 'Problem'
PROB_ARGS = ['Problem_arg1', 'Problem_arg2', 'Problem_arg3']
PROB_ARGS_VALUES = ['Problem_arg1_value', 'Problem_arg2_value', 'Problem_arg3_value']

TERM_NAME = 'Termination_type'
TERM_VALUE = 'Termination_value'

PM_NAMES = ['PM1', 'PM2', 'PM3']
N_SEEDS = 'N_seeds'

# check if the union of the lists equals the input columns
if not set(INPUT_COLUMNS) == set(ALGO_ARGS + ALGO_ARGS_VALUES + PROB_ARGS + PROB_ARGS_VALUES + [ALGO_NAME, PROB_NAME, TERM_NAME, TERM_VALUE] + PM_NAMES + [N_SEEDS]):
    raise Exception('Input columns do not match')
 

class RunArgs():
    def __init__(self, run_id: int, n_seeds: int, algorithm, problem, termination, PM_list: list):
        self.problem = problem
        self.algorithm = algorithm
        self.termination = termination
        self.n_seeds = n_seeds
        self.PM = PM_list
        self.run_id = run_id
        return

class Input():
    def __init__(self, csv_file):
        self.run_args_list = []
        self.read_input(csv_file)
        
    def read_input(self, csv_file):
        input_data = pd.read_csv(csv_file)
        
        # check if the input file contains all the required columns
        if not set(INPUT_COLUMNS).issubset(input_data.columns):
            raise Exception('Input file does not contain all the required columns')
        
        run_id = 0
        # for each row in input file get the arguments for the respective run
        for index, row in input_data.iterrows():
            prob_name, prob_args, term_name, term_value, PM_list = self.read_row(row)
            prob = get_problem(prob_name, **prob_args)
            algo_name, algo_args = self.read_row_algo(row, prob.n_obj)
            algo = get_algorithm(algo_name, **algo_args)
            term = get_termination(term_name, term_value)
            check_PM(PM_list, prob.n_obj)
            run_id += 1
            self.run_args_list.append(RunArgs(run_id, row[N_SEEDS], algo, prob, term, PM_list))
            
        return
    
    def read_row(self, line):
        
        prob_name = line[PROB_NAME]
        prob_args = {}
        for arg, arg_value in zip(PROB_ARGS, PROB_ARGS_VALUES):
            if not pd.isna(line[arg]):
                prob_args[line[arg]] = line[arg_value]
                
        term_name = line[TERM_NAME]
        if not pd.isna(line[TERM_VALUE]):
            term_value = line[TERM_VALUE]
        
        # get the PM names from the input file
        PM_list = [line[pm_column].lower() for pm_column in PM_NAMES if not pd.isna(line[pm_column])]
        
        return prob_name, prob_args, term_name, term_value, PM_list
    
    def read_row_algo(self, line, n_obj):
        algo_name = line[ALGO_NAME].lower()
        algo_args = {}
        for arg, arg_value in zip(ALGO_ARGS, ALGO_ARGS_VALUES):
            if not pd.isna(line[arg]):
                if line[arg] == 'ref_dirs':
                    algo_args[line[arg]] = get_reference_directions(line[arg_value], n_dim=n_obj, n_points=n_obj)
                else:
                    algo_args[line[arg]] = line[arg_value]
        return algo_name, algo_args        