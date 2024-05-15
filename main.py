from PyQt5.QtWidgets import QApplication
from frontend.main_window import MainWindow
from utils.defines import SEEDS_KEY, TERM_KEY, PI_KEY, ALGO_KEY, PROB_KEY, CROSS_KEY, MUT_KEY
import pickle


INIT_FROM_FILE = False
SHORTER = True
RUN = False

def MOOstartFromFile():

    shorter = '_shorter' if SHORTER else ''
    with open(f'others/moo_run_options{shorter}.pickle', 'rb') as file:
        run_options_moo = pickle.load(file) #@IgnoreException

    with open(f'others/moo_parameters.pickle', 'rb') as file:
        parameters_moo = pickle.load(file) #@IgnoreException
    
    return run_options_moo, parameters_moo

def defaultStart():
    run_options_moo = {
        PROB_KEY: ['dtlz2'],
        ALGO_KEY: ['nsga3'],
        PI_KEY: ['igd'],
        TERM_KEY: ['n_gen'],
        SEEDS_KEY: 1
    }

    run_options_soo = {
        PROB_KEY: ['ackley', 'griewank', 'rastrigin'],
        ALGO_KEY: ['ga', 'pso'],
        PI_KEY: ['best', 'avg_fitness', '-goal_achieved', 'evals_on_goal'],
        TERM_KEY: ['n_eval'],
        SEEDS_KEY: 3
    }    
    return run_options_moo, run_options_soo

def main():
    
    app = QApplication([])

    if INIT_FROM_FILE:
        run_options_moo, parameters_moo = MOOstartFromFile()
        main_window = MainWindow(run_options_moo=run_options_moo, parameters_moo=parameters_moo)
    else:
        run_options_moo, run_options_soo = defaultStart()
        main_window = MainWindow(run_options_soo, run_options_moo)
        
    if RUN:
        main_window.activeTabs().runButton()
        
    main_window.show()    
    app.exec_()
        
if __name__ == '__main__':
    main()


