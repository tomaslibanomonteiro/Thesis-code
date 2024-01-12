from PyQt5.QtWidgets import QHeaderView, QMainWindow, QTabWidget, QVBoxLayout, QTableWidget, QTabBar, QFileDialog
from PyQt5.uic import loadUi

from backend.get import (get_algorithm, get_performance_indicator, get_problem,
                         get_termination)
from backend.defaults import Defaults
from backend.run import RunThread, SingleRunArgs
from frontend.my_widgets import MyComboBox, MyMessageBox
from frontend.edit_windows import (EditWindow, ArgsAreSet)
from frontend.main_window_frames import ResultFrame
from utils.defines import DESIGNER_MAIN, RUN_OPTIONS_KEYS, DEFAULT_ROW_NUMBERS, DESIGNER_MAIN_TABS
import pickle

class MyMainWindow(QMainWindow):
    def __init__(self, options_soo = {}, options_moo = {}, defaults_soo = Defaults('soo').dict, defaults_moo = Defaults('moo').dict, ) -> None:
        super().__init__()        
        
        loadUi(DESIGNER_MAIN, self)

        # Create single objective optimization tab
        self.soo_tabs = MainTabsWidget(options_soo, defaults_soo, 'Single Objective Optimization')
        my_layout_soo = QVBoxLayout()
        my_layout_soo.addWidget(self.soo_tabs)
        my_layout_soo.setStretch(0, 1)
        self.SOOpage.setLayout(my_layout_soo)
        
        # Create multi objective optimization tab
        self.moo_tabs = MainTabsWidget(options_moo, defaults_moo, 'Multi Objective Optimization')
        my_layout_moo = QVBoxLayout()
        my_layout_moo.addWidget(self.moo_tabs)
        my_layout_moo.setStretch(0, 1)
        self.MOOpage.setLayout(my_layout_moo)
        
        # Set the current page to the SOO or MOO page depending on the options given to start the app
        page, text = (0, "Change to MOO") if options_soo != {} else (1, "Change to SOO")
        self.stackedWidget.setCurrentIndex(page)
        self.action_SwitchPage.setText(text)

        # Menu bar actions
        self.action_EditRunOptions.triggered.connect(self.editRunOptions)
        self.action_SwitchPage.triggered.connect(self.switchPage)
        self.action_SaveDefaultsVariants.triggered.connect(self.saveDefaultsVariants)
        self.action_LoadRunOptions.triggered.connect(self.loadRunOptions)
        self.action_LoadResults.triggered.connect(self.loadResults)
        self.action_SaveDefaultsVariants.triggered.connect(self.saveDefaultsVariants)
        self.action_SaveAllResults.triggered.connect(self.saveAllResults)
        self.action_SeeTutorial.triggered.connect(self.seeTutorial)
        self.action_About.triggered.connect(self.about)
        self.action_SaveRunOptions.triggered.connect(self.saveRunOptions)

    ####### GENRAL METHODS #######
    
    def switchPage(self):
        """Switch between SOO and MOO pages, and change the menu bar accordingly"""
        if self.stackedWidget.currentIndex() == 0:
            self.stackedWidget.setCurrentIndex(1)
            self.action_SwitchPage.setText("Change to SOO")
        else:
            self.stackedWidget.setCurrentIndex(0)
            self.action_SwitchPage.setText("Change to MOO")
    
    ##### TODO: Implement the functionality for the following actions
    
    def seeTutorial(self):
        # TODO: Implement the functionality for the See Tutorial action
        pass

    def about(self):
        # TODO: Implement the functionality for the About action
        pass
    
    ###### MAIN WINDOW METHODS ######
    
    def saveRunOptions(self):
        """Save the run options"""
        tabs = self.soo_tabs if self.stackedWidget.currentIndex() == 0 else self.moo_tabs

        options_dict = tabs.runOptions_to_dict()
        
        # Open file dialog to select the save location
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix('.pickle')
        file_dialog.setNameFilter('Pickle Files (*.pickle)')
        file_dialog.setWindowTitle('Save Run Options')
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            
            # Save options_dict as a pickle file
            with open(file_path, 'wb') as file:
                pickle.dump(options_dict, file)
    
    def loadRunOptions(self):
        """Load the run options"""
        tabs = self.soo_tabs if self.stackedWidget.currentIndex() == 0 else self.moo_tabs

        # Open file dialog to select the file to load
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setDefaultSuffix('.pickle')
        file_dialog.setNameFilter('Pickle Files (*.pickle)')
        file_dialog.setWindowTitle('Load Run Options')
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            
            # Load the pickle file
            with open(file_path, 'rb') as file:
                options_dict = pickle.load(file)
                
                # Set the run options
                tabs.runOptions_to_tables(options_dict)

    def saveAllResults(self):
        tabs = self.soo_tabs if self.stackedWidget.currentIndex() == 0 else self.moo_tabs
        tabs.saveAllResults()
        
    ##### TODO: Implement the functionality for the following actions #####

    def loadResults(self):
        # TODO: Implement the functionality for the Load Results action
        pass
    
    ####### EDIT WINDOW METHODS #######
    
    def editRunOptions(self):
        active_tabs = self.soo_tabs if self.stackedWidget.currentIndex() == 0 else self.moo_tabs
        active_tabs.edit_window.show()
    
    ##### TODO: Implement the functionality for the following actions #####

    def saveDefaultsVariants(self):
        # TODO: Implement the functionality for the Save Defaults Variants action
        pass
    
    
class MainTabsWidget(QTabWidget):
    def __init__(self, options: dict, defaults: Defaults, label: str) -> None:
        super().__init__()

        loadUi(DESIGNER_MAIN_TABS, self)
        
        ############################ GENERAL #################################
        
        self.defaults = defaults
        
        # create the edit window 
        tab_dicts = {'problem': ('Edit Problems', get_problem, [self.prob_table]), 
                     'algorithm': ('Edit Algorithms', get_algorithm, [self.algo_table]), 
                     'pi': ('Edit Performance Indicators', get_performance_indicator, [self.pi_table]),
                     'termination': ('Edit Termination Criteria', get_termination, [self.term_table])}
        self.edit_window = EditWindow(tab_dicts, self.defaults)
        
        # Make the tabs closable
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        self.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.tabBar().setTabButton(1, QTabBar.RightSide, None)

        ############################ RUN TAB  #################################
        
        # set run options
        missing_keys = set(RUN_OPTIONS_KEYS) - set(options.keys())
        for key in missing_keys:
            options[key] = []
        self.options = options

        self.soo_label.setText(label)
        self.initialComboBoxItems()
        self.runOptions_to_tables(options)
        
        # set run button 
        self.run_button.clicked.connect(self.runButton)

        ############################ RESULTS TAB  #################################

        # this property holds the result frames from each run
        self.result_frames = []
        
        # open, save and erase buttons                            
        self.save_button.clicked.connect(self.saveAllResults)
        self.open_button.clicked.connect(self.openAllResults)
        self.erase_button.clicked.connect(self.eraseAllResults)
    
    ### General methods ###        
    def closeTab(self, index):
        """Close the tab at the given index"""
        self.removeTab(index)
    
    ### Run tab methods ###
    def initialComboBoxItems(self):
        """Set one comboBox for each table with the initial items from the defaults"""
        
        # items for each combobox
        self.comboBox_items = []
        for key in ['problem', 'algorithm', 'pi', 'termination']:
            items = [obj_id for obj_id in self.defaults[key].keys() if ArgsAreSet(self.defaults[key])]
            self.comboBox_items.append(items)    
        
        # columns with comboboxes
        tables_list = [self.prob_table, self.algo_table, self.pi_table, self.term_table]
        
        for table, items in zip(tables_list, self.comboBox_items): 
            # strech the table to fit the window
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # add one combobox with the items 
            combobox = MyComboBox(items, table=table, add_rows= table != self.term_table)
            table.setCellWidget(0, 0, combobox)
                        
    def setTable(self, table: QTableWidget, table_options: list, min_rows: int):
        """Assumes the table has only one combobox. Repeats the comboboxes to the correct number of rows
        and sets the index to the correspondent item in the list. Returns a string with the items that are not available"""
        
        if table_options == []:
            return

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
                
    def runOptions_to_tables(self, options: dict):
        
        missing_keys = set(RUN_OPTIONS_KEYS) - set(options.keys())
        for key in missing_keys:
            options[key] = [] if key != 'n_seeds' else 1
            
        # set the combo boxes and the default run options
        missing_options = self.setTable(self.prob_table, options['prob'], DEFAULT_ROW_NUMBERS[0])
        missing_options += self.setTable(self.algo_table, options['algo'], DEFAULT_ROW_NUMBERS[1])
        missing_options += self.setTable(self.pi_table, options['pi'], DEFAULT_ROW_NUMBERS[2])
        missing_options += self.setTable(self.term_table, options['term'], DEFAULT_ROW_NUMBERS[3])

        self.n_seeds_SpinBox.setValue(options['n_seeds'])
        
        if missing_options != "":
            warning = MyMessageBox(f"The following options are not available: {missing_options[:-2]}. \nTo choose them, please add"
                                   " the correspondent Variant ID to the respective table through 'Edit Run Options' in the menu bar.")
            
    def runOptions_to_dict(self):
        """Get the run options from the table into a dictionary"""
        options = {}
        keys = RUN_OPTIONS_KEYS.copy()
        keys.remove('n_seeds')
        for table, key in zip([self.prob_table, self.algo_table, self.pi_table, self.term_table], keys):
            options[key] = [table.cellWidget(row, 0).currentText() for row in range(table.rowCount()) if table.cellWidget(row, 0).currentText() != ""]
        options['n_seeds'] = self.n_seeds_SpinBox.value()
        
        return options
    
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
        return RunThread(run_args, term_id, term_object, n_seeds, moo)

    def runButton(self):
        """First start the run window, then start the run. The two are separated 
        so that in a test scenario the threads from this window can be trailed 
        so it waits for them to finish before checking results."""
        
        if self.results_layout.count() > 6:
            warning = MyMessageBox("Please clear one of the results before running again.")
            return
        
        run = self.getRunObject()
        if run is None:
            return

        # create a result frame. get the number of the run from the self.listWidget
        run_number = self.results_layout.count() + 1  # Assuming run_number is the count of items in the list
        result_frame = ResultFrame(run, f"Run {run_number}", self)

        self.results_layout.addWidget(result_frame)  # Add the ResultFrame to the QVBoxLayout.
        
        self.setCurrentIndex(1)
                
    ### Results tab methods ###
    def noResults(self):
        """Return True if there are no results"""
        if self.results_layout.count() == 0:
            warning = MyMessageBox("There are no results available.")
            return True
        return False
    
    def saveAllResults(self):
        """Save all results"""
        if self.noResults():
            return
        
        for i in range(self.results_layout.count()):
            self.results_layout.itemAt(i).widget().saveResults()
    
    def openAllResults(self):
        """Open all results"""
        if self.noResults():
            return
        
        for i in range(self.results_layout.count()):
            self.results_layout.itemAt(i).widget().openTab()
    
    def eraseAllResults(self):
        """Erase all results"""
        if self.noResults():
            return
        
        for i in range(self.results_layout.count()):
            self.results_layout.itemAt(0).widget().erase()
            