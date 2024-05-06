from backend.defaults import Defaults
from frontend.main_window import MainWindow
from utils.defines import RESULTS_FOLDER, RUN_OPTIONS_KEYS, PROB_KEY, ALGO_KEY, PI_KEY, TERM_KEY, SEEDS_KEY, MOO_KEY
import pandas as pd
from backend.get import get_algorithm, get_problem

TEST_NAME_KEY = 'test_name'
class Test():
    def __init__(self, options: dict, n_seeds:int=1, n_evals:int=500, parameters=None):
        
        self.test_name = options.pop(TEST_NAME_KEY) + '.csv'
        self.is_finished = False
        
        if SEEDS_KEY not in options.keys():
            options[SEEDS_KEY] = n_seeds
        if TERM_KEY not in options.keys():
            options[TERM_KEY] = ['n_eval']
        if 'n_evals' in options.keys():
            n_evals = options.pop('n_evals')

        if set(options.keys()) != set(RUN_OPTIONS_KEYS + [MOO_KEY]):
            raise Exception('Invalid options dictionary. Test options must contain at least: ' + str([MOO_KEY, PI_KEY, ALGO_KEY, PROB_KEY]))
        self.options = options
        self.moo = self.options.pop(MOO_KEY) 
        
        if parameters is None:
            self.parameters = Defaults(self.moo).parameters
        else:
            self.parameters = parameters
        self.parameters[TERM_KEY]['n_eval']['n_max_evals'] = n_evals
        
        # get main window, and run object 
        run_options_soo, parameters_soo = (self.options, self.parameters) if not self.moo else ({}, Defaults(False).parameters)
        run_options_moo, parameters_moo = (self.options, self.parameters) if self.moo else ({}, Defaults(True).parameters)
        
        self.main_window = MainWindow(run_options_soo, run_options_moo, parameters_soo, parameters_moo)
        self.run_thread = self.main_window.activeTabs().getRunThread()
        self.run_thread.finished.connect(self.afterRun) if self.run_thread is not None else None
    
    def run(self):
        if self.run_thread is not None: 
            self.run_thread.start()
        else:
            self.afterRun()
        
    def afterRun(self):
        if self.run_thread is not None:
            data = self.run_thread.data
        else:
            df = {'error': ['RunThread was not created.']}
            data = pd.DataFrame(df)
        data.to_csv(RESULTS_FOLDER + '/' + self.test_name, index=False)
        self.is_finished = True

############################################################################################################
######################################### SOO TESTS ########################################################
############################################################################################################

# 'brkga' is combinatorial algo, has to be run with a combinatorial problem like 'random_knp'
# 'cmaes' not giving consistent results - not setting the seed correctly?

soo_algos_list = list(get_algorithm('soo_options').keys())
soo_algos_list.remove('brkga')
soo_algos_list.remove('cmaes')

soo_algos = { 
    MOO_KEY: False,
    PI_KEY: ['best'],
    ALGO_KEY: soo_algos_list,
    PROB_KEY: ['ackley'],
    TEST_NAME_KEY: 'soo_algos',
}

soo_probs_list = list(get_problem('soo_options').keys())

soo_probs = {
    MOO_KEY: False,
    PI_KEY: ['best'],
    ALGO_KEY: ['de'],
    PROB_KEY: soo_probs_list, 
    TEST_NAME_KEY: 'soo_probs'
}

soo_mixed = {
    MOO_KEY: False,
    PI_KEY: ['best'],
    ALGO_KEY: ['ga', 'pso', 'de'],
    PROB_KEY: ['ackley','g1','griewank','rastrigin','rosenbrock'],
    TEST_NAME_KEY: 'soo_mixed'
}
    
############################################################################################################
######################################### MOO TESTS ########################################################
############################################################################################################

moo_algos_list = list(get_algorithm('moo_options').keys())

moo_algos = {
    MOO_KEY: True,
    ALGO_KEY: moo_algos_list,
    PI_KEY: ['gd+'],
    PROB_KEY: ['dtlz4'],
    TEST_NAME_KEY: 'moo_algos'
}

moo_probs_list = list(get_problem('moo_options').keys())

moo_probs = {
    MOO_KEY: True,
    PI_KEY: ['gd+'],
    ALGO_KEY: ['nsga2'],
    PROB_KEY: moo_probs_list,
    TEST_NAME_KEY: 'moo_probs'
}

moo_mixed = {
    MOO_KEY: True,
    PI_KEY: ['gd', 'gd+', 'igd+', 'igd', '-hv'],
    ALGO_KEY: ['nsga2', 'nsga3'],
    PROB_KEY: ['bnh','ctp1'],
    TEST_NAME_KEY: 'moo_mixed'
}