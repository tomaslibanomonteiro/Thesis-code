from backend.get_defaults import Defaults
from frontend.main_window import MyMainWindow
from threading import Thread
from utils.defines import RESULTS_FOLDER, RUN_OPTIONS_KEYS

class Test():
    def __init__(self, test_name: str, options: dict, defaults_soo = Defaults('soo'), defaults_moo = Defaults('moo')) -> None:
        
        self.test_name = test_name + '.csv'
        if set(options.keys()) != set(RUN_OPTIONS_KEYS):
            raise Exception('Invalid options dictionary! Test must contain all options: ' + str(RUN_OPTIONS_KEYS))
        self.options = options
        self.defaults_soo = defaults_soo
        self.defaults_moo = defaults_moo
        
        self.main_window = None
        self.run = None
        self.my_thread = Thread(target=self.runTestThread)
      
    def runTest(self):
        # get main window, and run object 
        self.main_window = MyMainWindow(self.options['moo'], self.options, self.defaults_soo, self.defaults_moo)
        self.run = self.main_window.getRunObject()
        
        # start a python thread 
        self.my_thread.start()
    
    def runTestThread(self):
        self.run.run()
        self.run.save_data(RESULTS_FOLDER + '/' + self.test_name)

############################################################################################################
######################################### SOO TESTS ########################################################
############################################################################################################

# 'brkga_default' is elementwise algo?
# 'cmaes_default' and 'pso_default' not giving consistent results

options_soo_algos = {
    'moo': False,
    'n_seeds': 2,
    'term': ['n_eval_default'],
    'pi': ['best_default'],
    'algo': ['ga_default', 'de_default', 'nelder-mead_default', 'pattern-search_default'],
    'prob': ['ackley_default']
}

soo_algos = Test('soo_algos', options_soo_algos)    

options_test_soo_probs = {
    'moo': False,
    'n_seeds': 2,
    'term': ['n_eval_default'],
    'pi': ['best_default'],
    'algo': ['de_default'],
    'prob': ['ackley_default', 'g1_default', 'g2_default', 'g3_default', 'g4_default', 'g5_default', 'g6_default', 'g7_default', 'g8_default', 'g9_default', 'g10_default', 'g11_default', 'g12_default', 'g13_default', 'g14_default', 'g15_default', 'g16_default', 'g17_default', 'g18_default', 'g19_default', 'g20_default', 'g21_default', 'g22_default', 'g23_default', 'g24_default', 'cantilevered_beam_default', 'griewank_default', 'himmelblau_default', 'knp_default', 'pressure_vessel_default', 'rastrigin_default', 'rosenbrock_default', 'schwefel_default', 'sphere_default', 'zakharov_default']
}

soo_probs = Test('soo_probs', options_test_soo_probs)

options_soo_mixed = {
    'moo': False,
    'n_seeds': 2,
    'term': ['n_eval_default'],
    'pi': ['best_default'],
    'algo': ['ga_default', 'pso_default', 'de_default'],
    'prob': ['ackley_default','g1_default','griewank_default','rastrigin_default','rosenbrock_default']
}        

soo_mixed = Test('soo_mixed', options_soo_mixed)
    
############################################################################################################
######################################### MOO TESTS ########################################################
############################################################################################################

options_moo_algos = {
    'moo': True,
    'n_seeds': 2,
    'term': ['n_eval_default'],
    'algo': ['nsga2_default', 'rnsga2_default', 'nsga3_default', 'unsga3_default', 'rnsga3_default', 'moead_default', 'ctaea_default'],
    'pi': ['gd+_default'],
    'prob': ['dtlz4_default']
}

moo_algos = Test('moo_algos', options_moo_algos)

options_moo_probs = {
    'moo': True,
    'n_seeds': 1,
    'term': ['n_eval_default'],
    'pi': ['gd+_default'],
    'algo': ['nsga2_default'],
    'prob': ['bnh_default', 'carside_default', 'ctp1_default', 'ctp2_default', 'ctp3_default', 'ctp4_default', 'ctp5_default', 'ctp6_default', 'ctp7_default', 'ctp8_default', 'dascmop1_default', 'dascmop2_default', 'dascmop3_default', 'dascmop4_default', 'dascmop5_default', 'dascmop6_default', 'dascmop7_default', 'dascmop8_default', 'dascmop9_default', 'df1_default', 'df2_default', 'df3_default', 'df4_default', 'df5_default', 'df6_default', 'df7_default', 'df8_default', 'df9_default', 'df10_default', 'df11_default', 'df12_default', 'df13_default', 'df14_default', 'modact_default', 'mw1_default', 'mw2_default', 'mw3_default', 'mw4_default', 'mw5_default', 'mw6_default', 'mw7_default', 'mw8_default', 'mw9_default', 'mw10_default', 'mw11_default', 'mw12_default', 'mw13_default', 'mw14_default', 'dtlz1^-1_default', 'dtlz1_default', 'dtlz2_default', 'dtlz3_default', 'dtlz4_default', 'dtlz5_default', 'dtlz6_default', 'dtlz7_default', 'convex_dtlz2_default', 'convex_dtlz4_default', 'sdtlz1_default', 'c1dtlz1_default', 'c1dtlz3_default', 'c2dtlz2_default', 'c3dtlz1_default', 'c3dtlz4_default', 'dc1dtlz1_default', 'dc1dtlz3_default', 'dc2dtlz1_default', 'dc2dtlz3_default', 'dc3dtlz1_default', 'dc3dtlz3_default', 'kursawe_default', 'osy_default', 'srn_default', 'tnk_default', 'truss2d_default', 'welded_beam_default', 'zdt1_default', 'zdt2_default', 'zdt3_default', 'zdt4_default', 'zdt5_default', 'zdt6_default', 'wfg1_default', 'wfg2_default', 'wfg3_default', 'wfg4_default', 'wfg5_default', 'wfg6_default', 'wfg7_default', 'wfg8_default', 'wfg9_default']
}

moo_probs = Test('moo_prob', options_moo_probs)

options_moo_mixed = {
    'moo': True,
    'n_seeds': 2,
    'term': ['n_eval_default'],
    'pi': ['gd_default', 'gd+_default', 'igd+_default', 'igd_default', 'hv_default', 'hv+_default'],
    'algo': ['nsga2_default', 'nsga3_default'],
    'prob': ['bnh_default','ctp1_default']
}

moo_mixed = Test('moo_mixed_1', options_moo_mixed)

