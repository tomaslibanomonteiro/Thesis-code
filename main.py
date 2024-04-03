from PyQt5.QtWidgets import QApplication
from frontend.main_window import MyMainWindow
from utils.defines import N_SEEDS_KEY, TERM_KEY, PI_KEY, ALGO_KEY, PROB_KEY


INIT_FROM_FILE = True
RUN = False

def main():
    
    app = QApplication([])

    if INIT_FROM_FILE:
        import pickle

        with open('moo_run_options.pickle', 'rb') as file:
            run_options_moo = pickle.load(file) #@IgnoreException

        with open('moo_parameters.pickle', 'rb') as file:
            parameters_moo = pickle.load(file) #@IgnoreException

        main_window = MyMainWindow(run_options_moo=run_options_moo, parameters_moo=parameters_moo)
    else:
        run_options_moo = {
            PROB_KEY: ['dtlz1', 'dtlz2'],
            ALGO_KEY: ['nsga2', 'nsga3'],
            PI_KEY: ['gd', 'gd+', 'igd+', 'igd'],
            TERM_KEY: ['n_eval'],
            N_SEEDS_KEY: 3
        }

        run_options_soo = {
            PROB_KEY: ['ackley', 'griewank', 'rastrigin'],
            ALGO_KEY: ['ga', 'pso'],
            PI_KEY: ['best'],
            TERM_KEY: ['n_eval'],
            N_SEEDS_KEY: 3
        }

        main_window = MyMainWindow(run_options_soo, run_options_moo)
        
    if RUN:
        main_window.activeTabs().runButton()
        
    main_window.show()    
    app.exec_()
        
if __name__ == '__main__':
    main()


