from PyQt5.QtWidgets import QFrame, QTableWidget, QTabWidget, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from backend.run import RunThread
from utils.defines import DESIGNER_PROGRESS_FRAME, PROB_KEY, ALGO_KEY, N_SEEDS_KEY, PI_KEY
from PyQt5.QtCore import Qt
from frontend.my_widgets import MyMessageBox
from PyQt5.QtWidgets import QTabWidget, QTableWidget, QTabBar, QWidget, QSpinBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
import pickle

from backend.run import RunThread, RunArgs
from frontend.my_widgets import MyComboBox, MyMessageBox
from frontend.edit_window import EditWindow, ArgsAreSet
from frontend.main_run_tab import RunTab
from utils.defines import (RUN_OPTIONS_KEYS, DEFAULT_ROW_NUMBERS, DESIGNER_FIXED_TABS, HISTORY_LAYOUT_WIDGETS, 
                           MAX_HISTORY_FRAMES, ALGO_KEY, PROB_KEY, PI_KEY, TERM_KEY, N_SEEDS_KEY, MOO_KEY)
from utils.utils import myFileManager, showAndRaise

class MainTabsWidget(QTabWidget):

    def __init__(self, run_options: dict, parameters: dict) -> None:
        super().__init__()

        loadUi(DESIGNER_FIXED_TABS, self)
        
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
        
        ############################ HISTORY TAB #################################
        
        # open, save and erase buttons                            
        self.save_all_runs.clicked.connect(self.saveAllRuns)
        self.save_all_results.clicked.connect(self.saveAllResults)
        self.open_all_tabs.clicked.connect(self.openAllTabs)
        self.load_run.clicked.connect(self.loadRun)
        self.erase_all_runs.clicked.connect(self.eraseAllRuns)

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
        min_rows = DEFAULT_ROW_NUMBERS[2] if self.moo_checkBox.isChecked() else 1 #! tá a mandar mal?
        missing_options += self.setTable(self.pi_table, run_options[PI_KEY], min_rows)
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
        
        run_options[MOO_KEY] = self.moo_checkBox.isChecked()
        
        return run_options
    
    def getIDsFromTable(self, table: QTableWidget):
        """Get the IDs from the table"""
        
        tables = [self.prob_table, self.algo_table, self.pi_table, self.term_table]
        names = ["Problem", "Algorithm", "Performance Indicator", "Termination Criteria"]
        
        ids = [table.cellWidget(row, 0).currentText() for row in range(table.rowCount()) if table.cellWidget(row, 0).currentText() != ""]
        if ids == []:
            MyMessageBox(f"Please select at least one {names[tables.index(table)]}.")
        elif len(ids) != len(set(ids)):
            MyMessageBox(f"Please selected {names[tables.index(table)]}s with different ids.")
            ids = []
        
        return ids
    
    def getRunThread(self):
        
        tabs = self.edit_window.tabs
            
        # get run args, a list with the arguments for each individual run
        run_args, algo_object, prob_object, pi_objects = [], None, None, []

        # get problem object
        for prob_id in self.getIDsFromTable(self.prob_table):
            prob_object = tabs[PROB_KEY].getObjectFromID(prob_id)
            pf = prob_object.pareto_front() if prob_object.pareto_front else None #!
            n_obj = prob_object.n_obj if prob_object.n_obj else None #!
            
            # get algo objects (ref_dirs depends on n_obj) 
            for algo_id in self.getIDsFromTable(self.algo_table):
                algo_object = tabs[ALGO_KEY].getObjectFromID(algo_id, pf, n_obj)
                
                # get pi objects (pi depends on prob pf)
                pi_ids, pi_objects = [], []
                for pi_id in self.getIDsFromTable(self.pi_table):
                    pi_ids.append(pi_id)
                    pi_object = tabs[PI_KEY].getObjectFromID(pi_id, pf, n_obj)
                    pi_objects.append(pi_object)
        
                # check if all objects are not None
                if prob_object and algo_object and not (None in pi_objects):
                    run_args.append(RunArgs(prob_id, prob_object, algo_id, algo_object, pi_ids, pi_objects))
                else:
                    return None
        

        if prob_object and algo_object and not (None in pi_objects) and pi_objects != []:
            # get the termination object
            term_ids = self.getIDsFromTable(self.term_table)
            term_id = term_ids[0] if term_ids != [] else None
            term_object = tabs[TERM_KEY].getObjectFromID(term_id) if term_id != None else None
            
            if term_object is not None:
                # get the rest of the parameters
                moo = self.moo_checkBox.isChecked()
                n_seeds = self.seedsSpinBox.value()
                parameters = self.edit_window.getParameters()
                run_options = self.runOptions_to_dict()
                return RunThread(run_args, term_id, term_object, n_seeds, moo, parameters, run_options, self.fixed_seeds)
        else:
            return None
    
    def setProgressFrame(self, run_thread: RunThread):
        
        if self.history_layout.count() > MAX_HISTORY_FRAMES + HISTORY_LAYOUT_WIDGETS - 1:
            MyMessageBox("Please clear one of the Runs before adding another.")
            return None
        
        # create a progress frame. get the number of the run from the self.listWidget
        self.run_counter += 1
        progress_frame = ProgressFrame(self, run_thread, f"Run {self.run_counter}")
        
        # add widget after the last widget in the layout but before the stretch
        self.history_layout.insertWidget(self.history_layout.count() - 1, progress_frame)
    
        return progress_frame
    
    def runButton(self):
        
        run_thread = self.getRunThread()
        if run_thread is not None:
            progress_frame = self.setProgressFrame(run_thread)
            if progress_frame is not None:
                self.setCurrentIndex(1)
                progress_frame.run_thread.start()    

    def saveRunOptions(self):
        """Save the run options"""
        options_dict = self.runOptions_to_dict()
        
        moo = "MOO" if self.moo_checkBox.isChecked() else "SOO"
        # Open file dialog to select the save location
        myFileManager(f'Save Run Options', f"{moo}_run_options.pickle", options_dict)
    
    def loadRunOptions(self):
        """Load the run options"""

        # Open file dialog to select the file to load
        options_dict = myFileManager('Load Run Options', keys_to_check=RUN_OPTIONS_KEYS, moo=self.moo_checkBox.isChecked())
        
        if options_dict is not None:
            self.runOptions_to_tables(options_dict)
    
    ### History tab methods ###
    
    def noRuns(self):
        if self.history_layout.count() == HISTORY_LAYOUT_WIDGETS:
            MyMessageBox("There are no Runs available.")
            return True
        return False
    
    def saveAllRuns(self):
        if not self.noRuns():     
            for i in range(HISTORY_LAYOUT_WIDGETS-1, self.history_layout.count()-1):
                frame = self.history_layout.itemAt(i).widget()
                if frame.save_run.isEnabled():
                    frame.save_run.click()
        showAndRaise(self)
        
    def saveAllResults(self):
        if not self.noRuns():     
            for i in range(HISTORY_LAYOUT_WIDGETS-1, self.history_layout.count()-1):
                frame = self.history_layout.itemAt(i).widget()
                if frame.save_result.isEnabled():
                    frame.save_result.click()
        showAndRaise(self)
                       
    def openAllTabs(self):
        if not self.noRuns():     
            for i in range(HISTORY_LAYOUT_WIDGETS-1, self.history_layout.count()-1):
                frame = self.history_layout.itemAt(i).widget()
                if frame.openTab_button.isEnabled():
                    frame.openTab()
        showAndRaise(self)
    
    def eraseAllRuns(self):
        if not self.noRuns():     
            for i in range(self.history_layout.count()-HISTORY_LAYOUT_WIDGETS):
                frame = self.history_layout.itemAt(HISTORY_LAYOUT_WIDGETS-1).widget()
                if frame.cancel_button.text() == "Erase":
                    frame.cancel_button.click()
        showAndRaise(self)
        
    def loadRun(self):
        moo = self.moo_checkBox.isChecked()
        keys = ['parameters', 'run_options', 'n_seeds', 'term_id', 'run_args_list', 'data', 'run_counter', 'total_runs', 'canceled', 'best_gen', 'fixed_seeds']
        data = myFileManager('Load Run', keys_to_check=keys, moo=moo)

        if data is not None:
            run_thread = RunThread(data['run_args_list'], data['term_id'], data['n_seeds'], moo, data['parameters'], data['run_options'], data['fixed_seeds'])
            run_thread.data = data['data']
            run_thread.best_gen = data['best_gen']
            progress_frame = self.setProgressFrame(run_thread)
            if progress_frame is not None:
                progress_frame.afterRun()
        
class ProgressFrame(QFrame):
    def __init__(self, tabWidget: MainTabsWidget, run_thread: RunThread, run_name: str):
        super().__init__()
        loadUi(DESIGNER_PROGRESS_FRAME, self)
        
        self.run_name = run_name
        self.label.setText(run_name)
        self.tabWidget = tabWidget
                
        # cancel button        
        self.cancel_button.clicked.connect(self.cancelRun)
    
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
        self.save_result.setEnabled(True)
        self.openTab_button.setEnabled(True)
        self.reproduce_run.setEnabled(True)
        self.save_run.clicked.connect(self.tab.saveRun)
        self.save_result.clicked.connect(self.tab.saveResult)
        self.openTab_button.clicked.connect(self.openTab) 
        self.reproduce_run.clicked.connect(self.reproduceRun)
        
        self.openTab()

        # change the erase button to cancel button
        self.cancel_button.setText("Erase")
        self.cancel_button.clicked.connect(self.erase)
    
    def closeTab(self, index):
        """Close the tab at the given index"""
        self.tabWidget.removeTab(index)       

    def receiveUpdate(self, label: str, value: int):
        """Update the progress bar and label with the current run"""
        if value == -1:
            MyMessageBox(label)
            self.erase()
        else:
            self.progressBar.setValue(value)
            self.progress_label.setText(label)

    # Button methods
                
    def openTab(self):
        """Check if any of the tabs has the same name as the run, if not, call afterRun"""
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == self.run_name:
                self.tabWidget.setCurrentIndex(i)
                return
        index = self.tabWidget.addTab(self.tab, self.run_name)
        self.tabWidget.setCurrentIndex(index)
    
    def reproduceRun(self):
        """Reproduce the run"""
        # make a dialog warning that it will erase the current run options and parameters, 
        # and ask if the user wants to proceed
        reply = QMessageBox.question(self, 'Warning',
            "This will erase the current run options and parameters, and replace them with" 
            " the ones from the run. Do you want to proceed?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.tabWidget.setEditWindow(self.run_thread.parameters)
            self.tabWidget.runOptions_to_tables(self.run_thread.run_options)
            self.tabWidget.setCurrentIndex(0)

    def erase(self):
        """Erase the run"""
        self.tabWidget.history_layout.removeWidget(self)
        # remove tab if it exists
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == self.run_name:
                self.tabWidget.removeTab(i)
                break
        self.deleteLater()     
    
    def cancelRun(self):
        """Cancel the run"""
        self.run_thread.cancel()
        self.erase()
