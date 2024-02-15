from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QTableWidget, QTabBar, QWidget, QSpinBox, QHBoxLayout, QMessageBox, QFrame

from backend.run import RunThread
from backend.run import RunThread, RunArgs

from frontend.my_widgets import MyComboBox
from frontend.edit_window import EditWindow, ArgsAreSet
from frontend.main_run_tab import RunTab
from utils.utils import myFileManager, showAndRaise, getAvailableName, MyMessageBox
from utils.defines import (DESIGNER_PROGRESS_FRAME,RUN_OPTIONS_KEYS, DEFAULT_ROW_NUMBERS, DESIGNER_FIXED_TABS, HISTORY_LAYOUT_WIDGETS,
                           MAX_HISTORY_FRAMES, ALGO_KEY, PROB_KEY, PI_KEY, TERM_KEY, N_SEEDS_KEY, MOO_KEY, OPERATORS_ARGS_DICT, RUN_OPTIONS_ARGS_DICT)

class MainTabsWidget(QTabWidget):
    """
    Central Widget in Main Window. Contains the Fixed Tabs: 
    
    Run Options Tab
    ---------------- 
    where the user can choose the problems to be solved by the algorithms given a certain termination,
    and over a determined number of seeds. and Main widget that contains all the tabs for the application.
    It provides methods for managing run options, getting IDs from tables, creating run threads,
    handling button actions, managing history tab methods, and loading run options.

    Important Methods:
    - updateComboBoxItems(key: str, items: list): Updates the items of the comboboxes in the "Run" tab,
    connected to the signal emited by the EditText widgets in the Edit Window that contain the respective IDs
    - dictToTables(run_options: dict): Populates the tables with data from a run_options dictionary.
    - tablesToDict: Converts the run options from the table into a dictionary.
    - getIDsFromTable: Retrieves the IDs from the given table.
    - getRunThread: Constructs a run thread based on the current settings.
    - runButton: Starts the run thread if it is not None.
    - saveRunOptions: Saves the current run options to a file.
    - loadRunOptions: Loads run options from a file.
    
    Run History Tab
    ---------------- 
    After a Run is finished, a progress frame is added to the history tab. Here, the 
    user can see the Run progress, and after it is finished, save the Run object to reproduce it in the future, 
    or just the results of it. Furthermore, a previously saved Run can be loaded and open to see and plot 
    the results within the app, in the dedicated Run Tab
    
    Important methods:
    - setProgressFrame: Sets up a progress frame for a given run thread.
    - saveAllRuns: Saves all available runs.
    - saveAllResults: Saves all results from the runs.
    - openAllTabs: Opens all tabs for the runs.
    - eraseAllRuns: Erases all runs.
    - loadRun: Loads a run from a file.
    
    Attributes
    ----------------
        run_counter: A counter for the number of runs.
        tables_dict: A dictionary mapping keys to table widgets.
        seedsSpinBox: A QSpinBox widget for setting the number of seeds.
        fixed_seeds: A boolean indicating whether the seeds are fixed.
        edit_window: An instance of the EditWindow class.
    """
    def __init__(self, run_options: dict, parameters: dict) -> None:
        super().__init__()

        loadUi(DESIGNER_FIXED_TABS, self)
                
        self.run_counter = 0
        self.tables_dict = {PROB_KEY: self.prob_table, ALGO_KEY: self.algo_table, PI_KEY: self.pi_table, TERM_KEY: self.term_table}     
        
        self.seedsSpinBox = self.setUI()
        self.fixed_seeds = self.fixed_seeds_checkBox.isChecked()

        # set edit window        \
        self.edit_window = EditWindow(parameters, self.moo_checkBox.isChecked())
        self.edit_window.itemUpdates.connect(self.updateComboBoxItems)
        
        # set run run_options
        self.initialComboBoxItems(parameters)
        
        missing_keys = set(RUN_OPTIONS_KEYS) - set(run_options.keys())
        for key in missing_keys:
            run_options[key] = [] if key != N_SEEDS_KEY else 1
        self.dictToTables(run_options)
        
    def setUI(self):
        
        self.tabCloseRequested.connect(self.closeTab)

        ######## RUN TAB ########

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
        
        self.run_button.clicked.connect(self.runButton)
        self.rand_seeds_checkBox.clicked.connect(self.setSeedCheckBoxes)
        self.fixed_seeds_checkBox.clicked.connect(self.setSeedCheckBoxes)
        self.save_run_options.clicked.connect(self.saveRunOptions)
        self.load_run_options.clicked.connect(self.loadRunOptions)
        
        ######## HISTORY TAB ########
        
        # open, save and erase buttons                            
        self.save_all_runs.clicked.connect(self.saveAllRuns)
        self.save_all_results.clicked.connect(self.saveAllResults)
        self.open_all_tabs.clicked.connect(self.openAllTabs)
        self.load_run.clicked.connect(self.loadRun)
        self.erase_all_runs.clicked.connect(self.eraseAllRuns)

        return spin_box
        
    def closeTab(self, index):
        # close the tab with the index
        self.removeTab(index)

    ### RUN TAB METHODS ###
    
    # edit tables
    
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
                
    def dictToTables(self, run_options: dict):
        
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
    
    # extract from tables
            
    def tablesToDict(self):
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
            
            if prob_object == None:
                return None
            # get algo objects (ref_dirs depends on n_obj) 
            for algo_id in self.getIDsFromTable(self.algo_table):
                algo_object = tabs[ALGO_KEY].getObjectFromID(algo_id, pf, n_obj)
                
                if algo_object == None:
                    return None
                # get pi objects (pi depends on prob pf)
                pi_ids, pi_objects = [], []
                for pi_id in self.getIDsFromTable(self.pi_table):
                    pi_ids.append(pi_id)
                    pi_object = tabs[PI_KEY].getObjectFromID(pi_id, pf, n_obj)
                    pi_objects.append(pi_object)
                    if pi_object == None:
                        return None
                    
                    run_args.append(RunArgs(prob_id, prob_object, algo_id, algo_object, pi_ids, pi_objects))

        # get the termination object
        term_ids = self.getIDsFromTable(self.term_table)
        term_id = term_ids[0] if term_ids != [] else None
        term_object = tabs[TERM_KEY].getObjectFromID(term_id) if term_id != None else None
            
        if term_object is not None:
            # get the rest of the parameters
            moo = self.moo_checkBox.isChecked()
            n_seeds = self.seedsSpinBox.value()
            parameters = self.edit_window.tabsToDict()
            run_options = self.tablesToDict()
            return RunThread(run_args, term_id, term_object, n_seeds, moo, parameters, run_options, self.fixed_seeds)
        else:
            return None
    
    # Button methods
    
    def runButton(self):
        
        run_thread = self.getRunThread()
        if run_thread is not None:
            progress_frame = self.setProgressFrame(run_thread)
            if progress_frame is not None:
                self.setCurrentIndex(1)
                progress_frame.run_thread.start()    

    def saveRunOptions(self):
        """Save the run options"""
        options_dict = self.tablesToDict()
        
        moo = "MOO" if self.moo_checkBox.isChecked() else "SOO"
        # Open file dialog to select the save location
        myFileManager(f'Save Run Options', f"{moo}_run_options.pickle", options_dict)
    
    def loadRunOptions(self):
        """Load the run options"""

        # Open file dialog to select the file to load
        options_dict, _ = myFileManager('Load Run Options', keys_to_check=RUN_OPTIONS_KEYS, moo=self.moo_checkBox.isChecked())
        
        if options_dict is not None:
            self.dictToTables(options_dict)
    
    ### HISTORY TAB METHODS ###

    def setProgressFrame(self, run_thread: RunThread, name:str=None):
        
        if self.history_layout.count() > MAX_HISTORY_FRAMES + HISTORY_LAYOUT_WIDGETS - 1:
            MyMessageBox("Please clear one of the Runs before adding another.")
            return None
        
        # create a progress frame. get the number of the run from the self.listWidget
        self.run_counter += 1
        
        if name is None:
            name = f"Run {self.run_counter}"
        curr_names = [self.history_layout.itemAt(i).widget().run_name for i in range(HISTORY_LAYOUT_WIDGETS-1, self.history_layout.count()-1)]
        name = getAvailableName(name, curr_names)
        progress_frame = ProgressFrame(self, run_thread, name)
        
        # add widget after the last widget in the layout but before the stretch
        self.history_layout.insertWidget(self.history_layout.count() - 1, progress_frame)
    
        return progress_frame
    
    def noRuns(self):
        if self.history_layout.count() == HISTORY_LAYOUT_WIDGETS:
            MyMessageBox("There are no Runs available.")
            return True
        return False
    
    # button methods
    
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
        keys = ['parameters', 'run_options', 'data', 'best_gen', 'run_counter']
        loaded_data, filename = myFileManager('Load Run', keys_to_check=keys, moo=moo)

        if loaded_data is not None:
            if not (isinstance(loaded_data['run_options'], dict) and isinstance(loaded_data['parameters'], dict)):
                MyMessageBox("The Run dictionary is not in the correct format. Must have 'parameters' and 'run_options' keys.")
                return
            param_keys = list(OPERATORS_ARGS_DICT.keys()) + list(RUN_OPTIONS_ARGS_DICT.keys()) + [MOO_KEY]
            if set(loaded_data['parameters'].keys()) != set(param_keys):
                MyMessageBox(f"The parameters must have the following keys: {param_keys}.")
                return
            if set(loaded_data['run_options'].keys()) != set(RUN_OPTIONS_KEYS + [MOO_KEY]):
                MyMessageBox(f"The run options must have the following keys: {RUN_OPTIONS_KEYS + [MOO_KEY]}.")
                return
            curr_parameters = self.edit_window.tabsToDict()
            curr_run_options = self.tablesToDict()
            self.edit_window.dictToTabs(loaded_data['parameters'])
            self.dictToTables(loaded_data['run_options'])
            run_thread = self.getRunThread()
            self.edit_window.dictToTabs(curr_parameters)
            self.dictToTables(curr_run_options)
            if run_thread is not None:
                run_thread.data, run_thread.best_gen, run_thread.run_counter = loaded_data['data'], loaded_data['best_gen'], loaded_data['run_counter']
                progress_frame = self.setProgressFrame(run_thread, filename)
                if progress_frame is not None:
                    progress_frame.afterRun()
                            
class ProgressFrame(QFrame):
    """
    Frame created to see a certain Run progress and allowing certain actions after it is finished.
    It is connected to the RunThread through a signal that updates the progress bar and label.

    Attributes:
    -----------
    main_tabs : MainTabsWidget
        The main tabs widget of the application.
    run_thread : RunThread
        The thread that is running the task.
    run_name : str
        The name of the run.
    run_tab : RunTab
        The tab that displays the results of the run.

    Methods:
    --------
    __init__(main_tabs, run_thread, run_name):
        Initializes the ProgressFrame with the main tabs widget, the run thread, and the run name.
    afterRun():
        Handles the actions to be performed after the run thread finishes.
    closeTab(index):
        Removes a tab from the tab widget at the given index.
    receiveUpdate(value, text):
        Updates the progress bar and label with the current run.
    openTab():
        Opens a tab with the results of the run.
    reproduceRun():
        Reproduces the run, setting the parameters and run options of the App to the ones of the Run.
    erase():
        Removes the ProgressFrame from the history layout and deletes it.
    cancelRun():
        Cancels the run thread and calls the erase method.
    """    
    def __init__(self, tabWidget: MainTabsWidget, run_thread: RunThread, run_name: str):
        super().__init__()
        loadUi(DESIGNER_PROGRESS_FRAME, self)
        
        self.run_name = run_name
        self.tabWidget = tabWidget
        self.run_thread = run_thread                
        
        self.run_thread.progressSignal.connect(self.receiveUpdate)
        self.run_thread.finished.connect(self.afterRun)

        # UI        
        self.label.setText(run_name)
        self.cancel_button.clicked.connect(self.cancelRun)
    
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
            self.tabWidget.edit_window.dictToTabs(self.run_thread.parameters)
            self.tabWidget.dictToTables(self.run_thread.run_options)
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

