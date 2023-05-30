from PyQt5.QtWidgets import QMainWindow, QHeaderView
from PyQt5.uic import loadUi
from backend.get_defaults import Defaults
from frontend.my_widgets import MyComboBox
from frontend.other_windows import AlgoWindow, setEditWindow
from backend.get import get_algorithm, get_problem, get_termination, get_performance_indicator
from utils.defines import DESIGNER_MAIN
from backend.run import Run    
class MyMainWindow(QMainWindow):
    def __init__(self, defaults: Defaults):
        super().__init__()
        
        loadUi(DESIGNER_MAIN, self)
        
        # set other windows
        self.term_window = setEditWindow(self.pushButton_edit_term, "Edit Terminations", defaults.term, get_termination, defaults)
        self.pi_window = setEditWindow(self.pushButton_edit_pi, "Edit Performance Indicators", defaults.pi, get_performance_indicator, defaults)
        self.prob_window = setEditWindow(self.pushButton_edit_prob, "Edit Problems", defaults.prob, get_problem, defaults)
        
        self.algo_window = AlgoWindow("Edit Algorithms", defaults.algo, get_algorithm, defaults)
        self.pushButton_edit_algo.clicked.connect(self.algo_window.show)
                            
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
        term_object = self.term_window.getObjectFromID(term_id)
        
        pi_ids = []
        pi_class_args_tuple = []
        # get pi args (object can only be instantiated after)
        for row in range(self.tableWidget_run_pi.rowCount()):
            if self.tableWidget_run_pi.cellWidget(row, 0).currentText() == "":
                break
            pi_ids.append(self.tableWidget_run_pi.cellWidget(row, 0).currentText())
            pi_class_args_tuple.append(self.pi_window.getArgsFromID(pi_ids[-1])) 
            
        # get the problem objects
        prob_ids = []
        prob_objects = []
        for row in range(self.tableWidget_run_prob.rowCount()):
            if self.tableWidget_run_prob.cellWidget(row, 0).currentText() == "":
                break
            prob_ids.append(self.tableWidget_run_prob.cellWidget(row, 0).currentText())
            prob_objects.append(self.prob_window.getObjectFromID(prob_ids[-1]))
                    
        # get the algorithm objects
        algo_ids = []
        algo_objects = []
        for row in range(self.tableWidget_run_algo.rowCount()):
            if self.tableWidget_run_algo.cellWidget(row, 0).currentText() == "":
                break
            algo_ids.append(self.tableWidget_run_algo.cellWidget(row, 0).currentText())
            algo_objects.append(self.algo_window.getObjectFromID(algo_ids[-1]))
            
        run = Run(prob_ids, prob_objects, algo_ids, algo_objects, pi_ids, pi_class_args_tuple, term_id, term_object, n_seeds)
                    
        run.run()
        run.printData()