from numpy import inf
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QTableWidget, QFrame, QTabBar, QWidget, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal, QTimer

from frontend.my_widgets import MyTextEdit, MyComboBox, ScientificDoubleSpinBox, ScientificSpinBox, MyCheckBox, MyMessageBox
from utils.debug import debug_print
from utils.defines import (DESIGNER_EDIT_WINDOW, DESIGNER_EDIT_TAB, NO_DEFAULT, OPERATORS, ID_COL, OPERATORS_ARGS_DICT, 
                           RUN_OPTIONS_ARGS_DICT, ALGO_KEY, REF_DIR_KEY, PI_KEY, VARIANT) 

def ArgsAreSet(dic: dict) -> bool:
    # check if any of the values in the dict is == NO_DEFAULT
    return not any([value == NO_DEFAULT for value in dic.values()]) 


class EditWindow(QDialog):
    itemUpdates = pyqtSignal(str,list) 
    operatorUpdates = pyqtSignal(str,list)
    def __init__(self, main_window, parameters: dict):
        super().__init__()

        loadUi(DESIGNER_EDIT_WINDOW, self)
        self.setWindowTitle("Edit Parameters")

        self.main_window = main_window
        self.parameters = parameters
        
        self.tabs = {tab_key: EditTab(self, tab_key, tab_args) for tab_key, tab_args in OPERATORS_ARGS_DICT.items()}            
        self.tabs.update({tab_key: EditTab(self, tab_key, tab_args) for tab_key, tab_args in RUN_OPTIONS_ARGS_DICT.items()})

        # set open_operators and open_run_options buttons
        self.open_operators.clicked.connect(self.openOperators)
        self.open_run_options.clicked.connect(self.openRunOptions)
        self.open_all_tabs.clicked.connect(self.openAllTabs)
        self.save_parameters.clicked.connect(self.main_window.saveParameters)
        self.load_parameters.clicked.connect(self.main_window.loadParameters)
        self.helpButton.clicked.connect(self.help)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)

        # Add a spacer so that the height remains the same when all other tabs are closed
        spacer = QWidget()
        spacer.setFixedHeight(20)
        spacer.setFixedWidth(1)
        self.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, spacer)

    def closeTab(self, index):
        # close the tab with the index
        self.tabWidget.removeTab(index)
        
    def openOperators(self):
        # close all tabs except the first one
        while self.tabWidget.count() > 1:
            self.tabWidget.removeTab(1)
            
        for tab_key in OPERATORS_ARGS_DICT.keys():
            self.tabWidget.addTab(self.tabs[tab_key], self.tabs[tab_key].name)
        self.tabWidget.setCurrentIndex(len(self.tabWidget)-1)
        
    def openRunOptions(self):
        # close all tabs except the first one
        while self.tabWidget.count() > 1:
            self.tabWidget.removeTab(1)
        
        for tab_key in RUN_OPTIONS_ARGS_DICT.keys():
            self.tabWidget.addTab(self.tabs[tab_key], self.tabs[tab_key].name)
        self.tabWidget.setCurrentIndex(len(self.tabWidget)-1)    
    
    def openAllTabs(self):
        for tab_key in self.tabs.keys():
            self.tabWidget.addTab(self.tabs[tab_key], self.tabs[tab_key].name)    
            
    def help(self):
        MyMessageBox("Click on \"Edit Run Options\" to edit their parameters. Click on \"Edit Operators\" to edit "
                     "the operators parameters that are then used in the algorithms. Click on \"Save Parameters\" "
                     "to save the parameters to a file.", "Help", warning_icon=False)
        
class EditTab(QFrame):
    def __init__(self, edit_window: EditWindow, key: str, tab_args: tuple):
        super().__init__()
        
        loadUi(DESIGNER_EDIT_TAB, self)
        
        self.edit_window = edit_window
        self.key = key
        self.name, label, self.get_function, _ = tab_args
        self.table_dict = edit_window.parameters[self.key]
        self.default_ids = list(self.table_dict.keys())        
        self.classes = [self.table_dict[key]["class"] for key in self.default_ids]
        self.label.setText(label)
        self.helpButton.clicked.connect(self.variantsHelp)
                
        if key == ALGO_KEY:
            self.setAlgorithmTab()

        self.dictToTable(self.table_dict)
    
    ###### GENERAL METHODS ######
    
    def setAlgorithmTab(self):

        # define operator combobox items
        self.operator_comboBox_items = {key: [key] + list(self.edit_window.parameters[key].keys()) for key in OPERATORS} 

        # add the operators button to the algorithm tab
        self.operators_button = QPushButton("Edit Operators")
        self.operators_button.clicked.connect(self.edit_window.openOperators)
        self.operators_button.setFixedWidth(100)
        self.operators_button.setFixedHeight(30)
        
        self.label_layout.insertWidget(3, self.operators_button)        
    
    def variantsHelp(self):
        MyMessageBox("To create variants of the default classes, choose a class from the comboBox."
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
                
        # scroll to the bottom of the table
        self.table.scrollToBottom()        
        
        # set the text edit with table to check if the id is unique
        id = id if id is not None else class_name + VARIANT
        
        text_edit = MyTextEdit(id, self)
        self.table.setCellWidget(row, ID_COL, text_edit)
        
        # connect the signal to the slot to update the items in the other tables
        if self.key in RUN_OPTIONS_ARGS_DICT.keys():
            text_edit.itemsSignal.connect(self.edit_window.itemUpdates.emit)
        else:
            text_edit.itemsSignal.connect(self.edit_window.operatorUpdates.emit)
                    
        # add a MyComboBox in the new row and set it to the class name
        combo_box = MyComboBox(self.classes, table=self.table, col=ID_COL+1, row=row)
        self.table.setCellWidget(row, ID_COL+1, combo_box)
        self.table.cellWidget(row, ID_COL+1).setCurrentIndex(self.classes.index(class_name))

        # functionalities if the call was not made from the "Add Variant" button
        if args_dict is not None: # set the default args in the new row
            for col in range(ID_COL+2, self.table.columnCount()):
                self.table.cellWidget(row, col).deleteLater() if self.table.cellWidget(row, col) is not None else None
            for col, (arg, value) in zip(range(ID_COL+2, self.table.columnCount(), 2), list(args_dict.items())):
                self.setTablePair(self.table, row, col, arg, value)
        
        # add a remove button in the new row
        remove_button = QPushButton("Remove")
        remove_button.setStyleSheet("color: red;")        
        remove_button.clicked.connect(lambda: self.removeVariant(text_edit))        
        self.table.setCellWidget(row, 0, remove_button)

    def removeVariant(self, text_edit: MyTextEdit):
        # find the row through the button
        row = self.table.indexAt(text_edit.pos()).row()
        print(f"Removing row {row}")
        # emit a signal to update the items in the other tables
        items = text_edit.makeUnique()
        items = [item for item in items if item != text_edit.text()]
        text_edit.itemsSignal.emit(text_edit.tab.key, items)
        self.table.removeRow(row)
        
    def setTablePair(self, table: QTableWidget, row: int, col: int, arg: str, value, editable: bool = True) -> None:
        
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
        elif self.key == ALGO_KEY and arg in OPERATORS:
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
        table.setCellWidget(row, col+1, MyComboBox(items, index, table=self.table, tab=self, key=arg))
                
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
        if self.key == REF_DIR_KEY:
            for arg in ["n_dim", "n_points", "partitions"]:
                self.check_ref_dirs_dependency(args_dict, arg, n_obj)    
        # get the pf from the problem pf
        elif self.key == PI_KEY:
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
            
            if arg in OPERATORS and self.key == ALGO_KEY and get_operator_obj:
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
            return self.edit_window.tabs[op_name].getObjectFromID(op_id, pf, n_obj)
    
