from PyQt5.QtWidgets import QApplication
from frontend.main_window import MyMainWindow

CLICK_RUN_SOO = False
CLICK_RUN_MOO = False

def main():
    from tests.tests_declaration import run_options_soo_simple, run_options_soo_mixed, run_options_moo_simple, run_options_moo_mixed
    
    # start the QApplication
    app = QApplication([])
    main_window = MyMainWindow(run_options_moo=run_options_moo_mixed)
    main_window.show()
    
    if CLICK_RUN_SOO:
        main_window.soo_tabs.runButton()

    elif CLICK_RUN_MOO:
        main_window.moo_tabs.runButton()
    
    # click to edit parameters
    main_window.editParameters()
    main_window.activePage().edit_window.openRunOptions()
    
    app.exec_()
        
if __name__ == '__main__':
    main()


