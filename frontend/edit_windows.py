from numpy import inf
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QTableWidget
from PyQt5.uic import loadUi

from backend.get import (get_crossover, get_decomposition, get_mutation,
                         get_reference_directions, get_sampling, get_selection)
from backend.get_defaults import NO_DEFAULT, OPERATORS, Defaults
from frontend.my_widgets import MyTextEdit, MyComboBox, ScientificDoubleSpinBox, ScientificSpinBox, MyCheckBox, MyMessageBox
from utils.debug import debug_print
from utils.defines import DESIGNER_ALGO_WINDOW, DESIGNER_EDIT_WINDOW, VARIANTS_HELP_MSG

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
        self.variants_interrogation.clicked.connect(self.variantsHelp)
        
        # set default table from table_dict and variant table 
        self.setDefaultTable()
        self.setVariantTable(self.defaults_table)
    
    def variantsHelp(self):
        helpbox = MyMessageBox(VARIANTS_HELP_MSG, "Variants Help", warning_icon=False)
        
    def setDefaultTable(self):
        # set number of rows and columns (each element of the list is a tuple (argument, value))
        self.defaults_table.setRowCount(len(self.table_dict)) 
        self.defaults_table.setColumnCount(max([len(row_dict) for row_dict in self.table_dict.values()]) * 2)

        # set col names
        for i in range(2, self.defaults_table.columnCount(), 2):
            self.defaults_table.setHorizontalHeaderItem(i, QTableWidgetItem("Arg" + str(int(i-1))))
            self.defaults_table.setHorizontalHeaderItem(i+1, QTableWidgetItem("Value"))
        
        # import deepcopy to avoid changing the original dict
        from copy import deepcopy
        table_dict_copy = deepcopy(self.table_dict)   
        # set the table items from the table, each row is a list of the arguments and values of the class
        for row, (row_id, row_dict) in zip(range(self.defaults_table.rowCount()), table_dict_copy.items()):
            self.setTablePair(self.defaults_table, row, 0, row_id, row_dict.pop("class"), editable=False)
            for col, (arg, value) in zip(range(2, self.defaults_table.columnCount(), 2), list(row_dict.items())):
                self.setTablePair(self.defaults_table, row, col, arg, value)
    
    def setTablePair(self, table: QTableWidget, row: int, col: int, arg: str, value, editable: bool = True) -> None:

        FAKE_OPERATORS = ['(energy|riesz)', 'red']
        
        # Set the widget in the arg column (always text)
        widget = MyTextEdit(arg, read_only=True)
        table.setCellWidget(row, col, widget)    
        
        # Set the widget in the value column
        if isinstance(value, bool):
            widget = MyCheckBox(value)
        elif isinstance(value, int):
            widget = ScientificSpinBox()
            widget.setValue(value)
        elif isinstance(value, float):
            widget = ScientificDoubleSpinBox()
            if value == inf:
                widget.setValue(widget.maximum())
            elif value == -inf:
                widget.setValue(widget.minimum())
            else:
                widget.setValue(value)
        elif arg in OPERATORS and table.cellWidget(row, 1).text() not in FAKE_OPERATORS:
            self.setOperatorComboBox(table, row, col, arg, value)
            return
        elif value is None:
            widget = MyTextEdit(str(value))
            widget.setStyleSheet("background-color: lightblue;")
        # only option left is convert to string            
        elif not isinstance(value, str):
            widget = MyTextEdit(str(value))
            widget.setStyleSheet("background-color: lightred;")
        # if the value is NO_DEFAULT, set the background to green
        elif value == NO_DEFAULT:
            widget = MyTextEdit(NO_DEFAULT)
            widget.setStyleSheet("background-color: lightyellow;")
        else:
            widget = MyTextEdit(value, read_only=not editable)
        
        table.setCellWidget(row, col+1, widget)    
                    
    def setOperatorComboBox(self, table: QTableWidget, row, col, arg, value):
        raise NotImplementedError("setOperatorComboBox called from EditWindow. Must be called from AlgoWindow")

    def setVariantTable(self, defaults_table: QTableWidget):
        
        classes = [defaults_table.cellWidget(row, 1).text() for row in range(defaults_table.rowCount())]
        
        # copy first row of defaults_table to variants_table
        self.variants_table.setRowCount(1)
        self.variants_table.setColumnCount(defaults_table.columnCount())
        
        widget = MyComboBox(classes, table=self.variants_table, copy_table=self.defaults_table, add_rows=True, col=1)
        self.variants_table.setCellWidget(0, 1, widget)
        
    def getObjectFromID(self, object_id, pf=None, n_obj=None):
        # get the object from a table
        for table in [self.variants_table, self.defaults_table]:
            for row in range(table.rowCount()):
                if table.cellWidget(row, 0) is None:
                    continue
                if table.cellWidget(row, 0).text() == object_id:
                    return self.getObjectFromRow(table, row, pf, n_obj)
                
        raise Exception("Object ID '", object_id, "' not found in table from window ", self.windowTitle()) 
            
    def getObjectFromRow(self, table: QTableWidget, row, pf=None, n_obj=None):
        # get the object from the table
        if isinstance(table.cellWidget(row, 1), MyTextEdit):
            class_name = table.cellWidget(row, 1).text()
        else:
            class_name = table.cellWidget(row, 1).currentText()
        args_dict = self.getArgsFromRow(table, row, pf, n_obj)
        
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
            raise Exception("Object ID matched, but problem getting it from the class", class_name, "in table from window ", self.windowTitle())
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
    
    def getArgsFromRow(self, table: QTableWidget, row: int, pf = None, n_obj=None):
        # get the args from the table
        args_dict = {}
        for col in range(2, table.columnCount(), 2):
            
            if table.cellWidget(row, col) in [None, ""]:
                break
            arg = table.cellWidget(row, col).text()
            widget = table.cellWidget(row, col+1)
            
            if arg in OPERATORS and self.windowTitle() == "Edit Algorithms":
                value = self.getOperator(arg, widget.currentText(), pf, n_obj)
            elif isinstance(widget, (ScientificSpinBox, ScientificDoubleSpinBox)):
                value = widget.value()       
            elif isinstance(widget, MyCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, MyComboBox):
                value = widget.currentText()
            elif isinstance(widget, MyTextEdit):
                value = widget.text() if widget.text() != "None" else None
                if widget.text() == NO_DEFAULT:
                    raise Exception("No default -> need to set value for arg ", arg, " in row ", row, " of window ", self.windowTitle())
                # try to convert text to int or float
                else:
                    try:
                        value = int(value)
                        debug_print("Arg ", arg, ", with value ", value, " converted to int, from window ", self.windowTitle()) 
                    except:
                        try:
                            value = float(value)
                            debug_print("Arg ", arg, ", with value ", value, " converted to int, from window ", self.windowTitle()) 
                        except:
                            pass
            else:
                raise Exception("Unknown widget type ", type(widget), " for arg ", arg, " in row ", row, " of window ", self.windowTitle())
            
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
        
    def setOperatorComboBox(self, table: QTableWidget, row, col, arg, value):

        items = self.operator_comboBox_items[arg]
                
        if value not in [NO_DEFAULT, None]:
            index = items.index(value)
        else:
            index = -1
        table.setCellWidget(row, col+1, MyComboBox(items, index))
                
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
        
