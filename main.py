from PyQt5.QtWidgets import QApplication
from frontend.main_window import MyMainWindow

CLICK_RUN_SOO = True
CLICK_RUN_MOO = False

def main():
    from tests.tests_declaration import options_soo_simple, options_soo_mixed, options_moo_simple, options_moo_mixed
    
    # start the QApplication
    app = QApplication([])
    main_window = MyMainWindow(options_soo_simple, options_moo_simple)
    main_window.show()
    
    if CLICK_RUN_SOO:
        for i in range(1):
            main_window.soo_tabs.runButton()

    elif CLICK_RUN_MOO:
        main_window.moo_tabs.runButton()
        
    app.exec_()
        
if __name__ == '__main__':
    main()


