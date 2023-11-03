from PyQt5.QtWidgets import QApplication
from frontend.main_window import MyMainWindow

CLICK_RUN_SOO = False
CLICK_RUN_MOO = False

def main():
    from tests.tests_declaration import options_moo_mixed, options_soo_mixed
    
    # start the QApplication
    app = QApplication([])
    main_window = MyMainWindow(options_soo_mixed, options_moo_mixed)
    main_window.show()
    
    if CLICK_RUN_SOO:
        main_window.soo_tabs.runButton()
    elif CLICK_RUN_MOO:
        main_window.moo_tabs.runButton()
        
    app.exec_()

        
        
if __name__ == '__main__':
    main()


