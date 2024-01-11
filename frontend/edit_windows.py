from numpy import inf
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QTableWidget, QPushButton, QFrame
from PyQt5.uic import loadUi

from backend.get import (get_crossover, get_decomposition, get_mutation,
                         get_reference_directions, get_sampling, get_selection)
from backend.defaults import NO_DEFAULT, OPERATORS, Defaults
from frontend.my_widgets import MyTextEdit, MyComboBox, ScientificDoubleSpinBox, ScientificSpinBox, MyCheckBox, MyMessageBox
from utils.debug import debug_print
from utils.defines import DESIGNER_EDIT_WINDOW, VARIANTS_HELP_MSG, DESIGNER_EDIT_FRAME

def ArgsAreSet(dic: dict) -> bool:
    # check if any of the values in the dict is == NO_DEFAULT
    return not any([value == NO_DEFAULT for value in dic.values()]) 

class OperatorWindow(QDialog):
    def __init__(self, tab_dict, defaults: dict):
        """ tab_dict is a dictionary with the following structure:
                {tab_name: (label, get_function, affected_tables)}"""
        
        super().__init__()
        loadUi(DESIGNER_EDIT_WINDOW, self)
        
        self.frames = {}
        
        for key in tab_dict.keys():
            self.frames[key] = EditFrame(key, tab_dict[key], defaults)
            self.tabWidget.addTab(self.frames[key], key)
            
        self.save_button.clicked.connect(self.save)
        
    def save(self):
        for frame in self.frames.values():
            frame.updateTables() if frame.isChanged() else None
        
        self.close()

class EditWindow(OperatorWindow):
    def __init__(self, tab_dict, defaults: dict):
        """ tab_dict is a dictionary with the following structure:
                {tab_name: (label, get_function, affected_tables)}"""
        super().__init__(tab_dict, defaults)
        
        # find algorithm frame 
        algo_frame = self.frames["algorithm"]
        tables = [algo_frame.defaults_table, algo_frame.variants_table]

        op_tab_dict = { "mutation": ("Edit Mutations", get_mutation, tables),
                        "crossover": ("Edit Crossovers", get_crossover, tables),
                        "selection": ("Edit Selections", get_selection, tables),
                        "sampling": ("Edit Samplings", get_sampling, tables),
                        "decomposition": ("Edit Decompositions", get_decomposition, tables),
                        "ref_dirs": ("Edit Ref_dirs", get_reference_directions, tables)}
                
        self.operator_window = OperatorWindow(op_tab_dict, defaults)
        
        # add the atritbute to the algo frame to get_operator()
        self.operators_button = QPushButton("Edit Operators")
        self.operators_button.clicked.connect(self.openOperatorWindow)

        # add and connect the button to open the operators window from the algo frame
        algo_frame.layout.addWidget(self.operators_button)
        algo_frame.op_frames = self.operator_window.frames
        
    def openOperatorWindow(self):
        self.operator_window.show()
    
class EditFrame(QFrame):
    def __init__(self, key, args: tuple, defaults: dict):
        super().__init__()
        
        loadUi(DESIGNER_EDIT_FRAME, self)
        
        self.key = key
        label, self.get_function, self.affected_tables = args
        self.table_dict = defaults[key] 
        self.default_ids = list(self.table_dict.keys())
        self.variant_ids = []
        
        self.label.setText(label)
        
        if key == "algorithm":
            self.op_frames = None
            self.operator_comboBox_items = {key: [key] + list(defaults[key].keys()) for key in OPERATORS} 
        
        # modify what the save and help buttons do
        self.variantsHelpButton.clicked.connect(self.variantsHelp)
                
        # set default table from table_dict and variant table 
        self.setDefaultTable()
        self.setVariantTable(self.defaults_table)
            
    def updateComboBoxItems(self, items: list):
        # if there is just one table, is main window, get all the comboboxes from the table
        if len (self.affected_tables) == 1:
            table = self.affected_tables[0]
            comboBoxes = [table.cellWidget(x,0) for x in range(table.rowCount()) if table.cellWidget(x, 0) is not None]     
        # Else is algo window, check cell by cell for the operator comboboxes    
        else: 
            comboBoxes = []
            for table in self.affected_tables:
                for row in range(table.rowCount()):
                    for col in range(2, table.columnCount(), 2):
                        arg = table.cellWidget(row, col)
                        if arg is not None and arg.text() == self.op_name:
                            comboBoxes.append(table.cellWidget(row, col+1))
        
        # update the comboboxes in the respective MainWindow table widget
        for comboBox in comboBoxes:
            curr_text = comboBox.currentText()
            comboBox.clear()
            comboBox.addItems(items)
            location = items.index(curr_text) if curr_text in items else -1
            comboBox.setCurrentIndex(location)                  
        
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
                
        raise Exception("Object ID '", object_id, "' not found in table from tab ", self.key)
            
    def getObjectFromRow(self, table: QTableWidget, row, pf=None, n_obj=None):
        # get the object from the table
        if isinstance(table.cellWidget(row, 1), MyTextEdit):
            class_name = table.cellWidget(row, 1).text()
        else:
            class_name = table.cellWidget(row, 1).currentText()
        args_dict = self.getArgsFromRow(table, row, pf, n_obj)
        
        # get the n_dim from the problem n_obj    
        if self.key == "ref_dirs":
            for arg in ["n_dim", "n_points", "partitions"]:
                self.check_ref_dirs_dependency(args_dict, arg, n_obj)    
        # get the pf from the problem pf
        elif self.key == "pi":
            if "pf" in args_dict and args_dict["pf"] == 'get from problem':
                args_dict["pf"] = pf
            
        obj = self.get_function(class_name, **args_dict)
        
        if obj is None:
            raise Exception("Object ID matched, but problem getting it from the class", class_name, "in table from tab ", self.key)
        else:
            return obj
        
    def check_ref_dirs_dependency(self, args_dict, arg, n_obj):
        if arg in args_dict and args_dict[arg].startswith("n_obj*"):
            factor_str = args_dict[arg].split("*")[1]
            try:
                factor = int(factor_str)
            except ValueError:
                raise ValueError("Invalid value for n_dim factor: ", factor_str)
            args_dict[arg] = n_obj * factor if n_obj is not None else None
    
    def getArgsFromRow(self, table: QTableWidget, row: int, pf = None, n_obj=None):
        # get the args from the table
        args_dict = {}
        for col in range(2, table.columnCount(), 2):
            
            if table.cellWidget(row, col) in [None, ""]:
                break
            arg = table.cellWidget(row, col).text()
            widget = table.cellWidget(row, col+1)
            
            if arg in OPERATORS and self.key == "algorithm":
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
                    pass
                    # raise Exception("No default -> need to set value for arg ", arg, " in row ", row, " of tab ", self.key)
                # try to convert text to int or float
                else:
                    try:
                        value = int(value) #@IgnoreException
                        debug_print("Arg ", arg, ", with value ", value, " converted to int, from tab ", self.key)
                    except:
                        try:
                            value = float(value) #@IgnoreException
                            debug_print("Arg ", arg, ", with value ", value, " converted to int, from tab ", self.key)
                        except:
                            pass
            else:
                raise Exception("Unknown widget type ", type(widget), " for arg ", arg, " in row ", row, " of tab ", self.key)
            
            args_dict[arg] = value
        return args_dict    
        
    def setOperatorComboBox(self, table: QTableWidget, row, col, arg, value):

        items = self.operator_comboBox_items[arg]
                
        if value not in [NO_DEFAULT, None]:
            index = items.index(value)
        else:
            index = -1
        table.setCellWidget(row, col+1, MyComboBox(items, index))
                
    def getOperator(self, op_name: str, op_id: str, pf = None, n_obj=None):
        
        if op_name not in OPERATORS:
            raise Exception("Operator " + op_name + " not found, with id " + op_id)
        else:
            return self.op_frames[op_name].getObjectFromID(op_id, pf, n_obj)
    
    def isChanged(self):
        # check if the variant table has changed
        for row in range(self.variants_table.rowCount()):
            if self.variants_table.cellWidget(row, 0) is not None and ArgsAreSet(self.getArgsFromRow(self.variants_table, row)):
                return True
        return False
    
    def updateTables(self):
        new_variant_ids = []
        table = self.variants_table
        # get the variants from the table
        for row in range(table.rowCount()):
            if table.cellWidget(row, 0) is not None and ArgsAreSet(self.getArgsFromRow(table, row)):
                new_variant_ids.append(table.cellWidget(row, 0).text())
        # if the variant ids have changed, change the respective ComboBoxes 
        if sorted(new_variant_ids) != sorted(self.variant_ids):
            self.variant_ids = new_variant_ids
            items = self.variant_ids + self.default_ids
            self.updateComboBoxItems(items)
        # close window
        self.close()
