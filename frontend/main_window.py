from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog
from PyQt5.uic import loadUi
import pickle
from PyQt5.QtCore import QCoreApplication

from backend.defaults import Defaults
from frontend.main_fixed_tabs import MainTabsWidget
from utils.defines import DESIGNER_MAIN, MOO_PAGE, SOO_PAGE
class MyMainWindow(QMainWindow):

    def __init__(self, run_options_soo = {}, run_options_moo = {}, parameters_soo = Defaults('soo').dict, parameters_moo = Defaults('moo').dict, ) -> None:
        super().__init__()        
        
        loadUi(DESIGNER_MAIN, self)
        
        switch_page = run_options_soo == {} and run_options_moo != {}
        # create pages
        args = [(self.SOOpage, run_options_soo, parameters_soo, SOO_PAGE), (self.MOOpage, run_options_moo, parameters_moo, MOO_PAGE)]
        self.tabs = {page_index: self.createTabs(page, run_options, parameters) for page, run_options, parameters, page_index in args}         
                
        # Menu bar actions
        self.action_SwitchPage.triggered.connect(self.switchPage)
        self.action_SeeTutorial.triggered.connect(self.seeTutorial)
        self.action_About.triggered.connect(self.about)

        self.action_SaveRunOptions.triggered.connect(self.saveRunOptions)
        self.action_SaveAllResults.triggered.connect(self.saveAllResults)
        self.action_LoadRunOptions.triggered.connect(self.loadRunOptions)
        self.action_LoadResults.triggered.connect(self.loadResults)

        self.action_EditParameters.triggered.connect(self.editParameters)
        self.action_SaveParameters.triggered.connect(self.saveParameters)
        self.action_LoadParameters.triggered.connect(self.loadParameters)
        
        # connect the buttons of each tab to the respective actions
        for tab in self.tabs.values():
            tab.soo_checkBox.clicked.connect(self.switchPage)
            tab.moo_checkBox.clicked.connect(self.switchPage)
            tab.parameters_button.clicked.connect(self.editParameters)

        # Set the current page to the SOO or MOO page depending on the options given to start the app
        self.action_SwitchPage.setText("Change to MOO")
        self.tabs[SOO_PAGE].soo_checkBox.setChecked(False)
        self.tabs[SOO_PAGE].moo_checkBox.setChecked(True)
        self.stackedWidget.setCurrentIndex(SOO_PAGE)
        self.switchPage() if switch_page else None
        
    ####### GENERAL METHODS #######
    
    def createTabs(self, page, run_options: dict, parameters: dict):
        """Create a page with the run options and parameters"""
        
        my_layout = QVBoxLayout()
        my_layout.setContentsMargins(0, 0, 0, 0)
        page.setLayout(my_layout)
        
        tabs = MainTabsWidget(run_options, parameters)
        my_layout.addWidget(tabs)
        my_layout.setStretch(0, 1)
        
        return tabs
    
    def activePage(self):
        """Return the active page"""
        return self.tabs[self.stackedWidget.currentIndex()]
    
    def switchPage(self):
        """Switch between SOO and MOO pages, and change the menu bar accordingly"""
        if self.stackedWidget.currentIndex() == SOO_PAGE:
            self.action_SwitchPage.setText("Change to SOO")
            self.tabs[SOO_PAGE].edit_window.close()
            self.tabs[MOO_PAGE].moo_checkBox.setChecked(True)
            self.tabs[MOO_PAGE].soo_checkBox.setChecked(False)
            self.stackedWidget.setCurrentIndex(MOO_PAGE)
        else:
            self.action_SwitchPage.setText("Change to MOO")
            self.tabs[MOO_PAGE].edit_window.close()
            self.tabs[SOO_PAGE].moo_checkBox.setChecked(False)
            self.tabs[SOO_PAGE].soo_checkBox.setChecked(True)
            self.stackedWidget.setCurrentIndex(SOO_PAGE)
    
    #####! TODO: Implement the functionality for the following actions
    
    def seeTutorial(self):
        # TODO: Implement the functionality for the See Tutorial action
        pass

    def about(self):
        # TODO: Implement the functionality for the About action
        pass
    
    ###### MAIN WINDOW METHODS ######
    
    def saveRunOptions(self):
        """Save the run options"""
        active_tabs = self.activePage()

        options_dict = active_tabs.runOptions_to_dict()
        
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
        active_tabs = self.activePage()

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
                active_tabs.runOptions_to_tables(options_dict)

    def saveAllResults(self):
        active_tabs = self.activePage()
        active_tabs.saveAllResults()
        
    #####! TODO: Implement the functionality for the following actions #####

    def loadResults(self):
        # TODO: Implement the functionality for the Load Results action
        pass
    
    ####### EDIT WINDOW METHODS #######
    
    def editParameters(self):
        active_tabs = self.activePage()
        if active_tabs.edit_window.isVisible():
            active_tabs.edit_window.activateWindow()
        else:
            active_tabs.edit_window.show()
    
    def saveParameters(self):
        active_tabs = self.activePage()
        active_tabs.edit_window.saveParameters()
            
    def loadParameters(self):
        active_tabs = self.activePage()
        active_tabs.edit_window.loadParameters()
        self.editParameters()

    def closeEvent(self, event):
        self.close()
        exit(0)
