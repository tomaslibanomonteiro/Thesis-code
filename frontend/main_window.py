from PyQt5.QtWidgets import QMainWindow, QHeaderView
from PyQt5.uic import loadUi
from utils.get_defaults import Defaults
from utils.get_defaults import NO_DEFAULT
from frontend.my_widgets import MyComboBox
from frontend.edit_window import EditWindow

DESIGNER_MAIN = 'frontend/designer_templates/main_window.ui' 
DESIGNER_EDIT_WINDOW = 'frontend/designer_templates/edit_window.ui'
DESIGNER_ALGO_WINDOW = 'frontend/designer_templates/algo_window.ui'

class MyMainWindow(QMainWindow):
    def __init__(self, defaults: Defaults):
        super().__init__()
        
        loadUi(DESIGNER_MAIN, self)
        self.edit_windows = []
        
        # set windows for pi, prob, term
        buttons = [self.pushButton_edit_pi, self.pushButton_edit_prob, self.pushButton_edit_term]
        labels = ["Edit Performance Indicators", "Edit Problems", "Edit Terminations"]
        ui_files = [DESIGNER_EDIT_WINDOW] * len(buttons)
        default_tables = [defaults.pi, defaults.prob, defaults.term]         
        self.setEditWindows(buttons, labels, default_tables, ui_files)
        
        # set window for algo (more buttons to connect to operators)
        self.setEditWindows([self.pushButton_edit_algo], ["Edit Algorithms"], [defaults.algo], [DESIGNER_ALGO_WINDOW])
        algo_window = self.edit_windows[-1]
        # set windows for algo operators (sampling, crossover, mutation, decomposition, selection, ref_dirs)
        buttons = [algo_window.pushButton_sampling, algo_window.pushButton_crossover, algo_window.pushButton_mutation, algo_window.pushButton_selection, algo_window.pushButton_decomposition, algo_window.pushButton_ref_dirs]
        labels = ["Edit Sampling Operators", "Edit Crossover Operators", "Edit Mutation Operators", "Edit Selection Operators", "Edit Decomposition Operators", "Edit Reference Directions"]
        ui_files = [DESIGNER_EDIT_WINDOW] * len(buttons)
        default_tables = [defaults.sampling, defaults.crossover, defaults.mutation, defaults.selection, defaults.decomposition, defaults.ref_dirs]
        self.setEditWindows(buttons, labels, default_tables, ui_files)        
        
        # set comboboxes from main window
        tables_list = [self.tableWidget_run_pi, self.tableWidget_run_algo, self.tableWidget_run_prob]
        pi_options = sorted([pi[0] for pi in defaults.pi])
        algo_options = sorted([algo[0] for algo in defaults.algo])
        prob_options = sorted([prob[0] for prob in defaults.prob])
        comboBox_options = [pi_options, algo_options, prob_options]
        self.setTablesToComboBoxes(tables_list, comboBox_options)
        self.comboBox_term.addItems([term[0] for term in defaults.term])
        self.comboBox_term.setCurrentIndex(-1)
        
        # set run button
        self.PushButton_Run.clicked.connect(self.runButton)
                
    def setEditWindows(self, buttons, labels, tables, ui_files):
        for button, label, table, ui_file in zip(buttons, labels, tables, ui_files):
            window = EditWindow(label, label, table, ui_file, self)
            self.edit_windows.append(window)
            button.clicked.connect(window.show)
            
    def setTablesToComboBoxes(self, tableWidget_list, comboBox_items_list):
        for table, items in zip(tableWidget_list, comboBox_items_list):
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

    def runButton(self):
        # get the values from the main window
        pi = self.getComboBoxValues(self.tableWidget_run_pi)
        algo = self.getComboBoxValues(self.tableWidget_run_algo)
        prob = self.getComboBoxValues(self.tableWidget_run_prob)
        term = self.comboBox_term.currentText()
        print(pi, algo, prob, term)
    
    def getComboBoxValues(self, table):
        values = []
        for row in range(table.rowCount()):
            combobox = table.cellWidget(row, 0)
            if combobox:
                values.append(combobox.currentText())
        return values
    
