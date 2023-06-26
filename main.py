from frontend.main_window import MyMainWindow
from PyQt5.QtWidgets import QApplication

DEFAULT_RUN_OPTIONS = True
CLICK_RUN_BUTTON = False
MULTI_OBJECTIVE = True

def setTableWidgetItems(tableWidget, items):
    for i, item in enumerate(items):
        index = tableWidget.cellWidget(i, 0).findText(item)
        tableWidget.cellWidget(i, 0).setCurrentIndex(index)
        
def DefaultRunOptions(main_window: MyMainWindow):
    # set seeds to 3
    main_window.SpinBox_n_seeds.setValue(1)
    # set termination to soo_default
    if MULTI_OBJECTIVE:
        # set termination 
        setTableWidgetItems(main_window.tableWidget_run_term, ['n_gen_default'])
        # set pi 
        setTableWidgetItems(main_window.tableWidget_run_pi, ['gd_default', 'gd+_default', 'igd+_default'])
        # set algo 
        setTableWidgetItems(main_window.tableWidget_run_algo, ['nsga2_default', 'nsga3_default', 'ctaea_default'])
        # set prob
        setTableWidgetItems(main_window.tableWidget_run_prob, ['bnh_default','ctp1_default', 'carside_default'])
        # set seed
        main_window.SpinBox_n_seeds.setValue(1)        
    else:
        # set termination 
        setTableWidgetItems(main_window.tableWidget_run_term, ['n_gen_default'])
        # set pi 
        setTableWidgetItems(main_window.tableWidget_run_pi, ['best_default'])
        # set algo 
        setTableWidgetItems(main_window.tableWidget_run_algo, ['ga_default', 'pso_default', 'de_default'])
        # set prob
        setTableWidgetItems(main_window.tableWidget_run_prob, ['ackley_default','g1_default','griewank_default','rastrigin_default','rosenbrock_default'])
        # set seed
        main_window.SpinBox_n_seeds.setValue(1)        

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


