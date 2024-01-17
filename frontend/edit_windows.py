from numpy import inf
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QTableWidget, QPushButton, QFrame, QHBoxLayout
from PyQt5.uic import loadUi
from backend.get import (get_crossover, get_decomposition, get_mutation,
                         get_reference_directions, get_sampling, get_selection)
from frontend.my_widgets import MyTextEdit, MyComboBox, ScientificDoubleSpinBox, ScientificSpinBox, MyCheckBox, MyMessageBox
from utils.debug import debug_print
from utils.defines import DESIGNER_EDIT_WINDOW, DESIGNER_EDIT_FRAME, NO_DEFAULT, OPERATORS, ID_COL
from copy import deepcopy #!

def ArgsAreSet(dic: dict) -> bool:
    # check if any of the values in the dict is == NO_DEFAULT
    return not any([value == NO_DEFAULT for value in dic.values()]) 

class OperatorWindow(QDialog):
    def __init__(self, tab_args: dict, parameters: dict):
        """ tab_args is a dictionary with the following structure:
                {tab_name: (label, get_function, affected_tables)}"""
        
        super().__init__()
        loadUi(DESIGNER_EDIT_WINDOW, self)
        
        self.tabs = {}
        
        for tab_name in tab_args.keys():
            self.tabs[tab_name] = EditTab(tab_name, tab_args[tab_name], parameters)
            self.tabWidget.addTab(self.tabs[tab_name], tab_name)
            
        self.save_button.clicked.connect(self.save)
        
    def save(self):
        for tab in self.tabs.values():
            tab.updateTables()

        self.close()

class EditWindow(OperatorWindow):
    def __init__(self, tab_args: dict, parameters: dict):
        """ tab_args is a dictionary with the following structure:
                {tab_name: (label, get_function, affected_tables)}"""
        super().__init__(tab_args, parameters)
        
        algo_tab = self.tabs["algorithm"]

        op_tab_dict = { "mutation": ("Edit Mutations", get_mutation, algo_tab.table),
                        "crossover": ("Edit Crossovers", get_crossover, algo_tab.table),
                        "selection": ("Edit Selections", get_selection, algo_tab.table),
                        "sampling": ("Edit Samplings", get_sampling, algo_tab.table),
                        "decomposition": ("Edit Decompositions", get_decomposition, algo_tab.table),
                        "ref_dirs": ("Edit Ref_dirs", get_reference_directions, algo_tab.table)}
                
        self.operator_window = OperatorWindow(op_tab_dict, parameters)
        
        # add the button to open Operator Window in the bottom of the EditWindow
        self.operators_button = QPushButton("Edit Operators")
        self.operators_button.clicked.connect(self.openOperatorWindow)
        self.operators_button.setFixedWidth(150)
        self.operators_button.setFixedHeight(50)
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.operators_button)
        button_layout.addStretch(1)

        # add the button layout to the algo_tab layout
        algo_tab.layout.addLayout(button_layout)        
        
        algo_tab.op_tabs = self.operator_window.tabs
        
    def openOperatorWindow(self):
        self.operator_window.show()
        
class EditTab(QFrame):
    def __init__(self, name: str, tab_args: tuple, parameters: dict):
        super().__init__()
        
        loadUi(DESIGNER_EDIT_FRAME, self)
        
        self.name = name
        label, self.get_function, self.affected_tables = tab_args
        self.table_dict = parameters[name]
        self.default_ids = list(self.table_dict.keys())        
        self.classes = [self.table_dict[key]["class"] for key in self.default_ids]
        self.label.setText(label)

        # modify what the save and help buttons do
        self.helpButton.clicked.connect(self.variantsHelp)
        
        if name == "algorithm":
            self.op_tabs = None
            self.operator_comboBox_items = {key: [key] + list(parameters[key].keys()) for key in OPERATORS} 
         
        self.dictToTable(self.table_dict)
    
    ###### GENERAL METHODS ######
                    
    def variantsHelp(self):
        helpbox = MyMessageBox("To create variants of the default classes, choose a class from the comboBox."
                               " The arguments will be inherited from the default class", "Variants Help", warning_icon=False)
        
    ###### EDIT TABLES ######
    
    def dictToTable(self, table_dict: dict):
        
        n_cols = max([len(row_dict) for row_dict in table_dict.values()]) * 2 + 1  # +1 to add the button column
        self.table.setColumnCount(n_cols)

        # set col names
        for i in range(ID_COL+2, n_cols, 2):
            self.table.setHorizontalHeaderItem(i, QTableWidgetItem("Arg" + str(int(i-1))))
            self.table.setHorizontalHeaderItem(i+1, QTableWidgetItem("Value"))

        variants = {}
        row = 0
        # set the table items from the table, each row is a list of the arguments and values of the class
        for row_id, row_dict in table_dict.items():
            # check if it is a variant or a default class and set the row accordingly
            if row_dict["class"] == row_id:
                self.table.setRowCount(row+1)
                self.addDefault(row_dict.pop("class"), row_id, row_dict, row)
                row += 1
            else:
                variants[row_id] = row_dict
                
        for row_id, row_dict in variants.items():
            self.addVariant(row_dict.pop("class"), row_id, row_dict)
            
    def addDefault(self, class_name: str, id:str, args_dict:dict, row:int):
        
        # add the id and class name in the first columns
        self.setTablePair(self.table, row, ID_COL, id, class_name, editable=False)
        
        # add the arguments and values in the rest of the columns
        for col, (arg, value) in zip(range(ID_COL+2, self.table.columnCount(), 2), list(args_dict.items())): 
            self.setTablePair(self.table, row, col, arg, value)

        # add "Add Variant" button at the end of the row
        add_variant_button = QPushButton("Add Variant")
        add_variant_button.setStyleSheet("color: green;")
        class_name = self.table.cellWidget(row, ID_COL+1).text()  # get the class name from the third column
        add_variant_button.clicked.connect(lambda checked, cn=class_name: self.addVariant(cn))
        self.table.setCellWidget(row, 0, add_variant_button)

    def addVariant(self, class_name: str, id:str = None, args_dict:dict = None):
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # add a MyComboBox in the new row and set it to the class name
        combo_box = MyComboBox(self.classes, table=self.table, col=ID_COL+1, row=row)
        self.table.setCellWidget(row, ID_COL+1, combo_box)
        self.table.cellWidget(row, ID_COL+1).setCurrentIndex(self.classes.index(class_name))
        
        # add a remove button in the new row
        remove_button = QPushButton("Remove")
        remove_button.setStyleSheet("color: red;")        
        remove_button.clicked.connect(lambda: self.removeVariant(self.table.rowCount()-1))
        self.table.setCellWidget(row, 0, remove_button)

        # scroll to the bottom of the table
        self.table.scrollToBottom()        
        
        # fucntionalities if the call was not made from the "Add Variant" button
        
        if id is not None: # set the id in the new row
            self.table.setCellWidget(row, ID_COL, MyTextEdit(id))
            
        if args_dict is not None: # set the default args in the new row
            for col in range(ID_COL+2, self.table.columnCount()):
                self.table.cellWidget(row, col).deleteLater() if self.table.cellWidget(row, col) is not None else None
            for col, (arg, value) in zip(range(ID_COL+2, self.table.columnCount(), 2), list(args_dict.items())):
                self.setTablePair(self.table, row, col, arg, value)
        
    def removeVariant(self, row):
        # remove the row from the table
        self.table.removeRow(row)
             
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

        items = self.operator_comboBox_items[arg]
                
        if value not in [NO_DEFAULT, None]:
            index = items.index(value)
        else:
            index = -1
        table.setCellWidget(row, col+1, MyComboBox(items, index))
                
    ###### EXTRACT FROM TABLE ######

    def tableToDict(self) -> dict:
        # get the table items from the table, each row is a list of the arguments and values of the class
        table_dict = {}
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, ID_COL+1)
            if widget is None:
                continue
            
            row_id = self.table.cellWidget(row, ID_COL).text()
            row_dict = self.getArgsFromRow(self.table, row, get_operator_obj=False)
            table_dict[row_id] = row_dict
            class_name = widget.text() if isinstance(widget, MyTextEdit) else widget.currentText()
            table_dict[row_id]["class"] = class_name
            
        return table_dict

    def getObjectFromID(self, object_id, pf=None, n_obj=None):
        # get the object from a table
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, ID_COL) is None:
                continue
            if self.table.cellWidget(row, ID_COL).text() == object_id:
                return self.getObjectFromRow(self.table, row, pf, n_obj)
                
        raise Exception("Object ID '", object_id, "' not found in table from tab ", self.name)
            
    def getObjectFromRow(self, table: QTableWidget, row, pf=None, n_obj=None):
        # get the object from the table
        if isinstance(table.cellWidget(row, ID_COL+1), MyTextEdit):
            class_name = table.cellWidget(row, ID_COL+1).text()
        else:
            class_name = table.cellWidget(row, ID_COL+1).currentText()
        args_dict = self.getArgsFromRow(table, row, pf, n_obj)
        
        # get the n_dim from the problem n_obj    
        if self.name == "ref_dirs":
            for arg in ["n_dim", "n_points", "partitions"]:
                self.check_ref_dirs_dependency(args_dict, arg, n_obj)    
        # get the pf from the problem pf
        elif self.name == "pi":
            if "pf" in args_dict and args_dict["pf"] == 'get from problem':
                args_dict["pf"] = pf
            
        obj = self.get_function(class_name, **args_dict)
        
        if obj is None:
            raise Exception("Object ID matched, but problem getting it from the class", class_name, "in table from tab ", self.name)
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
    
    def getArgsFromRow(self, table: QTableWidget, row: int, pf = None, n_obj=None, get_operator_obj=True) -> dict:
        # get the args from the table
        args_dict = {}
        for col in range(ID_COL+2, table.columnCount(), 2):
            
            if table.cellWidget(row, col) in [None, ""]:
                break
            arg = table.cellWidget(row, col).text()
            widget = table.cellWidget(row, col+1)
            
            if arg in OPERATORS and self.name == "algorithm" and get_operator_obj:
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
                    # raise Exception("No default -> need to set value for arg ", arg, " in row ", row, " of tab ", self.name)
                # try to convert text to int or float
                else:
                    try:
                        value = int(value) #@IgnoreException
                        debug_print("Arg ", arg, ", with value ", value, " converted to int, from tab ", self.name)
                    except:
                        try:
                            value = float(value) #@IgnoreException
                            debug_print("Arg ", arg, ", with value ", value, " converted to int, from tab ", self.name)
                        except:
                            pass
            else:
                raise Exception("Unknown widget type ", type(widget), " for arg ", arg, " in row ", row, " of tab ", self.name)
            
            args_dict[arg] = value
        return args_dict    
    
    def getOperator(self, op_name: str, op_id: str, pf = None, n_obj=None):
        
        if op_name not in OPERATORS:
            raise Exception("Operator " + op_name + " not found, with id " + op_id)
        else:
            return self.op_tabs[op_name].getObjectFromID(op_id, pf, n_obj)
    
    ###### UPDATE COMBOBOXES ######
        
    #!
    def updateTables(self):
        return
        # check if the variant table has changed
        for row in range(self.variants_table.rowCount()):
            if self.variants_table.cellWidget(row, ID_COL) is None or not ArgsAreSet(self.getArgsFromRow(self.variants_table, row)):
                return 

        new_variant_ids = []
        table = self.variants_table
        # get the variants from the table
        for row in range(table.rowCount()):
            if table.cellWidget(row, ID_COL) is not None and ArgsAreSet(self.getArgsFromRow(table, row)):
                new_variant_ids.append(table.cellWidget(row, ID_COL).text())
        # if the variant ids have changed, change the respective ComboBoxes 
        if sorted(new_variant_ids) != sorted(self.variant_ids):
            self.variant_ids = new_variant_ids
            items = self.variant_ids + self.default_ids
            self.updateComboBoxItems(items)
        # close window
        self.close()

    def updateComboBoxItems(self, items: list):
        # if there is just one table, is main window, get all the comboboxes from the table
        if len (self.affected_tables) == 1:
            table = self.affected_tables[ID_COL]
            comboBoxes = [table.cellWidget(x,ID_COL) for x in range(table.rowCount()) if table.cellWidget(x, ID_COL) is not None]     
        # Else is algo window, check cell by cell for the operator comboboxes    
        else: 
            comboBoxes = []
            for table in self.affected_tables:
                for row in range(table.rowCount()):
                    for col in range(ID_COL+2, table.columnCount(), 2):
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

