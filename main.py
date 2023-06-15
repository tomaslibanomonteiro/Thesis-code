from frontend.main_window import MyMainWindow
from PyQt5.QtWidgets import QApplication

DEFAULT_RUN_OPTIONS = True
CLICK_RUN_BUTTON = False
MULTI_OBJECTIVE = True

def DefaultRunOptions(main_window: MyMainWindow):
    # set seeds to 3
    main_window.SpinBox_n_seeds.setValue(1)
    # set termination to soo_default
    if MULTI_OBJECTIVE:
        index = main_window.tableWidget_run_term.cellWidget(0, 0).findText('moo_default')
    else:
        index = main_window.tableWidget_run_term.cellWidget(0, 0).findText('soo_default')
    main_window.tableWidget_run_term.cellWidget(0, 0).setCurrentIndex(index)
    # set pi to indexes 1 2 and 3 of combobox
    main_window.tableWidget_run_pi.cellWidget(0, 0).setCurrentIndex(0)
    main_window.tableWidget_run_pi.cellWidget(1, 0).setCurrentIndex(1)
    main_window.tableWidget_run_pi.cellWidget(2, 0).setCurrentIndex(3)
    # set algo to indexes 1 2 and 3 of combobox
    main_window.tableWidget_run_algo.cellWidget(0, 0).setCurrentIndex(0)
    main_window.tableWidget_run_algo.cellWidget(1, 0).setCurrentIndex(2)
    main_window.tableWidget_run_algo.cellWidget(2, 0).setCurrentIndex(3)
    # set prob to indexes 1 2 and 3 of combobox
    main_window.tableWidget_run_prob.cellWidget(0, 0).setCurrentIndex(0)
    main_window.tableWidget_run_prob.cellWidget(1, 0).setCurrentIndex(1)
    main_window.tableWidget_run_prob.cellWidget(2, 0).setCurrentIndex(2)

def main():
    
    # create the application
    app = QApplication([])
    
    # start the main window of the application
    main_window = MyMainWindow()

    if MULTI_OBJECTIVE:
        main_window.radioButton_moo.setChecked(True)
    if DEFAULT_RUN_OPTIONS:
        DefaultRunOptions(main_window)
        if CLICK_RUN_BUTTON:
            main_window.PushButton_Run.click()
        
    main_window.show()
    app.exec_()
    
        
if __name__ == '__main__':
    main()


