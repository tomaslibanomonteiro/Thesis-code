from PyQt5.QtWidgets import QMainWindow, QHeaderView
from PyQt5.uic import loadUi
from utils.get_defaults import Defaults
from utils.get_defaults import NO_DEFAULT
from frontend.my_widgets import MyComboBox
from frontend.edit_window import EditWindow
from utils.get import get_algorithm, get_problem, get_termination, get_performance_indicator, get_sampling, \
                    get_crossover, get_mutation, get_decomposition, get_selection, get_reference_directions, get_other_class_options

DESIGNER_MAIN = 'frontend/designer_templates/main_window.ui' 
DESIGNER_EDIT_WINDOW = 'frontend/designer_templates/edit_window.ui'
DESIGNER_ALGO_WINDOW = 'frontend/designer_templates/algo_window.ui'

class MyMainWindow(QMainWindow):
    def __init__(self, defaults: Defaults):
        super().__init__()
        
        loadUi(DESIGNER_MAIN, self)
        self.edit_windows = []
        
        # set windows for pi, prob, term
        buttons = [self.pushButton_edit_term, self.pushButton_edit_pi, self.pushButton_edit_prob]
        labels = ["Edit Termination", "Edit Performance Indicators", "Edit Problem"]
        ui_files = [DESIGNER_EDIT_WINDOW] * len(buttons)
        default_tables = [defaults.term, defaults.pi, defaults.prob]
        get_functions = [get_termination, get_performance_indicator, get_problem]         
        self.setEditWindows(buttons, labels, default_tables, ui_files, get_functions, defaults)
        
        # set window for algo (more buttons to connect to operators)
        self.setEditWindows([self.pushButton_edit_algo], ["Edit Algorithms"], [defaults.algo], [DESIGNER_ALGO_WINDOW], [get_algorithm], defaults)
        algo_window = self.edit_windows[-1]
        
        # set windows for algo operators (sampling, crossover, mutation, decomposition, selection, ref_dirs)
        buttons = [algo_window.pushButton_sampling, algo_window.pushButton_crossover, algo_window.pushButton_mutation, \
                    algo_window.pushButton_selection, algo_window.pushButton_decomposition, algo_window.pushButton_ref_dirs] 
        labels = ["Edit Sampling Operators", "Edit Crossover Operators", "Edit Mutation Operators", "Edit Selection Operators",\
                    "Edit Decomposition Operators", "Edit Reference Directions"]
        ui_files = [DESIGNER_EDIT_WINDOW] * len(buttons)
        default_tables = [defaults.sampling, defaults.crossover, defaults.mutation, defaults.selection, defaults.decomposition,\
                            defaults.ref_dirs]
        get_functions = [get_sampling, get_crossover, get_mutation, get_selection, get_decomposition, get_reference_directions]
        self.setEditWindows(buttons, labels, default_tables, ui_files, get_functions, defaults)        
        
        # set comboboxes from main window
        tables_list = [self.tableWidget_run_pi, self.tableWidget_run_algo, self.tableWidget_run_prob]
        pi_options = sorted([lst[0][0] for lst in defaults.pi])
        algo_options = sorted([algo[0][0] for algo in defaults.algo])
        prob_options = sorted([prob[0][0] for prob in defaults.prob])
        comboBox_options = [pi_options, algo_options, prob_options]
        self.setTablesToComboBoxes(tables_list, comboBox_options)
        self.comboBox_term.addItems([term[0][0] for term in defaults.term])
        self.comboBox_term.setCurrentIndex(-1)
        
        # set run button
        self.PushButton_Run.clicked.connect(self.runButton)
                
    def setEditWindows(self, buttons, labels, tables, ui_files, get_functions, defaults: Defaults):
        for button, label, table, ui_file, get_function in zip(buttons, labels, tables, ui_files, get_functions): # type: ignore
            window = EditWindow(label, label, table, ui_file, get_function, defaults)
            self.edit_windows.append(window)
            button.clicked.connect(window.show)
            
    def setTablesToComboBoxes(self, tableWidget_list, comboBox_items_list):
        for table, items in zip(tableWidget_list, comboBox_items_list): # type: ignore
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
        n_seeds = self.SpinBox_n_seeds.value()
        
        # get the termination object
        term_id = self.comboBox_term.currentText()
        term_object = self.edit_windows[0].getObjectFromID(term_id)
        print(term_object)
        
        pi_ids = []
        pi_class_args_tuple = []
        # get pi args (object can only be instantiated after )
        for row in range(self.tableWidget_run_pi.rowCount()):
            if self.tableWidget_run_pi.cellWidget(row, 0).currentText() == "":
                break
            pi_ids.append(self.tableWidget_run_pi.cellWidget(row, 0).currentText())
            pi_class_args_tuple.append(self.edit_windows[1].getArgsFromID(pi_ids[-1]))
            
        # get the problem objects
        prob_ids = []
        prob_objects = []
        for row in range(self.tableWidget_run_prob.rowCount()):
            if self.tableWidget_run_prob.cellWidget(row, 0).currentText() == "":
                break
            prob_ids.append(self.tableWidget_run_prob.cellWidget(row, 0).currentText())
            prob_objects.append(self.edit_windows[2].getObjectFromID(prob_ids[-1]))
            
        print("prob_objects", prob_objects)
        
        # get the algorithm objects
        algo_ids = []
        algo_objects = []
        for row in range(self.tableWidget_run_algo.rowCount()):
            if self.tableWidget_run_algo.cellWidget(row, 0).currentText() == "":
                break
            algo_ids.append(self.tableWidget_run_algo.cellWidget(row, 0).currentText())
            algo_objects.append(self.edit_windows[3].getObjectFromID(algo_ids[-1]))