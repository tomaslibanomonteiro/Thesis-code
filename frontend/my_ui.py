from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QDialog, QSpinBox, QDoubleSpinBox, QTableWidgetItem, QCheckBox, QLineEdit
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtGui import QColor
from utils.inpect_classes import Defaults
from utils.inpect_classes import NO_DEFAULT

DESIGNER_MAIN = 'frontend/designer_main.ui'
DESIGNER_EDIT_WINDOW = 'frontend/designer_edit_window.ui'
DESIGNER_ALGO_WINDOW = 'frontend/designer_algo_window.ui'

class MyComboBox(QComboBox):
    def __init__(self, items = [], initial_index=-1, initial_text="", enabled = True):
        super().__init__()
        
        for item in items:
            self.addItem(item)
        self.setCurrentIndex(initial_index)
        self.setEnabled(enabled) # TODO: this is not working
        self.setEditText(initial_text)

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        loadUi(DESIGNER_MAIN, self)
        self.edit_windows = []
        self.defaults = Defaults()
        
        # set windows for pi, prob, term
        buttons = [self.pushButton_edit_pi, self.pushButton_edit_prob, self.pushButton_edit_term]
        labels = ["Edit Performance Indicators", "Edit Problems", "Edit Terminations"]
        ui_files = [DESIGNER_EDIT_WINDOW] * len(buttons)
        default_tables = [self.defaults.pi, self.defaults.prob, self.defaults.term]         
        self.setEditWindows(buttons, labels, default_tables, ui_files)
        
        # set window for algo (more buttons to connect to operators)
        self.setEditWindows([self.pushButton_edit_algo], ["Edit Algorithms"], [self.defaults.algo], [DESIGNER_ALGO_WINDOW])
        algo_window = self.edit_windows[-1]
        # set windows for algo operators (sampling, crossover, mutation, decomposition, selection, ref_dirs)
        buttons = [algo_window.pushButton_sampling, algo_window.pushButton_crossover, algo_window.pushButton_mutation, algo_window.pushButton_selection, algo_window.pushButton_decomposition, algo_window.pushButton_ref_dirs]
        labels = ["Edit Sampling Operators", "Edit Crossover Operators", "Edit Mutation Operators", "Edit Selection Operators", "Edit Decomposition Operators", "Edit Reference Directions"]
        ui_files = [DESIGNER_EDIT_WINDOW] * len(buttons)
        default_tables = [self.defaults.sampling, self.defaults.crossover, self.defaults.mutation, self.defaults.selection, self.defaults.decomposition, self.defaults.ref_dirs]
        self.setEditWindows(buttons, labels, default_tables, ui_files)        
        
        # set comboboxes from main window
        tables_list = [self.tableWidget_run_pi, self.tableWidget_run_algo, self.tableWidget_run_prob]
        pi_options = sorted([pi[0] for pi in self.defaults.pi])
        algo_options = sorted([algo[0] for algo in self.defaults.algo])
        prob_options = sorted([prob[0] for prob in self.defaults.prob])
        comboBox_options = [pi_options, algo_options, prob_options]
        self.setTablesToComboBoxes(tables_list, comboBox_options)
        self.comboBox_term.addItems([term[0] for term in self.defaults.term])
        self.comboBox_term.setCurrentIndex(-1)
                
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

class EditWindow(QDialog):
    def __init__(self, window_title: str, label: str, table: list, ui_file, main_window: MyMainWindow):
        super().__init__()
        loadUi(ui_file, self)
        self.main_window = main_window
        self.default_table = table
        self.setWindowTitle(window_title)
        self.label.setText(label)

        # set number of rows and columns
        self.tableWidget.setRowCount(len(table))
        # make the table with the number of columns of the biggest row
        self.tableWidget.setColumnCount(max([len(row) for row in table]))
        # set the table items from the table, each row is a list of strings
        self.setTableItems()
        
        # adjust the size of the table to fit the window
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def setTableItems(self):
        table = self.default_table
        for row in range(self.tableWidget.rowCount()):
            for col in range(0, self.tableWidget.columnCount(), 2):
                if col < len(table[row]):
                    self.setTableItem(row, col)
                else:
                    self.tableWidget.setItem(row, col, QTableWidgetItem(""))
    
    def setTableItem(self, row, col):
        self.tableWidget.setItem(row, col, QTableWidgetItem(self.default_table[row][col]))
        # check if is int to put a SpinBox
        if isinstance(self.default_table[row][col+1], int):
            self.tableWidget.setCellWidget(row, col+1, QSpinBox())
            self.tableWidget.cellWidget(row, col+1).setValue(self.default_table[row][col+1])
        # check if it is float to put a doule SpinBox
        elif isinstance(self.default_table[row][col+1], float):
            self.tableWidget.setCellWidget(row, col+1, QDoubleSpinBox())
            self.tableWidget.cellWidget(row, col+1).setValue(self.default_table[row][col+1])
        # if the table is from algorithms, check if arg is operator, and put a comboBox with the possible operators
        elif self.default_table == self.main_window.defaults.algo:    
            # check if arg is an operator, and put a comboBox with the possible operators
            if self.default_table[row][col] == "mutation":
                items = [sublist[0] for sublist in self.main_window.defaults.mutation]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "crossover":
                items = [sublist[0] for sublist in self.main_window.defaults.crossover]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "selection":
                items = [sublist[0] for sublist in self.main_window.defaults.selection]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "sampling":
                items = [sublist[0] for sublist in self.main_window.defaults.sampling]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "decomposition":
                items = [sublist[0] for sublist in self.main_window.defaults.decomposition]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "ref_dirs":
                items = [sublist[0] for sublist in self.main_window.defaults.ref_dirs]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
        # check if is True or False to put a CheckBox
        elif self.default_table[row][col+1] in [True, False]:
            self.tableWidget.setCellWidget(row, col+1, QCheckBox().setChecked(self.default_table[row][col+1]))
        # check if it is not string, color with red (must be an object)
        elif not isinstance(self.default_table[row][col+1], str):
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(str(self.default_table[row][col+1])))
            self.tableWidget.item(row, col+1).setBackground(QColor(255, 0, 0))
        # check if has no default value, color with red
        elif self.default_table[row][col+1] == NO_DEFAULT:
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(NO_DEFAULT))
            self.tableWidget.item(row, col+1).setBackground(QColor(255, 0, 0))
        else:
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(self.default_table[row][col+1]))
                        
def main():
    app = QApplication([])
    main_window = MyMainWindow()
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()    