from frontend.my_widgets import ScientificSpinBox, ScientificDoubleSpinBox, MyComboBox
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QCheckBox
from PyQt5.uic import loadUi
from numpy import inf
from utils.get_defaults import NO_DEFAULT
from PyQt5.QtGui import QColor
from utils.get_defaults import Defaults

class EditWindow(QDialog):
    def __init__(self, window_title: str, label: str, table_list: list, ui_file: str, get_function, defaults: Defaults):
        super().__init__()
        loadUi(ui_file, self)
        self.table_list = table_list
        self.defaults = defaults
        self.setWindowTitle(window_title)
        self.label.setText(label)
        self.get_function = get_function

        # set the table items from the table, each row is a list of strings
        self.setTableItems()
            
    def setTableItems(self):
        
        # set number of rows and columns (each element of the list is a tuple (argument, value))
        self.tableWidget.setRowCount(len(self.table_list)) 
        self.tableWidget.setColumnCount(max([len(row) for row in self.table_list])*2)

        # set the table items from the table, each row is a list of the arguments and values of the class
        table = self.table_list
        for row in range(self.tableWidget.rowCount()):
            for col in range(0, self.tableWidget.columnCount(), 2):
                if col < len(table[row]):
                    self.setTableItem(row, col)
                else:
                    self.tableWidget.setItem(row, col, QTableWidgetItem(""))
    
    def setTableItem(self, row, col):
        
        # get the argument and value of the class
        arg, value = self.table_list[row][int(col/2)]
        
        OPERATORS = ["mutation", "crossover", "selection", "sampling", "decomposition", "ref_dirs"]

        # arg is always a string
        self.tableWidget.setItem(row, col, QTableWidgetItem(arg))
        
        # set table item according to value type 
        if isinstance(value, int):
            self.tableWidget.setCellWidget(row, col+1, ScientificSpinBox())
            self.tableWidget.cellWidget(row, col+1).setValue(value)
        # check if it is float to put a doule SpinBox
        elif isinstance(value, float):
            self.tableWidget.setCellWidget(row, col+1, ScientificDoubleSpinBox())
            if value == inf:
                # set the value to the maximum value of the doubleSpinBox
                self.tableWidget.cellWidget(row, col+1).setValue(self.tableWidget.cellWidget(row, col+1).maximum())
            elif value == -inf:
                self.tableWidget.cellWidget(row, col+1).setValue(self.tableWidget.cellWidget(row, col+1).minimum())
            else:
                self.tableWidget.cellWidget(row, col+1).setValue(value)
        # if arg is an operator, put a comboBox with the possible operators
        elif arg in OPERATORS:
            self.setOperatorComboBox(row, col, arg, value)    
        # check if is True or False to put a CheckBox
        elif value in [True, False]:
            self.tableWidget.setCellWidget(row, col+1, QCheckBox().setChecked(value))
        # check if is None
        elif value == None:
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(str(value)))
            self.tableWidget.item(row, col+1).setBackground(QColor(0, 0, 255))
        # check if is not a string, color with red (must be a class, something is wrong)
        elif not isinstance(value, str):
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(str(value)))
            self.tableWidget.item(row, col+1).setBackground(QColor(255, 0, 0))
            print("Object arg in row ", row, ": ", value, " of window: ", self.windowTitle())
        # check if has no default value, color
        elif value == NO_DEFAULT:
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(NO_DEFAULT))
            self.tableWidget.item(row, col+1).setBackground(QColor(0, 255, 0))
        else:
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(value))
    
    def setOperatorComboBox(self, row, col, arg, value):
        # check if arg is an operator, and put a comboBox with the possible operators
        if arg == "mutation":
            items = [sublist[0] for sublist in self.defaults.mutation]
            index = items.index(value)
            self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
        elif arg == "crossover":
            items = [sublist[0] for sublist in self.defaults.crossover]
            index = items.index(value)
            self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
        elif arg == "selection":
            items = [sublist[0] for sublist in self.defaults.selection]
            index = items.index(value)
            self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
        elif arg == "sampling" and value not in ('kraemer', 'reduction'):
            items = [sublist[0] for sublist in self.defaults.sampling]
            index = items.index(value)
            self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
        elif arg == "decomposition":
            items = [sublist[0] for sublist in self.defaults.decomposition]
            index = items.index(value)
            self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
        elif arg == "ref_dirs":
            items = [sublist[0] for sublist in self.defaults.ref_dirs]
            index = items.index(value)
            self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))            
        else:
            print("Error: operator ", arg, " not found with value ", value)
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(value))
            
    def getObjectFromID(self, object_id):
        # get the object from the table
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, 0).text() == object_id:
                return self.getObjectFromRow(row)
            
        raise Exception("Object ID '", object_id, "' not found in table from window ", self.windowTitle()) 
    
    def getArgsFromID(self, object_id):
        # get the args from the table
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, 0).text() == object_id:
                return self.tableWidget.item(row, 1).text(), self.getArgsFromRow(row)
            
        raise Exception("Object ID '" + str(object_id) + "' not found in table from window ", self.windowTitle())    
        
    def getObjectFromRow(self, row):
        # get the object from the table
        class_name = self.tableWidget.item(row, 1).text()
        args_dict = self.getArgsFromRow(row)
            
        obj = self.get_function(class_name, **args_dict)
        if obj is None:
            raise Exception("Object ID matched, but problem getting it from the class", self.tableWidget.item(row, 0).text(), "in table from window ", self.windowTitle())
        else:
            return obj
        
    def getArgsFromRow(self, row):
        # get the args from the table
        args_dict = {}
        for col in range(2, self.tableWidget.columnCount(), 2):
            # check if the cell is empty
            if self.tableWidget.item(row, col+1) is None and self.tableWidget.cellWidget(row, col+1) is None:
                break
            elif isinstance(self.tableWidget.cellWidget(row, col+1), (ScientificSpinBox, ScientificDoubleSpinBox)):
                args_dict[self.tableWidget.item(row, col).text()] = self.tableWidget.cellWidget(row, col+1).value()       
            elif isinstance(self.tableWidget.cellWidget(row, col+1), QCheckBox):
                args_dict[self.tableWidget.item(row, col).text()] = self.tableWidget.cellWidget(row, col+1).isChecked()
            else:
                args_dict[self.tableWidget.item(row, col).text()] = self.tableWidget.item(row, col+1).text()
        return args_dict    