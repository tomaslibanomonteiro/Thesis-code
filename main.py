from PyQt5.QtWidgets import QApplication
from frontend.main_window import MyMainWindow
from utils.defines import SEEDS_KEY, TERM_KEY, PI_KEY, ALGO_KEY, PROB_KEY, CROSS_KEY, MUT_KEY


INIT_FROM_FILE = False
RUN = True

def MOOstartFromFile():
    
    from backend.defaults import Defaults
    import pickle

    # Load the first dictionary from the first pickle file
    with open('moo_parameters.pickle', 'rb') as file1:
        dict1 = pickle.load(file1)

    dict2 = Defaults(moo=True).parameters

    dict2[PROB_KEY] = dict1[PROB_KEY]
    dict2[ALGO_KEY]['nsga3'] = dict1[ALGO_KEY]['nsga3']
    dict2[ALGO_KEY]['moead-pbi'] = dict1[ALGO_KEY]['moead-pbi']
    dict2[ALGO_KEY]['moead-tch'] = dict1[ALGO_KEY]['moead-tch']
    dict2[ALGO_KEY]['nsga3'] = dict1[ALGO_KEY]['nsga3']
    dict2[TERM_KEY]['n_gen'] = dict1[TERM_KEY]['n_gen']
    dict2[CROSS_KEY] = dict1[CROSS_KEY]
    dict2[MUT_KEY] = dict1[MUT_KEY]

    # Save the joined dictionary in another pickle file
    with open('moo_parameters.pickle', 'wb') as output_file:
        pickle.dump(dict2, output_file)

    with open('moo_run_options2.pickle', 'rb') as file:
        run_options_moo = pickle.load(file) #@IgnoreException

    with open('moo_parameters.pickle', 'rb') as file:
        parameters_moo = pickle.load(file) #@IgnoreException
    
    return run_options_moo, parameters_moo

def defaultStart():
    run_options_moo = {
        PROB_KEY: ['dtlz1', 'dtlz2'],
        ALGO_KEY: ['nsga2', 'nsga3'],
        PI_KEY: ['gd', 'gd+', 'igd+', 'igd'],
        TERM_KEY: ['n_eval'],
        SEEDS_KEY: 2
    }

    run_options_soo = {
        # PROB_KEY: ['ackley', 'griewank', 'rastrigin'],
        # ALGO_KEY: ['ga', 'pso'],
        # PI_KEY: ['best'],
        # TERM_KEY: ['n_eval'],
        # SEEDS_KEY: 3
    }    
    return run_options_moo, run_options_soo

def main():
    
    app = QApplication([])

    if INIT_FROM_FILE:
        run_options_moo, parameters_moo = MOOstartFromFile()
        main_window = MyMainWindow(run_options_moo=run_options_moo, parameters_moo=parameters_moo)
    else:
        run_options_moo, run_options_soo = defaultStart()
        main_window = MyMainWindow(run_options_soo, run_options_moo)
        
    if RUN:
        main_window.activeTabs().runButton()
        
    main_window.show()    
    app.exec_()
        
if __name__ == '__main__':
    main()


