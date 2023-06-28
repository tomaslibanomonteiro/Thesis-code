from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QHeaderView, QMainWindow
from PyQt5.uic import loadUi

from backend.get import (get_algorithm, get_performance_indicator, get_problem,
                         get_termination)
from backend.get_defaults import Defaults
from backend.run import Run, SingleRunArgs
from frontend.my_widgets import MyComboBox
from frontend.other_windows import (AlgoWindow, ArgsAreSet, RunWindow,
                                    setEditWindow)
from utils.defines import DESIGNER_MAIN, NO_DEFAULT

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        loadUi(DESIGNER_MAIN, self)
        
        # connect button to single or multi objective optimization
        self.defaults_single = Defaults('soo')
        self.defaults_multi = Defaults('moo')
        self.defaults = self.defaults_single
        self.radioButton_moo.toggled.connect(self.objectivesButton)
        
        self.algo_window = None
        self.prob_window = None
        self.pi_window = None
        self.term_window = None
        self.window_combobox_items = None
        self.run_windows = []
        self.initialize()        

        # set run button
        self.PushButton_Run.clicked.connect(self.runButton)
    
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
        
        # set comboboxes from main window
        tables_list = [self.tableWidget_run_pi, self.tableWidget_run_algo, self.tableWidget_run_prob, self.tableWidget_run_term]
        pi_options = [key for key in self.defaults.pi.keys() if ArgsAreSet(self.defaults.pi[key])]
        algo_options = [key for key in self.defaults.algo.keys() if ArgsAreSet(self.defaults.algo[key])]
        prob_options = [key for key in self.defaults.prob.keys() if ArgsAreSet(self.defaults.prob[key])]
        term_options = [key for key in self.defaults.term.keys() if ArgsAreSet(self.defaults.term[key])]
        self.window_combobox_items = [pi_options, algo_options, prob_options, term_options]
        
        for table, items in zip(tables_list, self.window_combobox_items): 
            # strech the table to fit the window
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row in range(table.rowCount()):
                initial_text = table.item(row, 0).text() if table.item(row, 0) else ""
                enabled = True if row == 0 else False
                combobox = MyComboBox(items, initial_text=initial_text, enabled=enabled)
                table.setCellWidget(row, 0, combobox)
                if row < table.rowCount() - 1:
                    combobox.currentIndexChanged.connect(lambda i, table=table, row=row+1: self.enableTableComboBox(table, row, 0))
    
    def enableTableComboBox(self, table, row, col, enabled=True):
        if row < table.rowCount() and col < table.columnCount():
            table.cellWidget(row, col).setEnabled(enabled)
    
    def objectivesButton(self):
        if self.radioButton_moo.isChecked():
            self.defaults = self.defaults_multi
        else:
            self.defaults = self.defaults_single
        self.initialize()
    
    def runButton(self):
        """Get the objects for each column in main window, by matching their ids, with the respective 
        ids in their windows, and instantiating the class with the arguments in the row.
        
        After having the objects, create a run window"""
        
        # get if it is single or multi objective optimization
        moo = self.radioButton_moo.isChecked()
        
        # get seed values
        n_seeds = self.SpinBox_n_seeds.value()
        
        # get the termination object
        term_id = self.tableWidget_run_term.cellWidget(0, 0).currentText()
        term_object = self.term_window.getObjectFromID(term_id)
        
        # get run args
        run_args =  []
        # get problem object
        for row in range(self.tableWidget_run_prob.rowCount()):
            if self.tableWidget_run_prob.cellWidget(row, 0).currentText() == "":
                break
            prob_id = self.tableWidget_run_prob.cellWidget(row, 0).currentText()
            prob_object = self.prob_window.getObjectFromID(prob_id)
            pf = prob_object.pareto_front() if prob_object.pareto_front else None
            n_obj = prob_object.n_obj
            
            # get pi objects (pi depends on prob pf)
            pi_ids, pi_objects = [], []
            for row in range(self.tableWidget_run_pi.rowCount()):
                if self.tableWidget_run_pi.cellWidget(row, 0).currentText() == "":
                    break
                pi_ids.append(self.tableWidget_run_pi.cellWidget(row, 0).currentText())
                pi_objects.append(self.pi_window.getObjectFromID(pi_ids[-1], pf, n_obj))
                
            # get algo objects (ref_dirs depends on n_obj) 
            for row in range(self.tableWidget_run_algo.rowCount()):
                if self.tableWidget_run_algo.cellWidget(row, 0).currentText() == "":
                    break
                algo_id = self.tableWidget_run_algo.cellWidget(row, 0).currentText()
                algo_object = self.algo_window.getObjectFromID(algo_id, pf, n_obj)
                
                # append the arguments for this run
                run_args.append(SingleRunArgs(prob_id, prob_object, algo_id, algo_object, pi_ids, pi_objects))
                    
        # get the run objects and create the run window
        run = Run(run_args, term_id, term_object, n_seeds, moo)
        self.run_windows.append(RunWindow(run,'Run ' + str(len(self.run_windows)+1)))
        