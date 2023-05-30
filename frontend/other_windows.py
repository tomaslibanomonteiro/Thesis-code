from frontend.my_widgets import ScientificSpinBox, ScientificDoubleSpinBox, MyComboBox
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QCheckBox
from PyQt5.uic import loadUi
from numpy import inf
from backend.get_defaults import NO_DEFAULT, OPERATORS
from PyQt5.QtGui import QColor
from backend.get_defaults import Defaults
from utils.debug import debug_print
from utils.defines import DESIGNER_EDIT_WINDOW, DESIGNER_ALGO_WINDOW
from backend.get import get_sampling, get_crossover, get_mutation, get_decomposition, \
                      get_selection, get_reference_directions

class EditWindow(QDialog):
    def __init__(self, window_title: str, table_list: list, get_function, defaults: Defaults, ui_file=DESIGNER_EDIT_WINDOW):
        super().__init__()
        loadUi(ui_file, self)
        self.table_list = table_list
        self.defaults = defaults
        self.setWindowTitle(window_title)
        self.label.setText(window_title)
        self.get_function = get_function
        
        # for each operator, set the combobox items available (only for algo window)
        combo_items = {}
        for op, op_list in [("mutation",self.defaults.mutation), ("crossover",self.defaults.crossover), ("selection",self.defaults.selection), ("sampling",self.defaults.sampling), ("decomposition",self.defaults.decomposition), ("ref_dirs",self.defaults.ref_dirs)]:
            combo_items[op] = [sublist[0][0] for sublist in op_list]
        self.operator_combobox_items = combo_items


        # set the table items from the table, each row is a list of strings
        self.setTableItems()
        
        # strech the table columns to match the size of the items
        self.tableWidget.resizeColumnsToContents()
            
    def setTableItems(self):
        
        # set number of rows and columns (each element of the list is a tuple (argument, value))
        self.tableWidget.setRowCount(len(self.table_list)) 
        self.tableWidget.setColumnCount(max([len(row) for row in self.table_list])*2)

        # set col names
        for i in range(2, self.tableWidget.columnCount(), 2):
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem("Arg" + str(int(i))))
            self.tableWidget.setHorizontalHeaderItem(i+1, QTableWidgetItem("Value"))
            
        # set the table items from the table, each row is a list of the arguments and values of the class
        for row in range(self.tableWidget.rowCount()):
            for col in range(0, self.tableWidget.columnCount(), 2):
                self.setTableItem(row, col)
    
    def setTableItem(self, row, col):
        
        if col >= len(self.table_list[row]*2):                    
            self.tableWidget.setItem(row, col, QTableWidgetItem(""))
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(""))
            return
        
        FAKE_OPERATORS = ['(energy|riesz)', 'red']

        # get the argument and value of the class
        arg, value = self.table_list[row][int(col/2)]
        
        # arg is always a string
        self.tableWidget.setItem(row, col, QTableWidgetItem(arg))
        
        # check if is True or False to put a CheckBox
        if value is True or value is False:
            self.tableWidget.setCellWidget(row, col+1, QCheckBox())
            self.tableWidget.cellWidget(row, col+1).setChecked(value)
        # set table item according to value type 
        elif isinstance(value, int):
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
        elif arg in OPERATORS and self.table_list[row][0][1] not in FAKE_OPERATORS: 
            self.setOperatorComboBox(row, col, arg, value)    
        # check if is None
        elif value == None:
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(str(value)))
            self.tableWidget.item(row, col+1).setBackground(QColor(0, 0, 255))
        # check if is not a string, color with red (must be a class, something is wrong)
        elif not isinstance(value, str):
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(str(value)))
            self.tableWidget.item(row, col+1).setBackground(QColor(255, 0, 0))
        # check if has no default value, color
        elif value == NO_DEFAULT:
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(NO_DEFAULT))
            self.tableWidget.item(row, col+1).setBackground(QColor(0, 255, 0))
        else:
            self.tableWidget.setItem(row, col+1, QTableWidgetItem(value))
    
    def setOperatorComboBox(self, row, col, arg, value):
        raise NotImplementedError("setOperatorComboBox called from EditWindow")

    def getObjectFromID(self, object_id):
        # get the object from the table
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, 0).text() == object_id:
                return self.getObjectFromRow(row)
            
        raise Exception("Object ID '", object_id, "' not found in table from window ", self.windowTitle()) 
            
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
            arg = self.tableWidget.item(row, col).text()
            
            value = None
            if arg == "":
                break
            elif isinstance(self.tableWidget.cellWidget(row, col+1), (ScientificSpinBox, ScientificDoubleSpinBox)):
                value = self.tableWidget.cellWidget(row, col+1).value()       
            elif isinstance(self.tableWidget.cellWidget(row, col+1), QCheckBox):
                value = self.tableWidget.cellWidget(row, col+1).isChecked()
            elif isinstance(self.tableWidget.cellWidget(row, col+1), MyComboBox):
                value = self.tableWidget.cellWidget(row, col+1).currentText()
            # elif self.tableWidget.item(row, col+1).text() == NO_DEFAULT:
            #     raise Exception("No default -> need to set value for arg ", arg, " in row ", row, " of window ", self.windowTitle())
            elif self.tableWidget.item(row, col+1).text() == "None":
                value = None
            else:
                value = self.tableWidget.item(row, col+1).text()
                # try to convert text to int or float
                try:
                    value = int(value)
                    debug_print(value, "Converted to int in window ", self.windowTitle(), " row ", row, " col ", col, " arg ", arg, " value ", value)
                except:
                    try:
                        value = float(value)
                        debug_print(value, "Converted to float in window ", self.windowTitle(), " row ", row, " col ", col, " arg ", arg, " value ", value)
                    except:
                        pass
                
            args_dict[arg] = value
        return args_dict    
    
    def getArgsFromID(self, object_id):
        # get the args from the table
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, 0).text() == object_id:
                return self.tableWidget.item(row, 1).text(), self.getArgsFromRow(row)
            
        raise Exception("Object ID '" + str(object_id) + "' not found in table from window ", self.windowTitle())    

def setEditWindow(button, window_title: str, table: list, get_function, defaults: Defaults, ui_file = DESIGNER_EDIT_WINDOW):
    """Set the edit window to when the button is clicked"""
    window = EditWindow(window_title, table, get_function, defaults, ui_file)
    button.clicked.connect(window.show)
    return window

class AlgoWindow(EditWindow):
    def __init__(self, window_title: str, table: list, get_function, defaults: Defaults, ui_file = DESIGNER_ALGO_WINDOW):
        super().__init__(window_title, table, get_function, defaults, ui_file)
        
        # set the edit windows for each operator
        self.mutation_window = setEditWindow(self.pushButton_mutation, "Edit Mutations", self.defaults.mutation, get_mutation, defaults)
        self.crossover_window = setEditWindow(self.pushButton_crossover, "Edit Crossovers", self.defaults.crossover, get_crossover, defaults)
        self.selection_window = setEditWindow(self.pushButton_selection, "Edit Selections", self.defaults.selection, get_selection, defaults)
        self.sampling_window = setEditWindow(self.pushButton_sampling, "Edit Samplings", self.defaults.sampling, get_sampling, defaults)
        self.decomposition_window = setEditWindow(self.pushButton_decomposition, "Edit Decompositions", self.defaults.decomposition, get_decomposition, defaults)
        self.ref_dirs_window = setEditWindow(self.pushButton_ref_dirs, "Edit Ref_dirs", self.defaults.ref_dirs, get_reference_directions, defaults)
        
    def setOperatorComboBox(self, row, col, arg, value):

        items = self.operator_combobox_items[arg]
                
        if value not in [NO_DEFAULT, None]:
            index = items.index(value)
        else:
            index = -1
        self.tableWidget.setCellWidget(row, col+1, MyComboBox(items, index))
            
    def getArgsFromRow(self, row: int):
        # get the args from the table
        args_dict = {}
        for col in range(2, self.tableWidget.columnCount(), 2):
            arg = self.tableWidget.item(row, col).text()
            
            value = None
            if arg == "":
                break
            elif arg in OPERATORS:
                value = self.getOperator(arg, self.tableWidget.cellWidget(row, col+1).currentText())
            elif isinstance(self.tableWidget.cellWidget(row, col+1), (ScientificSpinBox, ScientificDoubleSpinBox)):
                value = self.tableWidget.cellWidget(row, col+1).value()       
            elif isinstance(self.tableWidget.cellWidget(row, col+1), QCheckBox):
                value = self.tableWidget.cellWidget(row, col+1).isChecked()
            elif isinstance(self.tableWidget.cellWidget(row, col+1), MyComboBox):
                value = self.tableWidget.cellWidget(row, col+1).currentText()
            # elif self.tableWidget.item(row, col+1).text() == NO_DEFAULT:
            #     raise Exception("No default -> need to set value for arg ", arg, " in row ", row, " of window ", self.windowTitle())
            elif self.tableWidget.item(row, col+1).text() == "None":
                value = None
            else:
                value = self.tableWidget.item(row, col+1).text()
                # try to convert text to int or float
                try:
                    value = int(value)
                    debug_print("Converted to int")
                except:
                    try:
                        value = float(value)
                        debug_print("Converted to float")
                    except:
                        pass
                
            args_dict[arg] = value
        return args_dict    
    
    def getOperator(self, op_name: str, op_id: str):
        
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
            return self.ref_dirs_window.getObjectFromID(op_id)
        else:
            raise Exception("Operator " + op_name + " not found, with id " + op_id)
        