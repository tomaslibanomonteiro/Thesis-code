from PyQt5.QtWidgets import QMainWindow, QVBoxLayout
from PyQt5.uic import loadUi

from backend.defaults import Defaults
from frontend.main_fixed_tabs import MainTabsWidget
from utils.defines import DESIGNER_MAIN, MOO_TAB, SOO_TAB
from utils.utils import showAndRaise

class MyMainWindow(QMainWindow):
    """
    Main Window of the application. Contains two pages, with their respective tabs:
    - Multi Objective Optimization Page and Single Obejective Optimization Tab

    Attributes
    ----------------
    - tabs: A dictionary that holds the tabs of the application. The keys are the page indices 
    and the values are the tabs themselves.

    Important Methods
    -----------------
    - createTabs: Creates a tab with the given page, run options, and parameters, and adds it to the layout of the page.
    - activeTabs: Returns the currently active tab based on the index of the stacked widget.
    - switchPage: Switches between the SOO and MOO pages, updates the menu bar and window title, and checks and unchecks the SOO and MOO checkboxes based on the current page.
    - closeEvent: Closes the application when the close event is triggered.
    - seeTutorial: displaying the tutorial.
    - about: displaying about information.
    """
    def __init__(self, run_options_soo = {}, run_options_moo = {}, parameters_soo = Defaults(False).parameters, parameters_moo = Defaults(True).parameters, ) -> None:
        super().__init__()        
        
        loadUi(DESIGNER_MAIN, self)
        
        switch_page = run_options_soo == {} and run_options_moo != {}
        
        # create pages
        args = [(self.SOOpage, run_options_soo, parameters_soo, SOO_TAB), (self.MOOpage, run_options_moo, parameters_moo, MOO_TAB)]
        self.tabs = {page_index: self.createTabs(page, run_options, parameters) for page, run_options, parameters, page_index in args}         
        
        self.setUI(switch_page)
    
    def setUI(self, switch_page):    

        self.setWindowTitle("Main Window - Single Objective Optimization")
        # Menu bar actions
        self.action_SwitchPage.triggered.connect(self.switchPage)
        self.action_SeeTutorial.triggered.connect(self.seeTutorial)
        self.action_About.triggered.connect(self.about)

        self.action_SaveRunOptions.triggered.connect(lambda: self.activeTabs().saveRunOptions())
        self.action_SaveAllRuns.triggered.connect(lambda: self.activeTabs().saveAllRuns())
        self.action_LoadRunOptions.triggered.connect(lambda: self.activeTabs().loadRunOptions())
        self.action_LoadRun.triggered.connect(lambda: self.activeTabs().loadRun())

        self.action_EditParameters.triggered.connect(lambda: showAndRaise(self.activeTabs().edit_window))
        self.action_SaveParameters.triggered.connect(lambda: self.activeTabs().edit_window.saveParameters())
        self.action_LoadParameters.triggered.connect(lambda: self.activeTabs().edit_window.loadParameters())
        
        # connect the buttons of each tab to the respective actions
        for tab in self.tabs.values():
            tab.soo_checkBox.clicked.connect(self.switchPage)
            tab.moo_checkBox.clicked.connect(self.switchPage)
            tab.parameters_button.clicked.connect(lambda: showAndRaise(self.activeTabs().edit_window))

        # Set the current page to MOO if SOO has empty run options
        self.tabs[MOO_TAB].moo_checkBox.setChecked(True)
        self.tabs[MOO_TAB].soo_checkBox.setChecked(False)
        self.switchPage() if switch_page else None
    
    def createTabs(self, page, run_options: dict, parameters: dict):
        """Create a page with the run options and parameters"""
        
        my_layout = QVBoxLayout()
        my_layout.setContentsMargins(0, 0, 0, 0)
        page.setLayout(my_layout)
        
        tabs = MainTabsWidget(run_options, parameters)
        my_layout.addWidget(tabs)
        my_layout.setStretch(0, 1)
        
        return tabs
    
    def activeTabs(self):
        """Return the active page"""
        return self.tabs[self.stackedWidget.currentIndex()]
    
    def switchPage(self):
        """Switch between SOO and MOO pages, and change the menu bar accordingly"""
        if self.stackedWidget.currentIndex() == SOO_TAB:
            self.action_SwitchPage.setText("Switch to SOO")
            self.tabs[SOO_TAB].edit_window.close()
            self.tabs[MOO_TAB].moo_checkBox.setChecked(True)
            self.tabs[MOO_TAB].soo_checkBox.setChecked(False)
            self.tabs[SOO_TAB].moo_checkBox.setChecked(False)
            self.tabs[SOO_TAB].soo_checkBox.setChecked(True)
            self.stackedWidget.setCurrentIndex(MOO_TAB)
            self.setWindowTitle("Main Window - Multi Objective Optimization")
        else:
            self.action_SwitchPage.setText("Switch to MOO")
            self.tabs[MOO_TAB].edit_window.close()
            self.tabs[SOO_TAB].moo_checkBox.setChecked(False)
            self.tabs[SOO_TAB].soo_checkBox.setChecked(True)
            self.tabs[MOO_TAB].moo_checkBox.setChecked(True)
            self.tabs[MOO_TAB].soo_checkBox.setChecked(False)
            self.stackedWidget.setCurrentIndex(SOO_TAB)
            self.setWindowTitle("Main Window - Single Objective Optimization")
                
    def closeEvent(self, event):
        self.close()
        exit(0)

    #####! TODO: Implement the functionality for the following actions
    
    def seeTutorial(self):
        #! TODO: Implement the functionality for the See Tutorial action
        pass

    def about(self):
        #! TODO: Implement the functionality for the About action
        pass    
    