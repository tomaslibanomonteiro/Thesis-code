from frontend.my_widgets import ScientificSpinBox, ScientificDoubleSpinBox, MyComboBox
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QCheckBox
from PyQt5.uic import loadUi
from numpy import inf
from utils.get_defaults import NO_DEFAULT
from PyQt5.QtGui import QColor
from utils.get_defaults import Defaults

class EditWindow(QDialog):
    def __init__(self, window_title: str, label: str, table: list, ui_file: str, defaults: Defaults):
        super().__init__()
        loadUi(ui_file, self)
        self.default_table = table
        self.defaults = defaults
        self.setWindowTitle(window_title)
        self.label.setText(label)

        # set number of rows and columns
        self.tableWidget.setRowCount(len(table))
        # make the table with the number of columns of the biggest row
        self.tableWidget.setColumnCount(max([len(row) for row in table]))
        # set the table items from the table, each row is a list of strings
        self.setTableItems()
        
        # adjust the size of the table to fit the window
        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def setTableItems(self):
        # set the table items from the table, each row is a list of the arguments and values of the class
        table = self.default_table
        for row in range(self.tableWidget.rowCount()):
            for col in range(0, self.tableWidget.columnCount(), 2):
                if col < len(table[row]):
                    self.setTableItem(row, col)
                else:
                    self.tableWidget.setItem(row, col, QTableWidgetItem(""))
    
    def setTableItem(self, row, col):
        # set the table item according to the type of the value
        self.tableWidget.setItem(row, col, QTableWidgetItem(self.default_table[row][col]))
        # check if is int to put a SpinBox
        if isinstance(self.default_table[row][col+1], int):
            self.tableWidget.setCellWidget(row, col+1, ScientificSpinBox())
            self.tableWidget.cellWidget(row, col+1).setValue(self.default_table[row][col+1])
        # check if it is float to put a doule SpinBox
        elif isinstance(self.default_table[row][col+1], float):
            self.tableWidget.setCellWidget(row, col+1, ScientificDoubleSpinBox())
            if self.default_table[row][col+1] == inf:
                # set the value to the maximum value of the doubleSpinBox
                self.tableWidget.cellWidget(row, col+1).setValue(self.tableWidget.cellWidget(row, col+1).maximum())
            elif self.default_table[row][col+1] == -inf:
                self.tableWidget.cellWidget(row, col+1).setValue(self.tableWidget.cellWidget(row, col+1).minimum())
            else:
                self.tableWidget.cellWidget(row, col+1).setValue(self.default_table[row][col+1])
        # if the table is from algorithms, check if arg is operator, and put a comboBox with the possible operators
        elif self.windowTitle() == "Edit Algorithm":    
            # check if arg is an operator, and put a comboBox with the possible operators
            if self.default_table[row][col] == "mutation":
                items = [sublist[0] for sublist in self.defaults.mutation]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "crossover":
                items = [sublist[0] for sublist in self.defaults.crossover]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "selection":
                items = [sublist[0] for sublist in self.defaults.selection]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "sampling":
                items = [sublist[0] for sublist in self.defaults.sampling]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "decomposition":
                items = [sublist[0] for sublist in self.defaults.decomposition]
                index = items.index(self.default_table[row][col+1])
                self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            elif self.default_table[row][col] == "ref_dirs":
                items = [sublist[0] for sublist in self.defaults.ref_dirs]
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
    