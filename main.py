from PyQt5.QtWidgets import QApplication
from frontend.main_window import MyMainWindow
from utils.defines import N_SEEDS_KEY, TERM_KEY, PI_KEY, ALGO_KEY, PROB_KEY

moo_options = {
    'moo': True,
    N_SEEDS_KEY: 2,
    TERM_KEY: ['n_eval'],
    PI_KEY: ['gd', 'gd+', 'igd+', 'igd'],
    ALGO_KEY: ['moead'],
    PROB_KEY: ['carside']
}

soo_options = {}

def main():
    
    app = QApplication([])
    main_window = MyMainWindow(soo_options, moo_options)
    main_window.show()    
    app.exec_()
        
if __name__ == '__main__':
    main()


