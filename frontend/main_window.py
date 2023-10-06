from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QHeaderView, QMainWindow
from PyQt5.uic import loadUi

from backend.get import (get_algorithm, get_performance_indicator, get_problem,
                         get_termination)
from backend.get_defaults import Defaults
from backend.run import Run, SingleRunArgs
from frontend.my_widgets import MyComboBox, MyMessageBox
from frontend.edit_windows import (AlgoWindow, ArgsAreSet, setEditWindow)
from frontend.run_window import RunWindow
from utils.defines import DESIGNER_MAIN, RUN_OPTIONS_KEYS, DEFAULT_ROW_NUMBERS

class MyMainWindow(QMainWindow):
    def __init__(self, moo = True, options = {}, defaults_soo = Defaults('soo'), defaults_moo = Defaults('moo')) -> None:
        super().__init__()        
        
        loadUi(DESIGNER_MAIN, self)
        
        # set run button
        self.PushButton_Run.clicked.connect(self.runButton)

        # connect button to single or multi objective optimization
        self.defaults_soo = defaults_soo
        self.defaults_moo = defaults_moo
        self.defaults = self.defaults_moo if moo else self.defaults_soo
        self.radioButton_moo.toggled.connect(self.objectivesButton)
        
        # set window variables
        self.algo_window = None
        self.prob_window = None
        self.pi_window = None
        self.term_window = None
        self.window_combobox_items = None
        self.run_windows = []
        
        # set run options
        if not set(options.keys()).issubset(set(RUN_OPTIONS_KEYS)):
            raise ValueError(f"Invalid run options: expected keys {RUN_OPTIONS_KEYS}, got keys {options.keys()}")
        
        missing_keys = set(RUN_OPTIONS_KEYS) - set(options.keys())
        for key in missing_keys:
            options[key] = []
        self.options = options
       
        self.initialize()        
        self.SetDefaultRunOptions()

    def initialize(self):
        """Initialize the main window regarding the default values in the comboboxes and the edit windows."""
        
        # set other windows
        self.prob_window = setEditWindow(self.pushButton_edit_prob, "Edit Problems", self.defaults.prob, get_problem, self.defaults)
        self.pi_window = setEditWindow(self.pushButton_edit_pi, "Edit Performance Indicators", self.defaults.pi, get_performance_indicator, self.defaults)
        self.term_window = setEditWindow(self.pushButton_edit_term, "Edit Terminations", self.defaults.term, get_termination, self.defaults)
        
        self.algo_window = AlgoWindow("Edit Algorithms", self.defaults.algo, get_algorithm, self.defaults)
        self.pushButton_edit_algo.clicked.connect(self.algo_window.show)
                            
        self.setComboBoxes()
            
    def setComboBoxes(self):
        
       
        # options for each combobox
        pi_options = [key for key in self.defaults.pi.keys() if ArgsAreSet(self.defaults.pi[key])]
        algo_options = [key for key in self.defaults.algo.keys() if ArgsAreSet(self.defaults.algo[key])]
        prob_options = [key for key in self.defaults.prob.keys() if ArgsAreSet(self.defaults.prob[key])] 
        term_options = [key for key in self.defaults.term.keys() if ArgsAreSet(self.defaults.term[key])]
        
        self.window_combobox_items = [prob_options, algo_options, pi_options, term_options]
        
        # row numbers are the max between the default row numbers and the number of options given to start the app
        start_rows = [len(self.options['prob']), len(self.options['algo']), len(self.options['pi']), len(self.options['term'])]
        row_numbers = [max(x, y) for x, y in zip(DEFAULT_ROW_NUMBERS, start_rows)]

        # columns with comboboxes
        tables_list = [self.tableWidget_run_prob, self.tableWidget_run_algo, self.tableWidget_run_pi, self.tableWidget_run_term]
        
        for table, n_rows, items in zip(tables_list, row_numbers, self.window_combobox_items): 
            
            is_termination = True if table == self.tableWidget_run_term else False
            
            # add rows to the table
            table.setRowCount(n_rows)
            
            # strech the table to fit the window
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row in range(table.rowCount()):
                combobox = MyComboBox(items, table=table, add_rows=not is_termination)
                table.setCellWidget(row, 0, combobox)
    
    def setTableWidgetItems(self, tableWidget, items):
        for i, item in enumerate(items):
            index = tableWidget.cellWidget(i, 0).findText(item)
            tableWidget.cellWidget(i, 0).setCurrentIndex(index)
            
    def SetDefaultRunOptions(self):
        if self.options == {}:
            return
        
        self.radioButton_moo.setChecked(self.options['moo'])
        self.SpinBox_n_seeds.setValue(self.options['n_seeds'])
        
        self.setTableWidgetItems(self.tableWidget_run_term, self.options['term'])
        self.setTableWidgetItems(self.tableWidget_run_pi, self.options['pi'])
        self.setTableWidgetItems(self.tableWidget_run_algo, self.options['algo'])
        self.setTableWidgetItems(self.tableWidget_run_prob, self.options['prob'])
    
    def objectivesButton(self):
        if self.radioButton_moo.isChecked():
            self.defaults = self.defaults_moo
        else:
            self.defaults = self.defaults_soo
        self.initialize()
    
    def getRunObject(self):
        # get if it is single or multi objective optimization
        moo = self.radioButton_moo.isChecked()
        
        # get seed values
        n_seeds = self.SpinBox_n_seeds.value()
        
        # get the termination object
        term_id = self.tableWidget_run_term.cellWidget(0, 0).currentText()
        if term_id == "":
            warning = MyMessageBox("Please select a Termination Criteria.")
            return None
        term_object = self.term_window.getObjectFromID(term_id)
        
        # get run args, a list with the arguments for each individual run
        run_args =  []
        algo_id = None
        # get problem object
        for row in range(self.tableWidget_run_prob.rowCount()):
            prob_id = self.tableWidget_run_prob.cellWidget(row, 0).currentText()
            if prob_id != "":
                prob_object = self.prob_window.getObjectFromID(prob_id)
                pf = prob_object.pareto_front() if prob_object.pareto_front else None
                n_obj = prob_object.n_obj
                
                # get algo objects (ref_dirs depends on n_obj) 
                for row in range(self.tableWidget_run_algo.rowCount()):
                    algo_id = self.tableWidget_run_algo.cellWidget(row, 0).currentText()
                    if algo_id != "":
                        algo_id = self.tableWidget_run_algo.cellWidget(row, 0).currentText()
                        algo_object = self.algo_window.getObjectFromID(algo_id, pf, n_obj)
                        
                        # get pi objects (pi depends on prob pf)
                        pi_ids, pi_objects = [], []
                        for row in range(self.tableWidget_run_pi.rowCount()):
                            pi_id = self.tableWidget_run_pi.cellWidget(row, 0).currentText()
                            if pi_id != "":
                                pi_ids.append(pi_id)
                                pi_objects.append(self.pi_window.getObjectFromID(pi_id, pf, n_obj))
                    
                        # check if any of the arguments is not set
                        if pi_ids == []:
                            warning = MyMessageBox("Please select at least one Performance Indicator.")
                            return None
                    
                        # append the arguments for this run
                        run_args.append(SingleRunArgs(prob_id, prob_object, algo_id, algo_object, pi_ids, pi_objects))
        
        if algo_id is None:
            warning = MyMessageBox("Please select at least one Problem.")   
            return None      
        elif run_args == []:
            warning = MyMessageBox("Please select at least one Algorithm.")
            return None
        
        # get the run objects and create the run window
        return Run(run_args, term_id, term_object, n_seeds, moo)
        
    def runButton(self):
        """First start the run window, then start the run. The two are separated 
        so that in a test scenario the threads from this window can be trailed 
        so it waits for them to finish before checking results."""
        run = self.getRunObject()
        if run is None:
            return
        run_window = RunWindow(run,'Run ' + str(len(self.run_windows)+1))
        self.run_windows.append(run_window)
        self.run_windows[-1].startRun()