from PyQt5.QtWidgets import QApplication
from frontend.main_window import MyMainWindow
from utils.defines import N_SEEDS_KEY, TERM_KEY, PI_KEY, ALGO_KEY, PROB_KEY

moo_options = {
    PROB_KEY: ['dtlz1', 'dtlz2'],
    ALGO_KEY: ['nsga2', 'nsga3'],
    PI_KEY: ['gd', 'gd+', 'igd+', 'igd'],
    TERM_KEY: ['n_eval'],
    N_SEEDS_KEY: 1
}

soo_options = {
    PROB_KEY: ['ackley', 'griewank', 'rastrigin'],
    ALGO_KEY: ['ga', 'pso'],
    PI_KEY: ['best'],
    TERM_KEY: ['n_eval'],
    N_SEEDS_KEY: 1
}

def main():
    
    app = QApplication([])
    main_window = MyMainWindow(soo_options, moo_options)
    main_window.tabs[0].runButton()
    main_window.tabs[1].runButton()
    
    main_window.show()    
    app.exec_()
        
if __name__ == '__main__':
    main()


