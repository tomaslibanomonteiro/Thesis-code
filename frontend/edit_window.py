from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QFrame, QTabBar, QWidget, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal

from simpleeval import simple_eval
from numpy import inf

from frontend.small_widgets import MyLineEdit, MyComboBox, ScientificDoubleSpinBox, ScientificSpinBox, MyCheckBox, MyWidgetsFrame, MyEmptyLineEdit
from utils.utils import myFileManager, MyMessageBox
from utils.defines import (DESIGNER_EDIT_WINDOW, DESIGNER_EDIT_TAB, NO_DEFAULT, OPERATORS, ID_COL, OPERATORS_ARGS_DICT, 
                           RUN_OPTIONS_ARGS_DICT, PROB_KEY, ALGO_KEY, TERM_KEY, PI_KEY, REF_DIR_KEY, CROSS_KEY, CLASS_KEY,
                           DECOMP_KEY, MUT_KEY, SAMP_KEY, SEL_KEY, VARIANT, MOO_KEY, CONVERT_KEY, CONVERTIBLES, 
                           WRITABLE_ARG_KEY, PLOT_TYPES_ARG_DICT, PARAMETERS_ARGS_DICT, PLOT_TYPES_KEY)

class EditWindow(QWidget):
    """
        Used to create a window to edit parameters of the objects that are called in the MainWindow. 
        
        Signals
        -----------
        It has two PyQt signals, runOptionsUpdates and operatorUpdates, which are used to communicate 
        changes of the MyEditText widgets that contain the IDs to the comboBoxes, so they are updated. 
        
        runOptionsUpdates(str, list) - All comboBoxes from the main window are connected. If the string matches
        the one from their table id, updates the current items to the ones in the list, matching with the 
        new/removed IDs
        
        operatorUpdates(str, list) - All operator comboBoxes from the 'Edit Algorithms' Tab  are connected. If the string matches
        the operator ID, updates the current items to the ones in the list, matching with the new/removed IDs
        
        Important Methods
        -----------------
        
        tabsToDict() -> dict:
            Converts the tabs in the window back into a dictionary of parameters.
        saveParameters():
            Saves the parameters from all the tabs into a dictionary and saves it to a file.

        dictToTabs(parameters: dict):
            Converts a dictionary of parameters into tabs in the window.
        loadParameters():
            Loads parameters from a file and converts them into tabs in the window.
    """    
    runOptionsUpdates = pyqtSignal(str,list) 
    operatorUpdates = pyqtSignal(str,list)

    def __init__(self, parameters: dict, moo: bool):
        super().__init__()

        loadUi(DESIGNER_EDIT_WINDOW, self)
        
        self.widgets_frame = MyWidgetsFrame()
        self.moo = moo
        self.dictToTabs(parameters)
        
        self.setUI()
    
    def setUI(self):
        
        self.setWindowTitle("Edit Parameters")
        
        # Add a spacer so that the height remains the same when all other tabs are closed
        spacer = QWidget()
        spacer.setFixedHeight(20)
        spacer.setFixedWidth(1)
        self.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, spacer)

    
        # set the buttons
        self.open_operators.clicked.connect(lambda: self.openTabsFromList(list(OPERATORS_ARGS_DICT.keys())))
        self.open_run_options.clicked.connect(lambda: self.openTabsFromList(list(RUN_OPTIONS_ARGS_DICT.keys())))
        self.save_parameters.clicked.connect(self.saveParameters)
        self.load_parameters.clicked.connect(self.loadParameters)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        
        # set the open tab buttons
        self.open_algorithms.clicked.connect(lambda: self.openTab(ALGO_KEY))
        self.open_pi.clicked.connect(lambda: self.openTab(PI_KEY))
        self.open_problems.clicked.connect(lambda: self.openTab(PROB_KEY))
        self.open_terminations.clicked.connect(lambda: self.openTab(TERM_KEY))
        self.open_ref_dirs.clicked.connect(lambda: self.openTab(REF_DIR_KEY))
        self.open_crossovers.clicked.connect(lambda: self.openTab(CROSS_KEY))
        self.open_decompositions.clicked.connect(lambda: self.openTab(DECOMP_KEY))
        self.open_mutations.clicked.connect(lambda: self.openTab(MUT_KEY))
        self.open_samplings.clicked.connect(lambda: self.openTab(SAMP_KEY))
        self.open_selections.clicked.connect(lambda: self.openTab(SEL_KEY))
        self.open_plot_types.clicked.connect(lambda: self.openTab(PLOT_TYPES_KEY))
            
    def dictToTabs(self, parameters: dict):
        # close all tabs except the first one
        while self.tabWidget.count() > 1:
            self.tabWidget.removeTab(1)
            
        self.tabs = {tab_key: EditTab(self, tab_key, tab_args, parameters) for tab_key, tab_args in {**OPERATORS_ARGS_DICT, **PLOT_TYPES_ARG_DICT}.items()}            
        self.tabs.update({tab_key: EditTab(self, tab_key, tab_args, parameters) for tab_key, tab_args in RUN_OPTIONS_ARGS_DICT.items()})

    def tabsToDict(self) -> dict:
        """Go through all the tabs and get the parameters as a dictionary, where the key is the tab name
        and the value is a dictionary with the parameters. dont forget to get the operators"""
        
        parameters = {}
        for _, tab in self.tabs.items():
            parameters[tab.key] = tab.tableToDict()
        
        parameters[MOO_KEY] = self.moo
        return parameters
        
    def closeTab(self, index):
        # close the tab with the index
        self.tabWidget.removeTab(index)

    def openTab(self, tab_key: str):
        self.tabWidget.addTab(self.tabs[tab_key], self.tabs[tab_key].name)
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
    
    ###### BUTTONS ######

    def openTabsFromList(self, tab_keys: list):
        # close all tabs except the first one
        while self.tabWidget.count() > 1:
            self.tabWidget.removeTab(1)
            
        for tab_key in tab_keys:
            self.tabWidget.addTab(self.tabs[tab_key], self.tabs[tab_key].name)
        self.tabWidget.setCurrentIndex(1)
        
    def saveParameters(self):
        """Go through all the tabs and save the parameters as a dictionary, where the key is the tab name
        and the value is a dictionary with the parameters. dont forget to save the operators"""
        
        parameters = self.tabsToDict()
        moo = "moo" if self.moo else "soo"
        myFileManager('Save Parameters', f'{moo}_parameters', parameters)
    
    def loadParameters(self): #! NEEDS FIX NOT SENDING LAST SIGNAL TO THE COMBOBOXES IN MAIN WINDOW
        """Load the parameters"""
        
        # Open file dialog to select the file to load
        keys = list(PARAMETERS_ARGS_DICT.keys())
        parameters, _ = myFileManager('Load Parameters', keys_to_check=keys, moo=self.moo)

        if parameters is not None:
            self.dictToTabs(parameters)
                                
class EditTab(QFrame):
    """
        Create a tab that allows users to edit the parameters for the classes that will be instantiated.
        
        Contains a table where each row corresponds to a different object which parameters can be edited. 

        The Table contains buttons to add and remove variants in the table.
        When a variant is added, the class name is set to the same as the default class, and the arguments are set to the same as the default arguments.
        When a variant is removed, the row is removed from the table.
        
        Both these actions emit a signal to update the items in the respective comboBoxes.
        Fo example if a variant is added in the algorithms: 'nsga2 variant',the signal is emitted
        to update the items in the comboBoxes from the Algorithm Table in Main window.
        
        
        Attributes
        ------------
            edit_window: The main window where the tab is located.
            key: A string to identify the tab.
            tab_args: A tuple containing arguments for the tab.
            parameters: A dictionary containing parameters for the tab.
    """
    def __init__(self, edit_window: EditWindow, key: str, tab_args: tuple, parameters: dict):
        super().__init__()
        
        loadUi(DESIGNER_EDIT_TAB, self)
        
        self.edit_window = edit_window
        self.key = key
        self.name, label, self.get_function = tab_args
        self.initial_table_dict = parameters[self.key]
    
        self.label.setText(label)
        self.dictToTable(self.initial_table_dict)
                    
    ###### EDIT TABLES ######
    
    def dictToTable(self, table_dict: dict):
        
        # add a customable arg in the end
        for key in table_dict.keys():
            table_dict[key]["(Custom Arg)" + WRITABLE_ARG_KEY] = ""
        
        # store all different keys in table_dict
        self.classes = [table_dict[key][CLASS_KEY] for key in table_dict.keys() if table_dict[key][CLASS_KEY] == key]
        self.default_ids = []
        for row_id, row_dict in table_dict.items():
            if row_dict[CLASS_KEY] not in self.classes:
                MyMessageBox(f"Error: Class {row_dict[CLASS_KEY]} in tab {self.key} does not have a default class. Please choose a valid parameters dictionary. ")
                return
            else:
                self.default_ids.append(row_id)
                
        # +1 to add the button column (at least 4 columns)
        n_cols = max([len(row_dict) for row_dict in table_dict.values()] + [3]) * 2 + 1  
        self.table.setColumnCount(n_cols)
        
        # erase the column headers from the 5th column onwards
        for col in range(4, n_cols):
            self.table.setHorizontalHeaderItem(col, QTableWidgetItem(""))
        variants = {}
        row = 0
        # set the table items from the table, each row is a list of the arguments and values of the class
        for row_id, row_dict in table_dict.items():
            # check if it is a variant or a default class and set the row accordingly
            if row_dict[CLASS_KEY] == row_id:
                self.table.setRowCount(row+1)
                self.addDefault(row_dict.pop(CLASS_KEY), row_id, row_dict, row)
                row += 1
            else:
                variants[row_id] = row_dict
        
        for row_id, row_dict in variants.items():
            self.addVariant(row_dict.pop(CLASS_KEY), row_id, row_dict)
            
    def addDefault(self, class_name: str, id:str, args_dict:dict, row:int):
        widgets_frame = self.edit_window.widgets_frame
        
        # add the id and class name in the first columns
        id_widget = MyLineEdit(id, "default_id", widgets_frame, True)
        self.table.setCellWidget(row, ID_COL, id_widget)
        class_widget = MyLineEdit(class_name, "default_class", widgets_frame, True)
        self.table.setCellWidget(row, ID_COL+1, class_widget)
        
        final_col = ID_COL+2
        # add the arguments and values in the rest of the columns
        for col, (arg, value) in zip(range(ID_COL+2, self.table.columnCount(), 2), list(args_dict.items())): 
            self.setTablePair(self.table, row, col, arg, value)
            final_col = col+2
        
        # set the rest of the items in the row non editable
        for col1 in range(final_col, self.table.columnCount()):
            # Create a non-editable QLineEdit widget with a transparent background
            self.table.setCellWidget(row, col1, MyEmptyLineEdit())                  
            
        # add "Add Variant" button at the end of the row
        add_variant_button = QPushButton("Add Variant")
        add_variant_button.setStyleSheet("color: green;")
        class_name = self.table.cellWidget(row, ID_COL+1).text()  # get the class name from the third column
        add_variant_button.clicked.connect(lambda checked, cn=class_name: self.addVariant(cn))
        self.table.setCellWidget(row, 0, add_variant_button)

    def addVariant(self, class_name: str, id:str = None, args_dict:dict = None):
        
        widgets_frame = self.edit_window.widgets_frame
        
        row = self.table.rowCount()
        self.table.insertRow(row)
                
        # scroll to the bottom of the table
        self.table.scrollToBottom()        
        
        # set the text edit with table to check if the id is unique
        id = id if id is not None else class_name + VARIANT
        
        id_widget = MyLineEdit(id, "variant_id", widgets_frame, tab=self)
        self.table.setCellWidget(row, ID_COL, id_widget)
        
        # connect the signal to the slot to update the items in the other tables
        if self.key in RUN_OPTIONS_ARGS_DICT.keys():
            id_widget.itemsSignal.connect(self.edit_window.runOptionsUpdates.emit)
        else:
            id_widget.itemsSignal.connect(self.edit_window.operatorUpdates.emit)
            
        # add a MyComboBox in the new row and set it to the class name
        combo_box = MyComboBox(self.classes, table=self.table, col=ID_COL+1, row=row, copy_style="variant_class", widgets_frame=widgets_frame)
        self.table.setCellWidget(row, ID_COL+1, combo_box)
        self.table.cellWidget(row, ID_COL+1).setCurrentIndex(self.classes.index(class_name))

        # functionalities if the call was not made from the "Add Variant" button
        if args_dict is not None: 
            # set the id again because it is overwritten by the combo box
            self.table.cellWidget(row, ID_COL).setText(id)

            # set the default args in the new row
            for col in range(ID_COL+2, self.table.columnCount()):
                self.table.cellWidget(row, col).deleteLater() if self.table.cellWidget(row, col) is not None else None
            
            final_col = ID_COL+2
            for col, (arg, value) in zip(range(ID_COL+2, self.table.columnCount(), 2), list(args_dict.items())):
                self.setTablePair(self.table, row, col, arg, value)
                final_col = col
        
            # set the rest of the items in the row non editable
            for col1 in range(final_col+2, self.table.columnCount()):
                # Create a non-editable QLineEdit widget with a transparent background
                self.table.setCellWidget(row, col1, MyEmptyLineEdit())                  

        # add a remove button in the new row
        remove_button = QPushButton("Remove")
        remove_button.setStyleSheet("color: red;")        
        remove_button.clicked.connect(lambda: self.removeVariant(id_widget))        
        self.table.setCellWidget(row, 0, remove_button)

    def removeVariant(self, id_widget: MyLineEdit):
        # find the row through the button
        row = self.table.indexAt(id_widget.pos()).row()
        # emit a signal to update the items in the other tables
        items = id_widget.makeUnique()
        items = [item for item in items if item != id_widget.text()]
        id_widget.itemsSignal.emit(id_widget.tab.key, items)
        self.table.removeRow(row)
        
    def setTablePair(self, table: QTableWidget, row: int, col: int, arg: str, value) -> None:
        
        widgets_frame = self.edit_window.widgets_frame
        # Set the widget in the arg column (always text)
        if arg.endswith(WRITABLE_ARG_KEY):
            arg = arg[:-len(WRITABLE_ARG_KEY)]
            widget = MyLineEdit(arg, "arg", widgets_frame, False)
        else:
            widget = MyLineEdit(arg, "arg", widgets_frame, True)
        table.setCellWidget(row, col, widget)    
        
        #  BOOL
        if isinstance(value, bool):
            widget = MyCheckBox(value, widgets_frame)
        # INT
        elif isinstance(value, int):
            widget = ScientificSpinBox(widgets_frame)
            widget.setValue(value)
        # FLOAT
        elif isinstance(value, float):
            widget = ScientificDoubleSpinBox(widgets_frame)
            if value == inf:
                widget.setValue(widget.maximum())
            elif value == -inf:
                widget.setValue(widget.minimum())
            else:
                widget.setValue(value)
        # COMBO BOX
        elif self.key == ALGO_KEY and arg in OPERATORS:
            items = self.edit_window.tabs[arg].initial_table_dict.keys()
            widget = MyComboBox(items, value, table=self.table, tab=self, key=arg, copy_style="comboBox", widgets_frame=widgets_frame)
        # NONE
        elif value is None:
            widget = MyLineEdit(str(value), "none", widgets_frame)
        elif isinstance(value, str):
            # NO DEFAULT
            if value == NO_DEFAULT:
                widget = MyLineEdit(NO_DEFAULT, "no_def", widgets_frame)
            # STRING TO BE CONVERTED
            elif value.endswith(CONVERT_KEY):
                value = value[:-len(CONVERT_KEY)]
                widget = MyLineEdit(value, "convert", widgets_frame)
            # PLAIN STRING
            else:
                widget = MyLineEdit(value, "value", widgets_frame)
        else:
            raise Exception("Unknown value type ", type(value), " for arg ", arg, " in row ", row, " of tab ", self.name)
        
        table.setCellWidget(row, col+1, widget)            
                        
    ###### EXTRACT FROM TABLES ######

    def tableToDict(self) -> dict:
        # get the table items from the table, each row is a list of the arguments and values of the class
        table_dict = {}
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, ID_COL+1)
            if widget is None:
                continue
            
            row_id = self.table.cellWidget(row, ID_COL).text()
            row_dict = self.getArgsFromRow(self.table, row, convert=False)
            table_dict[row_id] = row_dict
            class_name = widget.text() if isinstance(widget, MyLineEdit) else widget.currentText()
            table_dict[row_id][CLASS_KEY] = class_name
            
        return table_dict

    def getObjectFromID(self, object_id, **kwargs):
        # get the object from a table
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, ID_COL) is None:
                continue
            if self.table.cellWidget(row, ID_COL).text() == object_id:
                return self.getObjectFromRow(self.table, row, **kwargs)
            
        MyMessageBox(f"Object ID '{object_id}' not found in table from tab {self.name}")
        
        return Exception("Object ID '", object_id, "' not found in table from tab ", self.name) 
            
    def getObjectFromRow(self, table: QTableWidget, row, **kwargs):
        # get the object from the table
        if isinstance(table.cellWidget(row, ID_COL+1), MyLineEdit):
            class_name = table.cellWidget(row, ID_COL+1).text()
        else:
            class_name = table.cellWidget(row, ID_COL+1).currentText()
        args_dict = self.getArgsFromRow(table, row, **kwargs)

        if not isinstance(args_dict, Exception):
            try:
                obj = self.get_function(class_name, args_dict=args_dict, **kwargs) #@IgnoreException
            except Exception as e:
                MyMessageBox(f"Error trying to get {class_name} from tab {self.key}:\n{e}"
                            "\nMake sure all arguments are correctly set for the respective class")
                obj = e
        else:
            obj = args_dict
                                
        return obj
                    
    def getArgsFromRow(self, table: QTableWidget, row: int, convert=True, **kwargs) -> dict:
        # get the args from the table
        args_dict = {}
        for col in range(ID_COL+2, table.columnCount(), 2):
            # break in the end of the row
            if table.cellWidget(row, col) in [None, ""] or isinstance(table.cellWidget(row, col), MyEmptyLineEdit):
                break
    
            # get the arg and the widget
            arg = table.cellWidget(row, col).text()
            widget = table.cellWidget(row, col+1)
            
            # OPERATOR
            if arg in OPERATORS and self.key == ALGO_KEY and convert:
                value = self.getOperator(arg, widget.currentText(), **kwargs)
            # COMBO BOX STRING
            elif isinstance(widget, MyComboBox):
                value = widget.currentText()
            # INT OR FLOAT
            elif isinstance(widget, (ScientificSpinBox, ScientificDoubleSpinBox)):
                value = widget.value()       
            # BOOL
            elif isinstance(widget, MyCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, MyLineEdit):
                value = widget.text() 
                # IGNORE EMPTY STRING 
                if value == '':
                    continue
                # NONE
                elif value == 'None':
                    value = None
                # NO DEFAULT
                elif value == NO_DEFAULT:
                    value = NO_DEFAULT
                # IDENTIFY CONVERTIBLE STRING IF EXPORTING
                elif not convert:
                    value = widget.text() + CONVERT_KEY if widget.convert else widget.text()
                # CONVERT STRING
                elif widget.convert: 
                    value = self.convertString(arg, value, **kwargs)
            else:
                raise Exception("Unknown widget type ", type(widget), " for arg ", arg, " in row ", row, " of tab ", self.name)
            
            if isinstance(value, Exception):
                return value
            else:
                args_dict[arg] = value

        return args_dict    
    
    def convertString(self, arg, string: str, **kwargs):
    
        for key, value in kwargs.items():
            if string == key:
                return value
            elif key in string:
                string = string.replace(key, str(value))
        try:
            result = simple_eval(string) #@IgnoreException
        except: 
            MyMessageBox(f"Invalid expression \'{string}\'in argument \'{arg}\', please use a valid mathematical expression with the convertibles if needed: {CONVERTIBLES}")
            result = None
            
        return result
    
    def getOperator(self, op_name: str, op_id: str, **kwargs):
        
        if op_name not in OPERATORS:
            raise Exception("Operator " + op_name + " not found, with id " + op_id)
        else:
            return self.edit_window.tabs[op_name].getObjectFromID(op_id, **kwargs)
    
