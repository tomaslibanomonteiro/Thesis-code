from PyQt5.QtWidgets import QApplication
from frontend.main_window import MyMainWindow

CLICK_RUN = False

def main():
    from tests.tests_declaration import options_moo_mixed, options_soo_mixed
    options = options_moo_mixed
    
    # start the QApplication
    app = QApplication([])
    main_window = MyMainWindow(options['moo'], options)
    main_window.show()
    
    if CLICK_RUN:
        main_window.runButton()
        
    app.exec_()

        
        
if __name__ == '__main__':
    main()


