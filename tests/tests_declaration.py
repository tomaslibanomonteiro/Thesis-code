from backend.defaults import Defaults
from frontend.main_window import MyMainWindow
from threading import Thread
from utils.defines import RESULTS_FOLDER, RUN_OPTIONS_KEYS, PROB_KEY, ALGO_KEY, PI_KEY, TERM_KEY, N_SEEDS_KEY

class Test():
    def __init__(self, test_name: str, options: dict, defaults_soo = Defaults('soo').dict, defaults_moo = Defaults('moo').dict) -> None:
        
        self.test_name = test_name + '.csv'
        
        if set(options.keys()) != set(RUN_OPTIONS_KEYS + ['moo']):
            raise Exception('Invalid options dictionary! Test options must contain: ' + str(RUN_OPTIONS_KEYS + ['moo']))
        self.options = options
        self.moo = self.options.pop('moo') 
        self.defaults_soo = defaults_soo
        self.defaults_moo = defaults_moo
        
        self.main_window = None
        self.run = None
        self.my_thread = Thread(target=self.runTestThread)
      
    def runTest(self):
        # get main window, and run object 
        run_options_soo = self.options if not self.moo else {}
        run_options_moo = self.options if self.moo else {}
        
        self.main_window = MyMainWindow(run_options_soo, run_options_moo, self.defaults_soo, self.defaults_moo)
        self.run = self.main_window.activePage().runButton()
        
        # start a python thread 
        self.my_thread.start()
    
    def runTestThread(self):
        self.run.run()
        self.run.save_data(RESULTS_FOLDER + '/' + self.test_name)

############################################################################################################
######################################### SOO TESTS ########################################################
############################################################################################################

# 'brkga' is elementwise algo?
# 'cmaes' and 'pso' not giving consistent results

run_options_soo_algos = {
    'moo': False,
    N_SEEDS_KEY: 2,
    TERM_KEY: ['n_eval'],
    PI_KEY: ['best'],
    ALGO_KEY: ['ga', 'de', 'nelder-mead', 'pattern-search'],
    PROB_KEY: ['ackley']
}

soo_algos = Test('soo_algos', run_options_soo_algos)    

run_options_test_soo_probs = {
    'moo': False,
    N_SEEDS_KEY: 2,
    TERM_KEY: ['n_eval'],
    PI_KEY: ['best'],
    ALGO_KEY: ['de'],
    PROB_KEY: ['ackley', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9', 'g10', 'g11', 'g12', 'g13', 'g14', 'g15', 'g16', 'g17', 'g18', 'g19', 'g20', 'g21', 'g22', 'g23', 'g24', 'cantilevered_beam', 'griewank', 'himmelblau', 'knp', 'pressure_vessel', 'rastrigin', 'rosenbrock', 'schwefel', 'sphere', 'zakharov']
}

soo_probs = Test('soo_probs', run_options_test_soo_probs)

run_options_soo_mixed = {
    'moo': False,
    N_SEEDS_KEY: 2,
    TERM_KEY: ['n_eval'],
    PI_KEY: ['best'],
    ALGO_KEY: ['ga', 'pso', 'de'],
    PROB_KEY: ['ackley','g1','griewank','rastrigin','rosenbrock']
}        

soo_mixed = Test('soo_mixed', run_options_soo_mixed)

run_options_soo_simple = {
    'moo': False,
    N_SEEDS_KEY: 2,
    TERM_KEY: ['n_eval'],
    PI_KEY: ['best'],
    ALGO_KEY: ['ga'],
    PROB_KEY: ['ackley']
}
    
############################################################################################################
######################################### MOO TESTS ########################################################
############################################################################################################

run_options_moo_algos = {
    'moo': True,
    N_SEEDS_KEY: 2,
    TERM_KEY: ['n_eval'],
    ALGO_KEY: ['nsga2', 'rnsga2', 'nsga3', 'unsga3', 'rnsga3', 'moead', 'ctaea'],
    PI_KEY: ['gd+'],
    PROB_KEY: ['dtlz4']
}

moo_algos = Test('moo_algos', run_options_moo_algos)

run_options_moo_probs = {
    'moo': True,
    N_SEEDS_KEY: 1,
    TERM_KEY: ['n_eval'],
    PI_KEY: ['gd+'],
    ALGO_KEY: ['nsga2'],
    PROB_KEY: ['bnh', 'carside', 'ctp1', 'ctp2', 'ctp3', 'ctp4', 'ctp5', 'ctp6', 'ctp7', 'ctp8', 'dascmop1', 'dascmop2', 'dascmop3', 'dascmop4', 'dascmop5', 'dascmop6', 'dascmop7', 'dascmop8', 'dascmop9', 'df1', 'df2', 'df3', 'df4', 'df5', 'df6', 'df7', 'df8', 'df9', 'df10', 'df11', 'df12', 'df13', 'df14', 'modact', 'mw1', 'mw2', 'mw3', 'mw4', 'mw5', 'mw6', 'mw7', 'mw8', 'mw9', 'mw10', 'mw11', 'mw12', 'mw13', 'mw14', 'dtlz1^-1', 'dtlz1', 'dtlz2', 'dtlz3', 'dtlz4', 'dtlz5', 'dtlz6', 'dtlz7', 'convex_dtlz2', 'convex_dtlz4', 'sdtlz1', 'c1dtlz1', 'c1dtlz3', 'c2dtlz2', 'c3dtlz1', 'c3dtlz4', 'dc1dtlz1', 'dc1dtlz3', 'dc2dtlz1', 'dc2dtlz3', 'dc3dtlz1', 'dc3dtlz3', 'kursawe', 'osy', 'srn', 'tnk', 'truss2d', 'welded_beam', 'zdt1', 'zdt2', 'zdt3', 'zdt4', 'zdt5', 'zdt6', 'wfg1', 'wfg2', 'wfg3', 'wfg4', 'wfg5', 'wfg6', 'wfg7', 'wfg8', 'wfg9']
}

moo_probs = Test('moo_prob', run_options_moo_probs)

run_options_moo_mixed = {
    'moo': True,
    N_SEEDS_KEY: 2,
    TERM_KEY: ['n_eval'],
    PI_KEY: ['gd', 'gd+', 'igd+', 'igd'],
    ALGO_KEY: ['nsga2', 'nsga3'],
    PROB_KEY: ['bnh','ctp1']
}

moo_mixed = Test('moo_mixed_1', run_options_moo_mixed)

run_options_moo_simple = {
    'moo': True,
    N_SEEDS_KEY: 2,
    TERM_KEY: ['n_eval'],
    PI_KEY: ['gd'],
    ALGO_KEY: ['nsga2'],
    PROB_KEY: ['bnh']    
}
