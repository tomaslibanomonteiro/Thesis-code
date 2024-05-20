from PyQt5.QtWidgets import QApplication
from frontend.main_window import MainWindow
from utils.defines import SEEDS_KEY, TERM_KEY, PI_KEY, ALGO_KEY, PROB_KEY, CROSS_KEY, MUT_KEY
import pickle


OTHER_START = False
RUN = False

def otherStart():
    from thesis.results_pso.start import start
    return start()

def defaultStart():
    run_options_moo = {
        PROB_KEY: ['dtlz1', 'dtlz2'],
        ALGO_KEY: ['nsga2', 'nsga3'],
        PI_KEY: ['gd', 'gd+', 'igd+', 'igd'],
        TERM_KEY: ['n_eval'],
        SEEDS_KEY: 3
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

    if OTHER_START:
        run_options, parameters = otherStart()
        main_window = MainWindow(run_options_soo=run_options, parameters_soo=parameters)
    else:
        run_options_moo, run_options_soo = defaultStart()
        main_window = MainWindow(run_options_soo, run_options_moo)
        
    if RUN:
        main_window.activeTabs().runButton()
        
    main_window.show()    
    app.exec_()
        
if __name__ == '__main__':
    main()


