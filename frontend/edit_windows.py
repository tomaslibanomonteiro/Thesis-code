from numpy import inf
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QCheckBox, QDialog, QTableWidgetItem
from PyQt5.uic import loadUi

from backend.get import (get_crossover, get_decomposition, get_mutation,
                         get_reference_directions, get_sampling, get_selection)
from backend.get_defaults import NO_DEFAULT, OPERATORS, Defaults
from backend.run import Run
from frontend.my_widgets import (MyComboBox, ScientificDoubleSpinBox,
                                 ScientificSpinBox)
from utils.debug import debug_print
from utils.defines import (DESIGNER_ALGO_WINDOW, DESIGNER_EDIT_WINDOW)
import pydevd

def ArgsAreSet(dic: dict) -> bool:
    # check if any of the values in the list is == NO_DEFAULT
    return not any([value == NO_DEFAULT for value in dic.values()]) 

class EditWindow(QDialog):
    def __init__(self, window_title: str, table_dict: dict, get_function, defaults: Defaults, ui_file=DESIGNER_EDIT_WINDOW):
        super().__init__()
        loadUi(ui_file, self)
        self.table_dict = table_dict
        self.defaults = defaults
        self.setWindowTitle(window_title)
        self.label.setText(window_title)
        self.get_function = get_function

        # set the table items from the table, each row is a list of strings
        self.setTableItems()
        
        # strech the table columns to match the size of the items
        self.tableWidget.resizeColumnsToContents()
            
    def setTableItems(self):
        
        # set number of rows and columns (each element of the list is a tuple (argument, value))
        self.tableWidget.setRowCount(len(self.table_dict)) 
        self.tableWidget.setColumnCount(max([len(row) for row in self.table_dict])*2)

        # set col names
        for i in range(2, self.tableWidget.columnCount(), 2):
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem("Arg" + str(int(i-1))))
            self.tableWidget.setHorizontalHeaderItem(i+1, QTableWidgetItem("Value"))
        
        # import deepcopy to avoid changing the original dict
        from copy import deepcopy
        table_dict_copy = deepcopy(self.table_dict)   
        # set the table items from the table, each row is a list of the arguments and values of the class
        for row, (row_id, row_dict) in zip(range(self.tableWidget.rowCount()), table_dict_copy.items()):
            self.setTableItem(row, 0, row_id, row_dict.pop("class"))
            for col, (arg, value) in zip(range(2, self.tableWidget.columnCount(), 2), list(row_dict.items())):
                self.setTableItem(row, col, arg, value)
    
    def setTableItem(self, row, col, arg, value):
        
        table = self.tableWidget
                   
        FAKE_OPERATORS = ['(energy|riesz)', 'red']
        
        # arg is always a string
        table.setItem(row, col, QTableWidgetItem(arg))
        
        # check if is True or False to put a CheckBox
        if value is True or value is False:
            table.setCellWidget(row, col+1, QCheckBox())
            table.cellWidget(row, col+1).setChecked(value)
        # set table item according to value type 
        elif isinstance(value, int):
            table.setCellWidget(row, col+1, ScientificSpinBox())
            table.cellWidget(row, col+1).setValue(value)
        # check if it is float to put a doule SpinBox
        elif isinstance(value, float):
            table.setCellWidget(row, col+1, ScientificDoubleSpinBox())
            if value == inf:
                # set the value to the maximum value of the doubleSpinBox
                table.cellWidget(row, col+1).setValue(table.cellWidget(row, col+1).maximum())
            elif value == -inf:
                table.cellWidget(row, col+1).setValue(table.cellWidget(row, col+1).minimum())
            else:
                table.cellWidget(row, col+1).setValue(value)
        # if arg is an operator, put a comboBox with the possible operators
        elif arg in OPERATORS and table.item(row, 1).text() not in FAKE_OPERATORS: 
            self.setOperatorComboBox(row, col, arg, value)    
        # check if is None
        elif value == None:
            table.setItem(row, col+1, QTableWidgetItem(str(value)))
            table.item(row, col+1).setBackground(QColor(0, 0, 255))
        # check if is not a string, color with red (must be a class, something is wrong)
        elif not isinstance(value, str):
            table.setItem(row, col+1, QTableWidgetItem(str(value)))
            table.item(row, col+1).setBackground(QColor(255, 0, 0))
        # check if has no default value, color
        elif value == NO_DEFAULT:
            table.setItem(row, col+1, QTableWidgetItem(NO_DEFAULT))
            table.item(row, col+1).setBackground(QColor(0, 255, 0))
        else:
            table.setItem(row, col+1, QTableWidgetItem(value))
    
    def setOperatorComboBox(self, row, col, arg, value):
        raise NotImplementedError("setOperatorComboBox called from EditWindow")

    def getObjectFromID(self, object_id, pf=None, n_obj=None):
        # get the object from the table
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, 0).text() == object_id:
                return self.getObjectFromRow(row, pf, n_obj)
            
        raise Exception("Object ID '", object_id, "' not found in table from window ", self.windowTitle()) 
            
    def getObjectFromRow(self, row, pf=None, n_obj=None):
        # get the object from the table
        class_name = self.tableWidget.item(row, 1).text()
        args_dict = self.getArgsFromRow(row, pf, n_obj)
        
        # get the n_dim from the problem n_obj    
        if self.windowTitle() == "Edit Ref_dirs":
            for arg in ["n_dim", "n_points", "partitions"]:
                self.check_ref_dirs_dependency(args_dict, arg, n_obj)    
        # get the pf from the problem pf
        elif self.windowTitle() == "Edit Performance Indicators":
            if "pf" in args_dict and args_dict["pf"] == 'get from problem':
                args_dict["pf"] = pf
            
        obj = self.get_function(class_name, **args_dict)
        
        if obj is None:
            raise Exception("Object ID matched, but problem getting it from the class", self.tableWidget.item(row, 0).text(), "in table from window ", self.windowTitle())
        else:
            return obj
        
    def check_ref_dirs_dependency(self, args_dict, arg, n_obj):
        if arg in args_dict and args_dict[arg].startswith("n_obj*"):
            factor_str = args_dict[arg].split("*")[1]
            try:
                factor = int(factor_str)
            except ValueError:
                raise ValueError("Invalid value for n_dim factor:", factor_str)
            args_dict[arg] = n_obj * factor if n_obj is not None else None
    
    def getArgsFromRow(self, row: int, pf = None, n_obj=None):
        # get the args from the table
        args_dict = {}
        for col in range(2, self.tableWidget.columnCount(), 2):
            
            if self.tableWidget.item(row, col) is None:
                break
            arg = self.tableWidget.item(row, col).text()
            
            value = None
            if arg == "":
                break
            elif arg in OPERATORS and self.windowTitle() == "Edit Algorithms":
                value = self.getOperator(arg, self.tableWidget.cellWidget(row, col+1).currentText(), pf, n_obj)
            elif isinstance(self.tableWidget.cellWidget(row, col+1), (ScientificSpinBox, ScientificDoubleSpinBox)):
                value = self.tableWidget.cellWidget(row, col+1).value()       
            elif isinstance(self.tableWidget.cellWidget(row, col+1), QCheckBox):
                value = self.tableWidget.cellWidget(row, col+1).isChecked()
            elif isinstance(self.tableWidget.cellWidget(row, col+1), MyComboBox):
                value = self.tableWidget.cellWidget(row, col+1).currentText()
            elif self.tableWidget.item(row, col+1).text() == NO_DEFAULT:
                raise Exception("No default -> need to set value for arg ", arg, " in row ", row, " of window ", self.windowTitle())
            elif self.tableWidget.item(row, col+1).text() == "None":
                value = None
            else:
                value = self.tableWidget.item(row, col+1).text()
                # try to convert text to int or float
                try:
                    value = int(value)
                    debug_print("Arg ", arg, ", with value ", value, " converted to int, from window ", self.windowTitle()) 
                except:
                    try:
                        value = float(value)
                        debug_print("Arg ", arg, ", with value ", value, " converted to int, from window ", self.windowTitle()) 
                    except:
                        pass
                
            args_dict[arg] = value
        return args_dict    

    def getOperator(self, operator, operator_name, pf = None, n_obj=None):
        raise NotImplementedError("getOperator called from EditWindow")
    
def setEditWindow(button, window_title: str, table: dict, get_function, defaults: Defaults, ui_file = DESIGNER_EDIT_WINDOW):
    """Set the edit window to when the button is clicked"""
    window = EditWindow(window_title, table, get_function, defaults, ui_file)
    button.clicked.connect(window.show)
    return window

class AlgoWindow(EditWindow):
    def __init__(self, window_title: str, table: dict, get_function, defaults: Defaults, ui_file = DESIGNER_ALGO_WINDOW):
        
        self.operator_comboBox_items = {} 
        # for each operator, set the combobox items available (only for algo window)
        for op, op_table in [("mutation", defaults.mutation), ("crossover", defaults.crossover), ("selection", defaults.selection), ("sampling", defaults.sampling), ("decomposition", defaults.decomposition), ("ref_dirs", defaults.ref_dirs)]:
            self.operator_comboBox_items[op] = list(op_table.keys())
        super().__init__(window_title, table, get_function, defaults, ui_file)
        
        # set the edit windows for each operator
        self.mutation_window = setEditWindow(self.pushButton_mutation, "Edit Mutations", self.defaults.mutation, get_mutation, defaults)
        self.crossover_window = setEditWindow(self.pushButton_crossover, "Edit Crossovers", self.defaults.crossover, get_crossover, defaults)
        self.selection_window = setEditWindow(self.pushButton_selection, "Edit Selections", self.defaults.selection, get_selection, defaults)
        self.sampling_window = setEditWindow(self.pushButton_sampling, "Edit Samplings", self.defaults.sampling, get_sampling, defaults)
        self.decomposition_window = setEditWindow(self.pushButton_decomposition, "Edit Decompositions", self.defaults.decomposition, get_decomposition, defaults)
        self.ref_dirs_window = setEditWindow(self.pushButton_ref_dirs, "Edit Ref_dirs", self.defaults.ref_dirs, get_reference_directions, defaults)
        
    def setOperatorComboBox(self, row, col, arg, value):

        items = self.operator_comboBox_items[arg]
                
        if value not in [NO_DEFAULT, None]:
            index = items.index(value)
        else:
            index = -1
        self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
                
    def getOperator(self, op_name: str, op_id: str, pf = None, n_obj=None):
        
        if op_name ==  "mutation":
            return self.mutation_window.getObjectFromID(op_id)
        elif op_name == "crossover":
            return self.crossover_window.getObjectFromID(op_id)
        elif op_name == "selection":
            return self.selection_window.getObjectFromID(op_id)
        elif op_name == "sampling":
            return self.sampling_window.getObjectFromID(op_id)
        elif op_name == "decomposition":
            return self.decomposition_window.getObjectFromID(op_id)
        elif op_name == "ref_dirs":
            return self.ref_dirs_window.getObjectFromID(op_id, pf, n_obj)
        else:
            raise Exception("Operator " + op_name + " not found, with id " + op_id)
        
