from PyQt5.QtWidgets import QFrame, QTableWidget, QTabWidget
from PyQt5.uic import loadUi
from backend.run import RunThread
from utils.defines import DESIGNER_RESULT_FRAME, PROB_KEY, ALGO_KEY, N_SEEDS_KEY, PI_KEY
from PyQt5.QtCore import Qt
from frontend.my_widgets import MyMessageBox
from PyQt5.QtWidgets import QTabWidget, QTableWidget, QTabBar, QWidget, QSpinBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

from backend.run import RunThread, RunArgs
from frontend.my_widgets import MyComboBox, MyMessageBox
from frontend.edit_window import (EditWindow, ArgsAreSet)
from frontend.main_run_tab import RunTab
from utils.defines import (RUN_OPTIONS_KEYS, DEFAULT_ROW_NUMBERS, DESIGNER_MAIN_TABS, RESULT_LAYOUT_WIDGETS, GET_OBJECT_ERROR, 
                           MAX_RESULT_FRAMES, ALGO_KEY, PROB_KEY, PI_KEY, TERM_KEY, N_SEEDS_KEY)


class MainTabsWidget(QTabWidget):

    def __init__(self, run_options: dict, parameters: dict) -> None:
        super().__init__()

        loadUi(DESIGNER_MAIN_TABS, self)
        
        ############################ GENERAL #################################
        
        self.run_counter = 0
        self.tables_dict = { PROB_KEY: self.prob_table, ALGO_KEY: self.algo_table, 
                            PI_KEY: self.pi_table, TERM_KEY: self.term_table}     
        self.tabCloseRequested.connect(self.closeTab)
        
        # Add a spacer so that the height remains the same when Run Tab is added with the close button
        spacer = QWidget()
        spacer.setFixedHeight(20)  
        spacer.setFixedWidth(1)  
        self.tabBar().setTabButton(0, QTabBar.RightSide, spacer)        
        self.tabBar().setTabButton(1, QTabBar.RightSide, spacer)
        
        # set the n_seeds spinbox
        spin_box = QSpinBox()
        spin_box.setMinimum(1)
        spin_box.setMaximum(99)
        spin_box.setAlignment(Qt.AlignCenter)
        spin_box.setStyleSheet("QSpinBox { min-width: 80px; min-height: 40px; }")
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(spin_box)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.n_seeds_table.setCellWidget(0, 0, widget)    
        
        self.seedsSpinBox = spin_box
        
        ############################ EDIT WINDOW ##############################
        
        self.edit_window = None
        self.setEditWindow(parameters)
        
        ############################ RUN TAB #################################
        
        # set run run_options
        missing_keys = set(RUN_OPTIONS_KEYS) - set(run_options.keys())
        for key in missing_keys:
            run_options[key] = [] if key != N_SEEDS_KEY else 1

        self.initialComboBoxItems(parameters)
        self.runOptions_to_tables(run_options)
        
        # set run button 
        self.run_button.clicked.connect(self.runButton)
        self.fixed_seeds = self.fixed_seeds_checkBox.isChecked()
        self.rand_seeds_checkBox.clicked.connect(self.setSeedCheckBoxes)
        self.fixed_seeds_checkBox.clicked.connect(self.setSeedCheckBoxes)
        
        ############################ RESULTS TAB #################################
        
        # open, save and erase buttons                            
        self.save_results_button.clicked.connect(self.saveAllResults)
        self.open_results_button.clicked.connect(self.openAllResults)
        self.erase_results_button.clicked.connect(self.eraseAllResults)

    def setEditWindow(self, parameters: dict):
        """Set the edit window with the parameters"""
        
        # create edit window
        self.edit_window = EditWindow(parameters)
        self.edit_window.itemUpdates.connect(self.updateComboBoxItems)

    def closeTab(self, index):
        # close the tab with the index
        self.removeTab(index)

    ### Run tab methods ###
    
    def setSeedCheckBoxes(self):
        if self.fixed_seeds:
            self.fixed_seeds = False
            self.rand_seeds_checkBox.setChecked(True)
            self.fixed_seeds_checkBox.setChecked(False)
        else:
            self.fixed_seeds = True
            self.fixed_seeds_checkBox.setChecked(True)
            self.rand_seeds_checkBox.setChecked(False)
            
    def updateComboBoxItems(self, key: str, items: list):
        """Update the items of the comboboxes in the run tab"""
        table = self.tables_dict[key] 
        for row in range(table.rowCount()):
            table.cellWidget(row, 0).updateItems(items)
            
    def initialComboBoxItems(self, parameters):
        """Set one comboBox for each table with the initial items from the parameters"""
        
        keys = RUN_OPTIONS_KEYS.copy() 
        keys.remove(N_SEEDS_KEY)
        
        for key in keys: 
            table = self.tables_dict[key]
            items = [obj_id for obj_id in parameters[key].keys() if ArgsAreSet(parameters[key])]
            combobox = MyComboBox(items, table=table, add_rows= table != self.term_table)
            table.setCellWidget(0, 0, combobox)
                        
    def setTable(self, table: QTableWidget, table_options: list, min_rows: int):
        """Assumes the table has only one combobox. Repeats the comboboxes to the correct number of rows
        and sets the index to the correspondent item in the list. Returns a string with the items that are not available"""
        
        # set the number of rows
        rows = max(min_rows, len(table_options))  
        table.setRowCount(rows)
        
        # set all widgets equal to the first one
        for row in range(rows):
            table.setCellWidget(row, 0, table.cellWidget(0, 0).copy())
        
        # set a combobox for each row with the correct item    
        missing_options = ""    
        for i in range(rows):
            if i < len(table_options) and table_options[i] != "":
                index = table.cellWidget(i, 0).findText(table_options[i])
                if index == -1:
                    missing_options = missing_options + f"{table_options[i]}, "
                    table.cellWidget(i, 0).setCurrentIndex(-1)
                else:
                    table.cellWidget(i, 0).setCurrentIndex(index)
            else:
                """If there are more rows than items, set the rest of the rows to "" """
                table.cellWidget(i, 0).setCurrentIndex(-1)
                
        return missing_options
                
    def runOptions_to_tables(self, run_options: dict):
        
        missing_keys = set(RUN_OPTIONS_KEYS) - set(run_options.keys())
            
        for key in missing_keys:
            run_options[key] = [] if key != N_SEEDS_KEY else 1
            
        # set the combo boxes and the default run_options
        missing_options = self.setTable(self.prob_table, run_options[PROB_KEY], DEFAULT_ROW_NUMBERS[0])
        missing_options += self.setTable(self.algo_table, run_options[ALGO_KEY], DEFAULT_ROW_NUMBERS[1])
        missing_options += self.setTable(self.pi_table, run_options[PI_KEY], DEFAULT_ROW_NUMBERS[2])
        missing_options += self.setTable(self.term_table, run_options[TERM_KEY], DEFAULT_ROW_NUMBERS[3])

        self.seedsSpinBox.setValue(run_options[N_SEEDS_KEY]) 
           
        if missing_options != "":
            MyMessageBox(f"The following run options are not available: {missing_options[:-2]}. \nTo choose them, please add"
                                   " the correspondent IDs to the respective table through the 'Edit Parameters' option of the menu bar.")
            
    def runOptions_to_dict(self):
        """Get the run options from the table into a dictionary"""
        run_options = {}
        keys = RUN_OPTIONS_KEYS.copy()
        keys.remove(N_SEEDS_KEY)
        for key, table in self.tables_dict.items():
            run_options[key] = [table.cellWidget(row, 0).currentText() for row in range(table.rowCount()) if table.cellWidget(row, 0).currentText() != ""]
        run_options[N_SEEDS_KEY] = self.seedsSpinBox.value()
        
        return run_options
    
    def getRunThread(self):

        moo = self.moo_checkBox.isChecked()
        
        # get seed values
        n_seeds = self.seedsSpinBox.value()
        
        tabs = self.edit_window.tabs
        
        # get the termination object
        term_id = self.term_table.cellWidget(0, 0).currentText()
        if term_id == "":
            MyMessageBox("Please select a Termination Criteria.")
            return None
        term_object = tabs[TERM_KEY].getObjectFromID(term_id)
        if term_object is GET_OBJECT_ERROR:
            return None
        # get run args, a list with the arguments for each individual run
        run_args =  []
        algo_id = None
        # get problem object
        for row in range(self.prob_table.rowCount()):
            prob_id = self.prob_table.cellWidget(row, 0).currentText()
            if prob_id != "":
                prob_object = tabs[PROB_KEY].getObjectFromID(prob_id)
                if prob_object is GET_OBJECT_ERROR:
                    return None
                pf = prob_object.pareto_front() if prob_object.pareto_front else None
                n_obj = prob_object.n_obj
                
                # get algo objects (ref_dirs depends on n_obj) 
                for row in range(self.algo_table.rowCount()):
                    algo_id = self.algo_table.cellWidget(row, 0).currentText()
                    if algo_id != "":
                        algo_id = self.algo_table.cellWidget(row, 0).currentText()
                        algo_object = tabs[ALGO_KEY].getObjectFromID(algo_id, pf, n_obj)
                        if algo_object is GET_OBJECT_ERROR:
                            return None
                        # get pi objects (pi depends on prob pf)
                        pi_ids, pi_objects = [], []
                        for row in range(self.pi_table.rowCount()):
                            pi_id = self.pi_table.cellWidget(row, 0).currentText()
                            if pi_id != "":
                                pi_ids.append(pi_id)
                                pi_object = tabs[PI_KEY].getObjectFromID(pi_id, pf, n_obj)
                                if pi_object is GET_OBJECT_ERROR:
                                    return None
                                pi_objects.append(pi_object)
                    
                        # check if any of the arguments is not set
                        if pi_ids == []:
                            MyMessageBox("Please select at least one Performance Indicator.")
                            return None
                    
                        # append the arguments for this run
                        run_args.append(RunArgs(prob_id, prob_object, algo_id, algo_object, pi_ids, pi_objects))
        
        if algo_id is None:
            MyMessageBox("Please select at least one Problem.")   
            return None      
        elif run_args == []:
            MyMessageBox("Please select at least one Algorithm.")
            return None
        else:
            parameters = self.edit_window.getParameters()
            run_options = self.runOptions_to_dict()
        
        # get the run objects and create the run window
        return RunThread(run_args, term_id, term_object, n_seeds, moo, parameters, run_options, self.fixed_seeds)

    def runButton(self):
        """First start the run window, then start the run. The two are separated 
        so that in a test scenario the threads from this window can be trailed 
        so it waits for them to finish before checking results."""
        
        if self.results_layout.count() > MAX_RESULT_FRAMES + RESULT_LAYOUT_WIDGETS - 1:
            MyMessageBox("Please clear one of the results before running again.")
            return
        
        run_thread = self.getRunThread()
        if run_thread is None:
            return

        # create a result frame. get the number of the run from the self.listWidget
        self.run_counter += 1
        result_frame = ResultFrame(self, run_thread, f"Run {self.run_counter}")
        
        # add widget after the last widget in the layout but before the stretch
        self.results_layout.insertWidget(self.results_layout.count() - 1, result_frame)
                
        self.setCurrentIndex(1)     
                   
    ### Results tab methods ###
    
    def noResults(self):
        """Return True if there are no results"""
        if self.results_layout.count() == RESULT_LAYOUT_WIDGETS:
            MyMessageBox("There are no results available.")
            return True
        return False
    
    def saveAllResults(self):
        """Save all results"""
        if self.noResults():
            return
        
        for i in range(RESULT_LAYOUT_WIDGETS-1, self.results_layout.count()-1):
            self.results_layout.itemAt(i).widget().saveResults()
    
    def openAllResults(self):
        """Open all results"""
        if self.noResults():
            return
        
        for i in range(RESULT_LAYOUT_WIDGETS-1, self.results_layout.count()-1):
            self.results_layout.itemAt(i).widget().openTab()
    
    def eraseAllResults(self):
        """Erase all results"""
        if self.noResults():
            return
        
        for i in range(self.results_layout.count()-RESULT_LAYOUT_WIDGETS):
            self.results_layout.itemAt(RESULT_LAYOUT_WIDGETS-1).widget().erase()
            
class ResultFrame(QFrame):
    def __init__(self, tabWidget: QTabWidget, run_thread: RunThread, run_name: str):
        super().__init__()
        loadUi(DESIGNER_RESULT_FRAME, self)
        
        self.run_name = run_name
        self.label.setText(run_name)
        self.tabWidget = tabWidget
                
        # cancel button
        self.cancel_button.clicked.connect(self.cancel_run)

        # make the run in a separate thread (has to be called in another class) 
        self.run_thread = run_thread                
        self.run_thread.progressSignal.connect(self.receiveUpdate)
        self.run_thread.finished.connect(self.afterRun)
        self.run_thread.start()

    def afterRun(self):
        """After the run is finished, add the tab to the run window and show it"""
        if self.run_thread.canceled:
            return
        
        self.tab = RunTab(self.run_thread, self.run_name)
        self.progressBar.setValue(100)
        self.progress_label.setText("")
        self.save_run.setEnabled(True)
        self.save_run.clicked.connect(self.tab.saveRun)
        self.save_data.setEnabled(True)
        self.save_data.clicked.connect(self.tab.saveData)
        self.openTab_button.setEnabled(True)
        self.openTab_button.clicked.connect(self.openTab) 
        self.openTab()

        # change the erase button to cancel button
        self.cancel_button.setText("Erase")
        self.cancel_button.clicked.connect(self.erase)
    
    def closeTab(self, index):
        """Close the tab at the given index"""
        self.tabWidget.removeTab(index)       

    def openTab(self):
        """Check if any of the tabs has the same name as the run, if not, call afterRun"""
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == self.run_name:
                self.tabWidget.setCurrentIndex(i)
                return
        index = self.tabWidget.addTab(self.tab, self.run_name)
        self.tabWidget.setCurrentIndex(index)
    
    def receiveUpdate(self, label: str, value: int):
        """Update the progress bar and label with the current run"""
        if value == -1:
            MyMessageBox(label)
            self.erase()
        else:
            self.progressBar.setValue(value)
            self.progress_label.setText(label)
                
    def erase(self):
        """Erase the run"""
        self.tabWidget.results_layout.removeWidget(self)
        # remove tab if it exists
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == self.run_name:
                self.tabWidget.removeTab(i)
                break
        self.deleteLater()     
    
    def cancel_run(self):
        """Cancel the run"""
        self.run_thread.cancel()
        self.erase()
        """Save the run""" #!
        print("save run to be implemented")