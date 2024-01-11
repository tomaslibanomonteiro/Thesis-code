from PyQt5.QtWidgets import QHeaderView, QMainWindow, QTabWidget, QVBoxLayout
from PyQt5.uic import loadUi

from backend.get import (get_algorithm, get_performance_indicator, get_problem,
                         get_termination)
from backend.defaults import Defaults
from backend.run import Run, SingleRunArgs
from frontend.my_widgets import MyComboBox, MyMessageBox
from frontend.edit_windows import (EditWindow, ArgsAreSet)
from frontend.run_widgets import ResultFrame
from utils.defines import DESIGNER_MAIN, RUN_OPTIONS_KEYS, DEFAULT_ROW_NUMBERS, DESIGNER_MAIN_TABS

class MyMainWindow(QMainWindow):
    def __init__(self, options_soo = {}, options_moo = {}, defaults_soo = Defaults('soo').dict, defaults_moo = Defaults('moo').dict, ) -> None:
        super().__init__()        
        
        loadUi(DESIGNER_MAIN, self)
        
        self.soo_tabs = MainTabsWidget(options_soo, defaults_soo, 'Single Objective Optimization')
        my_layout_soo = QVBoxLayout()
        my_layout_soo.addWidget(self.soo_tabs)
        my_layout_soo.setStretch(0, 1)
        self.SOOpage.setLayout(my_layout_soo)
        
        self.moo_tabs = MainTabsWidget(options_moo, defaults_moo, 'Multi Objective Optimization')
        my_layout_moo = QVBoxLayout()
        my_layout_moo.addWidget(self.moo_tabs)
        my_layout_moo.setStretch(0, 1)
        self.MOOpage.setLayout(my_layout_moo)
        
        page = 0 if options_soo != {} else 1
        self.stackedWidget.setCurrentIndex(page)
        self.actionSOO.setChecked(page == 0)

        # Add an action to the 'File' menu that switches between the SOO and MOO pages
        self.actionSOO.triggered.connect(self.switch_page)
        self.actionEdit_Run_Options.triggered.connect(self.edit_run_options)
    
    def edit_run_options(self):
        active_tabs = self.soo_tabs if self.actionSOO.isChecked() else self.moo_tabs
        active_tabs.edit_window.show()
        
    def switch_page(self):
        if self.stackedWidget.currentIndex() == 0:
            self.stackedWidget.setCurrentIndex(1)
            self.actionSOO.setChecked(False)
        else:
            self.stackedWidget.setCurrentIndex(0)
            self.actionSOO.setChecked(True)

class MainTabsWidget(QTabWidget):
    def __init__(self, options, defaults, label) -> None:
        super().__init__()

        loadUi(DESIGNER_MAIN_TABS, self)
        
        self.soo_label.setText(label)
        # set run button 
        self.run_button.clicked.connect(self.runButton)
        self.defaults = defaults
        
        # set run options
        if not set(options.keys()).issubset(set(RUN_OPTIONS_KEYS)):
            raise ValueError(f"Invalid run options: expected keys {RUN_OPTIONS_KEYS}, got keys {options.keys()}")
        
        missing_keys = set(RUN_OPTIONS_KEYS) - set(options.keys())
        for key in missing_keys:
            options[key] = []
        self.options = options

        self.setComboBoxes()
        self.SetDefaultRunOptions()                            
        
        # KEYS MUST MATCH 'DEFAULTS' KEYS 
        tab_dicts = {'problem': ('Edit Problems', get_problem, [self.prob_table]), 
                     'algorithm': ('Edit Algorithms', get_algorithm, [self.algo_table]), 
                     'pi': ('Edit Performance Indicators', get_performance_indicator, [self.pi_table]),
                     'termination': ('Edit Termination Criteria', get_termination, [self.term_table])}
        
        self.edit_window = EditWindow(tab_dicts, self.defaults)
                
    def setComboBoxes(self):
        
        # options for each combobox
        
        self.comboBox_items = []
        for key in ['problem', 'algorithm', 'pi', 'termination']:
            options = [obj_id for obj_id in self.defaults[key].keys() if ArgsAreSet(self.defaults[key])]
            self.comboBox_items.append(options)    
        
        # row numbers are the max between the default row numbers and the number of options given to start the app
        start_rows = [len(self.options['prob']), len(self.options['algo']), len(self.options['pi']), len(self.options['term'])]
        row_numbers = [max(x, y) for x, y in zip(DEFAULT_ROW_NUMBERS, start_rows)]

        # columns with comboboxes
        tables_list = [self.prob_table, self.algo_table, self.pi_table, self.term_table]
        
        for table, n_rows, items in zip(tables_list, row_numbers, self.comboBox_items): 
            
            is_termination = True if table == self.term_table else False
            
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
        
        self.n_seeds_SpinBox.setValue(self.options['n_seeds'])
        
        self.setTableWidgetItems(self.term_table, self.options['term'])
        self.setTableWidgetItems(self.pi_table, self.options['pi'])
        self.setTableWidgetItems(self.algo_table, self.options['algo'])
        self.setTableWidgetItems(self.prob_table, self.options['prob'])    
    
    def getRunObject(self):

        moo = self.soo_label.text() == 'Multi Objective Optimization'
        
        # get seed values
        n_seeds = self.n_seeds_SpinBox.value()
        
        frames = self.edit_window.frames
        
        # get the termination object
        term_id = self.term_table.cellWidget(0, 0).currentText()
        if term_id == "":
            warning = MyMessageBox("Please select a Termination Criteria.")
            return None
        term_object = frames['termination'].getObjectFromID(term_id)
        
        # get run args, a list with the arguments for each individual run
        run_args =  []
        algo_id = None
        # get problem object
        for row in range(self.prob_table.rowCount()):
            prob_id = self.prob_table.cellWidget(row, 0).currentText()
            if prob_id != "":
                prob_object = frames['problem'].getObjectFromID(prob_id)
                pf = prob_object.pareto_front() if prob_object.pareto_front else None
                n_obj = prob_object.n_obj
                
                # get algo objects (ref_dirs depends on n_obj) 
                for row in range(self.algo_table.rowCount()):
                    algo_id = self.algo_table.cellWidget(row, 0).currentText()
                    if algo_id != "":
                        algo_id = self.algo_table.cellWidget(row, 0).currentText()
                        algo_object = frames['algorithm'].getObjectFromID(algo_id, pf, n_obj)
                        
                        # get pi objects (pi depends on prob pf)
                        pi_ids, pi_objects = [], []
                        for row in range(self.pi_table.rowCount()):
                            pi_id = self.pi_table.cellWidget(row, 0).currentText()
                            if pi_id != "":
                                pi_ids.append(pi_id)
                                pi_objects.append(frames['pi'].getObjectFromID(pi_id, pf, n_obj))
                    
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
        
        result_frame = ResultFrame(run, f"Run {self.my_layout.count()+1}", self)        
        self.my_layout.addWidget(result_frame)
        