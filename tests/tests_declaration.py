from backend.get_defaults import Defaults
from frontend.main_window import MyMainWindow
from threading import Thread
from utils.defines import RESULTS_FOLDER

class Test():
    def __init__(self, test_name: str, test_types: list, options: dict, defaults_soo = Defaults('soo'), defaults_moo = Defaults('moo')) -> None:
        
        self.test_name = test_name + '.csv'
        self.test_types = test_types
        self.options = options
        self.defaults_soo = defaults_soo
        self.defaults_moo = defaults_moo
        
        self.main_window = None
        self.run = None
        self.my_thread = Thread(target=self.runTestThread)

                
    def isOfType(self, test_types: list) -> bool:
        return any([t in self.test_types for t in test_types])
    
    def runTest(self):
        # get main window, and run object 
        self.main_window = MyMainWindow(self.isOfType(['moo']), self.options, self.defaults_soo, self.defaults_moo)
        self.run = self.main_window.getRunObject()
        
        # start a python thread 
        self.my_thread.start()
    
    def runTestThread(self):
        self.run.run()
        self.run.saveData(RESULTS_FOLDER + '/' + self.test_name)

options_test_de = {
    'moo': False,
    'n_seeds': 2,
    'term': ['n_gen_default'],
    'pi': ['best_default'],
    'algo': ['de_default'],
    'prob': ['ackley_default']
}

test_de = Test('de', ['soo', 'short'], options_test_de)

options_test1 = {
    'moo': True,
    'n_seeds': 2,
    'term': ['n_gen_default'],
    'pi': ['gd_default', 'gd+_default', 'igd+_default'],
    'algo': ['nsga2_default', 'nsga3_default'],
    'prob': ['bnh_default','ctp1_default']
}

test1 = Test('moo_mixed', ['moo', 'short'], options_test1)

options_test2 = {
    'moo': True,
    'n_seeds': 2,
    'term': ['n_gen_default'],
    'pi': ['gd_default', 'gd+_default'],
    'algo': ['nsga2_default'],
    'prob': ['bnh_default','ctp1_default', 'ctp2_default', 'ctp3_default']
}

test2 = Test('moo_prob', ['moo', 'short', 'prob'], options_test2)

options_test3 = {
    'moo': False,
    'n_seeds': 2,
    'term': ['n_gen_default'],
    'pi': ['best_default'],
    'algo': ['ga_default', 'pso_default', 'de_default'],
    'prob': ['ackley_default','g1_default','griewank_default','rastrigin_default','rosenbrock_default']
}        

test3 = Test('soo_mixed', ['soo', 'short'], options_test3)
