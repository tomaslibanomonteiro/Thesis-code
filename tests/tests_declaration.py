from backend.defaults import Defaults
from frontend.main_window import MainWindow
from utils.defines import RESULTS_FOLDER, RUN_OPTIONS_KEYS, PROB_KEY, ALGO_KEY, PI_KEY, TERM_KEY, SEEDS_KEY, MOO_KEY

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
        self.run_thread.finished.connect(self.afterRun)
    
    def run(self):
        self.run_thread.start()
        
    def afterRun(self):
        data = self.run_thread.data
        data.to_csv(RESULTS_FOLDER + '/' + self.test_name, index=False)
        self.is_finished = True

############################################################################################################
######################################### SOO TESTS ########################################################
############################################################################################################

# 'brkga' is elementwise algo?
# 'cmaes' and 'pso' not giving consistent results

soo_algos = { 
    MOO_KEY: False,
    PI_KEY: ['best'],
    ALGO_KEY: ['ga', 'de', 'nelder-mead', 'pattern-search', 'cmaes', 'pso'],
    PROB_KEY: ['ackley'],
    TEST_NAME_KEY: 'soo_algos',
}

# 'knp' not set?
soo_probs = {
    MOO_KEY: False,
    PI_KEY: ['best'],
    ALGO_KEY: ['de'],
    PROB_KEY: ['ackley', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9', 'g10', 'g11', 'g12', 'g13', 'g14', 'g15', 'g16', 'g17', 'g18', 'g19', 'g20', 'g21', 'g22', 'g23', 'g24', 'cantilevered_beam', 'griewank', 'himmelblau', 'pressure_vessel', 'rastrigin', 'rosenbrock', 'schwefel', 'sphere', 'zakharov'],
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

moo_algos = {
    MOO_KEY: True,
    ALGO_KEY: ['nsga2', 'rnsga2', 'nsga3', 'unsga3', 'rnsga3', 'moead', 'ctaea'],
    PI_KEY: ['gd+'],
    PROB_KEY: ['dtlz4'],
    TEST_NAME_KEY: 'moo_algos'
}

moo_probs = {
    MOO_KEY: True,
    PI_KEY: ['gd+'],
    ALGO_KEY: ['nsga2'],
    PROB_KEY: ['bnh', 'carside', 'ctp1', 'ctp2', 'ctp3', 'ctp4', 'ctp5', 'ctp6', 'ctp7', 'ctp8', 'dascmop1', 'dascmop2', 'dascmop3', 'dascmop4', 'dascmop5', 'dascmop6', 'dascmop7', 'dascmop8', 'dascmop9', 'df1', 'df2', 'df3', 'df4', 'df5', 'df6', 'df7', 'df8', 'df9', 'df10', 'df11', 'df12', 'df13', 'df14', 'modact', 'mw1', 'mw2', 'mw3', 'mw4', 'mw5', 'mw6', 'mw7', 'mw8', 'mw9', 'mw10', 'mw11', 'mw12', 'mw13', 'mw14', 'dtlz1^-1', 'dtlz1', 'dtlz2', 'dtlz3', 'dtlz4', 'dtlz5', 'dtlz6', 'dtlz7', 'convex_dtlz2', 'convex_dtlz4', 'sdtlz1', 'c1dtlz1', 'c1dtlz3', 'c2dtlz2', 'c3dtlz1', 'c3dtlz4', 'dc1dtlz1', 'dc1dtlz3', 'dc2dtlz1', 'dc2dtlz3', 'dc3dtlz1', 'dc3dtlz3', 'kursawe', 'osy', 'srn', 'tnk', 'truss2d', 'welded_beam', 'zdt1', 'zdt2', 'zdt3', 'zdt4', 'zdt5', 'zdt6', 'wfg1', 'wfg2', 'wfg3', 'wfg4', 'wfg5', 'wfg6', 'wfg7', 'wfg8', 'wfg9'],
    TEST_NAME_KEY: 'moo_probs'
}

moo_mixed = {
    MOO_KEY: True,
    PI_KEY: ['gd', 'gd+', 'igd+', 'igd'],
    ALGO_KEY: ['nsga2', 'nsga3'],
    PROB_KEY: ['bnh','ctp1'],
    TEST_NAME_KEY: 'moo_mixed'
}