from frontend.main_window import MyMainWindow
from PyQt5.QtWidgets import QApplication
from backend.get_defaults import Defaults

DEFAULT_RUN_OPTIONS = True

def setRunOptions(main_window: MyMainWindow):
    # set seeds to 3
    main_window.SpinBox_n_seeds.setValue(3)
    # set termination to soo_default
    main_window.comboBox_term.setCurrentText("soo_default")
    # set pi to indexes 1 2 and 3 of combobox
    main_window.tableWidget_run_pi.cellWidget(0, 0).setCurrentIndex(1)
    main_window.tableWidget_run_pi.cellWidget(1, 0).setCurrentIndex(2)
    main_window.tableWidget_run_pi.cellWidget(2, 0).setCurrentIndex(3)
    # set algo to indexes 1 2 and 3 of combobox
    main_window.tableWidget_run_algo.cellWidget(0, 0).setCurrentIndex(4)
    main_window.tableWidget_run_algo.cellWidget(1, 0).setCurrentIndex(10)
    main_window.tableWidget_run_algo.cellWidget(2, 0).setCurrentIndex(3)
    # set prob to indexes 1 2 and 3 of combobox
    main_window.tableWidget_run_prob.cellWidget(0, 0).setCurrentIndex(1)
    main_window.tableWidget_run_prob.cellWidget(1, 0).setCurrentIndex(2)
    main_window.tableWidget_run_prob.cellWidget(2, 0).setCurrentIndex(3)

def main():
    
    # create the application
    app = QApplication([])
    
    # get the default values for algo prob and term in the pymoo framework
    defaults = Defaults()
    
    # start the main window of the application
    main_window = MyMainWindow(defaults)

    if DEFAULT_RUN_OPTIONS:
        setRunOptions(main_window)
        # press the run button
        main_window.PushButton_Run.click()
        
    main_window.show()
    app.exec_()
    
        
if __name__ == '__main__':
    main()


