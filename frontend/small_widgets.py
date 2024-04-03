import re
from typing import Tuple

from PyQt5.QtWidgets import QTableWidget, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit, QMenu, QAction, QFrame
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import QtCore
from PyQt5.QtGui import QValidator
from PyQt5.uic import loadUi

from numpy import inf
from typing import Tuple

from utils.defines import ID_COL, VARIANT, DESIGNER_WIDGETS_FRAME, NO_DEFAULT
from utils.utils import getAvailableName, MyMessageBox

"""
This code has been adapted from: https://gist.github.com/jdreaver/0be2e44981159d0854f5
Changes made are support for PyQt5, localisation, better intermediate state detection and better stepping.
Some inspiration taken from: https://github.com/pyqtgraph/pyqtgraph/blob/develop/pyqtgraph/widgets/SpinBox.py
"""

"""
This code has been adapted from: https://gist.github.com/jdreaver/0be2e44981159d0854f5
Changes made are support for PyQt5, localisation, better intermediate state detection and better stepping.
Some inspiration taken from: https://github.com/pyqtgraph/pyqtgraph/blob/develop/pyqtgraph/widgets/SpinBox.py
"""

# spinBoxes variables
decimal_point = re.escape(QtCore.QLocale().decimalPoint())
exp_regex = r'(([+-]?\d+(' + decimal_point + r'\d*)?|' + decimal_point + r'\d+)([eE][+-]?\d+)?)'
exp_float_re = re.compile(exp_regex)
int_exp_regex = r'(([+-]?\d+(' + decimal_point + r'\d*)?|' + decimal_point + r'\d+)([eE][+]?\d+)?)'
exp_int_re = re.compile(int_exp_regex)
partial_int_re = re.compile(r'([+-]?(\d?))')
valid_int_re = re.compile(r'([+-]?\d*)')
partial_pos_int_regex = re.compile(r'([+]?(\d?))')
partial_pos_int_re = re.compile(partial_pos_int_regex)
partial_float_regex = r'([+-]?((\d*' + decimal_point + r'?))?\d*)'
partial_float_re = re.compile(partial_float_regex)

class MyWidgetsFrame(QFrame):
    """
    A frame that contains various widgets with certain styles. All the widgets from this file 
    will inherit the style and size policy of the respective widgets of the frame, providing a 
    quick way to modify them through the Designer Tool of PyQt5, instead of having to code the 
    desired characteristics. 
    
    Important Method
    ---------------
    
    - copyStyleAndSizePolicy(self, widget, copy_key): Copies the style and size policy of the widget specified by copy_key
    to the given widget. It raises a ValueError if copy_key does not match any known keys.

    copy_key values can be:
    - default_id, variant_id, arg, value, no_def, none, default_class, variant_class, comboBox, spinBox, doubleSpinBox, checkBox.
    """
    def __init__(self):
        super().__init__()
        # Load the .ui file
        loadUi(DESIGNER_WIDGETS_FRAME, self)
        
        # set the font of the widgets
        font = self.font()
        for i in range(self.gridLayout.count()):
            widget = self.gridLayout.itemAt(i).widget()
            if widget is not None:
                curr_stylesheet = widget.styleSheet()
                insert_index = curr_stylesheet.rfind('}')
                if insert_index != -1:
                    new_str = f"\nfont: {font.pointSize()}pt \"{font.family()}\";\n"
                    new_stylesheet = curr_stylesheet[:insert_index] + new_str + curr_stylesheet[insert_index:]
                    widget.setStyleSheet(new_stylesheet)              
    
    def copyStyleAndSizePolicy(self, widget, copy_key):
        if copy_key == "default_id":
            copy_widget = self.default_id
        elif copy_key == "variant_id":
            copy_widget = self.variant_id
        elif copy_key == "arg":
            copy_widget = self.arg
        elif copy_key == "value":
            copy_widget = self.value
        elif copy_key == "convertible":
            copy_widget = self.convertible    
        elif copy_key == "no_def":
            copy_widget = self.no_def
        elif copy_key == "none":
            copy_widget = self.none
        elif copy_key == "default_class":
            copy_widget = self.default_class
        elif copy_key == "variant_class":
            copy_widget = self.variant_class
        elif copy_key == "comboBox":
            copy_widget = self.comboBox
        elif copy_key == "spinBox":
            copy_widget = self.spinBox
        elif copy_key == "doubleSpinBox":
            copy_widget = self.doubleSpinBox
        elif copy_key == "checkBox":
            copy_widget = self.checkBox
        else:
            raise ValueError(f"Unknown copy style of MyWidgetsFrame: {copy_key}")
        
        widget.setStyleSheet(copy_widget.styleSheet())
        widget.sizePolicy().setHorizontalPolicy(copy_widget.sizePolicy().horizontalPolicy())
        widget.sizePolicy().setVerticalPolicy(copy_widget.sizePolicy().verticalPolicy())

class MyLineEdit(QLineEdit):
    """
    LineEdit that emits a signal when the text changes and ensures that the text is unique within a certain context.

    Attributes
    ----------
    - itemsSignal: A PyQt signal that is emitted when the text changes.
    - tab: A reference to the tab that contains the line edit. If it is None, the signal will not be emitted.
    - recorded_text: The initial text of the line edit.
    - widgets_frame: A reference to the widgets frame from where the style will be copied.
    - copy_style: defines what is the widget from widgets frame from which the style will be copied.

    Methods:
    - __init__(text, copy_style, widgets_frame, read_only, tab): Initializes the instance.
    - focusOutEvent(event): Trims whitespace from the text when the widget loses focus and emits a signal if the text has changed.
    - emitSignal(): Emits a signal with the key of the tab and a list of unique items.
    - makeUnique(): Ensures that the text in the line edit is unique within the context of the table it belongs to.
    - copy(): Creates a copy of the MyLineEdit instance.
    """
    itemsSignal = pyqtSignal(str, list)
    def __init__(self, text="", copy_style=None, widgets_frame:MyWidgetsFrame=None, read_only=False, tab=None):
        super().__init__()
        
        self.tab = tab
        self.recorded_text = text
        self.widgets_frame = widgets_frame
        self.copy_style = copy_style
        self.setText(text)
        self.setReadOnly(read_only)
        self.convertible = copy_style == "convertible"
        self.widgets_frame.copyStyleAndSizePolicy(self, copy_style) if copy_style is not None else None
        self.setMenu()
    
    def setMenu(self):
        pass
        # # create a custom context menu
        # self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.showContextMenu)
        # self.context_menu = QMenu(self)
        
        # if self.convertible:
        #     # add an option to convert widget to a string
        #     self.clear_action = QAction("Set value to convertible string", self)
        #     self.clear_action.triggered.connect(self.clearSelection)
        #     self.context_menu.addAction(self.clear_action)

        # # add an option to add another combobox to the table
        # self.add_rows = QAction("Add Row", self)
        # self.add_rows.triggered.connect(self.addRowToTable)
        # self.context_menu.addAction(self.add_rows)


        # t = self.tab.table

        
    def focusOutEvent(self, event):
        
        self.setText(self.text().strip())
        # if the text is different from the recorded text, set style sheet and emit signal
        if self.recorded_text != self.text(): 
            if self.text() == "None": 
                self.widgets_frame.copyStyleAndSizePolicy(self, "none")
            elif self.text() == NO_DEFAULT:
                self.widgets_frame.copyStyleAndSizePolicy(self, "no_def")
            else: 
                self.widgets_frame.copyStyleAndSizePolicy(self, "value")
            self.emitSignal()
        
        super().focusOutEvent(event)
            
    def emitSignal(self):
        if self.tab is not None and not self.isReadOnly():
            items = self.makeUnique()
            self.itemsSignal.emit(self.tab.key, items)
        
    def makeUnique(self):        
        # check if the text is different from the rest of the table
        self.setText("can't be empty") if self.text() in ["", "\n", " "] else None
        
        t = self.tab.table
        items = [t.cellWidget(row, ID_COL).text() for row in range(t.rowCount()) if t.cellWidget(row, ID_COL) is not None and t.cellWidget(row, ID_COL) != self]
        text = self.text()
        text = getAvailableName(text, items)
        self.setText(text)
        items.append(text)
        items.sort() 
        return items 
        
    def copy(self):
        copy = MyLineEdit(self.text(), self.copy_style, self.widgets_frame, self.isReadOnly(), self.tab)
        return copy
    
class MyEmptyLineEdit(QLineEdit):
    """
    LineEdit that is read only and has no border or background.
    Exists to be used as a placeholder for empty cells in the table.
    """
    def __init__(self):
        super().__init__()
        
        self.setReadOnly(True)
        self.setStyleSheet("background:transparent; border:none;")
    
    def copy(self):
        copy = MyEmptyLineEdit()
        return copy
    
class MyComboBox(QComboBox):
    """
    A custom QComboBox with additional functionality depending on its place:
    
    ComboBox in Main Window Table
    ------------------------------
    If it is on the Main Window Table, it can add rows to the table and remove itself from the table.
    Also, when a Line Edit from Edit Window that contains the IDs of the Run Options Objects emits a signal 
    saying the IDs have changed, it can update its items if the signal key matches the key of the tab:
    (algorithm Ids have changed -> If it has the key=ALGO_KEY, updates the items).
    
    Variant Class ComboBox in Edit Window
    -------------------------------------
    If it is a comboBox from a Variant Class, whenever the current index changes, it can copy the row from 
    the table that matches the current text, so the arguments of the variant matches the ones from the 
    Default Class. 
    
    Operator ComboBox in Edit Window
    ------------------------------
    when a Line Edit from Edit Window that contains the IDs of the operators Objects emits a signal 
    saying the IDs have changed, it can update its items if the signal key matches the key of the tab:
    (operator 'mutation' Ids have changed -> If it has the key=OPERATOR_KEY, updates the items).
    
    Attributes
    ----------
        table: The QTableWidget in which the combobox is located.
        add_rows: A boolean indicating whether the combobox can add rows to the table.
        col: The column in the table where the combobox is located.
        row: The row in the table where the combobox is located.
        tab: The tab in which the combobox is located.
        key: The key used to update the combobox items when a signal is received.
        copy_style: A widget from which to copy the style and size policy.
        widgets_frame: The MyWidgetsFrame in which the combobox is located.
        context_menu: The custom context menu for the combobox.
        clear_action: The action to clear the combobox selection.
        add_rows: The action to add a row to the table.
        remove_combobox_action: The action to remove a row from the table.

    Methods
    -------
        showContextMenu(pos): Shows the custom context menu at the given position.
        addRowToTable(): Adds a new row to the table.
        removeRowFromTable(): Removes a row from the table.
        clearSelection(): Clears the current selection in the combobox.
        copyRowFromClass(): Copies a row from the table that matches the current text of the combobox.
        receiveSignal(key, items): Updates the items in the combobox when a signal with a matching key is received.
        updateItems(items): Updates the items in the combobox.
        copy(): Returns a copy of the combobox.

    Args
    ----
        items (list, optional): The initial items for the combobox. Defaults to an empty list.
        initial_item (str, optional): The initial selected item in the combobox. Defaults to an empty string.
        enabled (bool, optional): Whether the combobox is enabled. Defaults to True.
        table (QTableWidget, optional): The table in which the combobox is located. Defaults to None.
        col (int, optional): The column in the table where the combobox is located. Defaults to 0.
        row (int, optional): The row in the table where the combobox is located. Defaults to None.
        add_rows (bool, optional): Whether the combobox can add rows to the table. Defaults to False.
        tab (optional): The tab in which the combobox is located. Defaults to None.
        key (optional): The key used to update the combobox items when a signal is received. Defaults to None.
        copy_style (optional): A widget from which to copy the style and size policy. Defaults to None.
        widgets_frame (MyWidgetsFrame, optional): The MyWidgetsFrame in which the combobox is located. Defaults to None.
    """
    def __init__(self, items=[], initial_item:str="", enabled: bool=True, table: QTableWidget=None, 
                 col:int=0, row:int=None, add_rows:bool=False, tab=None, key=None, copy_style=None, widgets_frame:MyWidgetsFrame=None):
        super().__init__()

        self.table = table # table in which the combobox is located
        self.add_rows = add_rows
        self.col = col
        self.row = row
        self.tab = tab
        self.key = key
        self.copy_style = copy_style
        self.widgets_frame = widgets_frame
        
        self.setUI(items, initial_item, enabled, row, add_rows, tab, key, copy_style)
        
    def setUI(self, items, initial_item, enabled, row, add_rows, tab, key, copy_style):

        tab.edit_window.operatorUpdates.connect(self.receiveSignal) if key is not None else None
        self.widgets_frame.copyStyleAndSizePolicy(self, copy_style) if copy_style is not None else None  
        self.setInsertPolicy(QComboBox.InsertAlphabetically)        
        self.addItems(items)
        self.setCurrentIndex(self.findText(initial_item))
        self.setEnabled(enabled)

        # create a custom context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.context_menu = QMenu(self)
        self.clear_action = QAction("Clear Selection", self)
        self.clear_action.triggered.connect(self.clearSelection)
        self.context_menu.addAction(self.clear_action)

        if add_rows:
            # add an option to add another combobox to the table
            self.add_rows = QAction("Add Row", self)
            self.add_rows.triggered.connect(self.addRowToTable)
            self.context_menu.addAction(self.add_rows)

            # add an option to remove the combobox from the table
            self.remove_combobox_action = QAction("Remove Row", self)
            self.remove_combobox_action.triggered.connect(self.removeRowFromTable)
            self.context_menu.addAction(self.remove_combobox_action)

        # connect the currentIndexChanged signal to a slot that updates the table
        self.currentIndexChanged.connect(self.copyRowFromClass) if row is not None else None
            
    def showContextMenu(self, pos):
        self.context_menu.exec_(self.mapToGlobal(pos))

    def addRowToTable(self):
        # create a new row  and add it to the table
        row_count = self.table.rowCount()
        items = [self.itemText(i) for i in range(self.count())]
        new_combobox = MyComboBox(items, table=self.table, col=self.col, add_rows=self.add_rows)
        self.table.setRowCount(row_count + 1)
        self.table.setCellWidget(row_count, self.col, new_combobox)

    def removeRowFromTable(self):
        # check if the combobox is the only one in the table, give warning 
        if self.table.rowCount() == 1: 
            MyMessageBox("Cannot remove the only row in the table.")			
        else:
            # remove the combobox from the table
            if self.row is not None:
                self.table.removeRow(self.row)
            else:
                index = self.table.indexAt(self.pos())
                if index.isValid():
                    self.table.removeRow(index.row())

    def clearSelection(self):
        self.setCurrentIndex(-1)
        self.setEditText("")

    def copyRowFromClass(self):

        if self.currentIndex() == -1:
            return

        # get the current text of the combobox
        text = self.currentText()
        
        # find the row of the copy table that matches the current text
        for row_to_copy in range(self.table.rowCount()):
            widget = self.table.cellWidget(row_to_copy, self.col)
            if isinstance(widget, MyLineEdit) and widget.text() == text:
                break
        
        # change id
        new_id = self.table.cellWidget(row_to_copy, ID_COL).text() + VARIANT
        widget = self.table.cellWidget(self.row, ID_COL)
        widget.setText(new_id)
        widget.emitSignal()
        
        # change args
        for col in range(self.col+1, self.table.columnCount()):
            widget = self.table.cellWidget(row_to_copy, col)
            if isinstance(widget, MyComboBox):
                new_widget = widget.copy()
            new_widget = widget.copy() if widget is not None else None
            self.table.setCellWidget(self.row, col, new_widget)
    
    def receiveSignal(self, key, items):
        if key == self.key:
            self.updateItems(items)
                    
    def updateItems(self, items:list):
        # store current text
        curr_text = self.currentText()
        # Clear the current items
        self.clear()
        # Add the new items
        self.addItems(items)
        self.setCurrentIndex(self.findText(curr_text))

    def copy(self):
        items = [self.itemText(i) for i in range(self.count())]
        copy = MyComboBox(items, self.currentText(), self.isEnabled(), self.table, self.col, self.row, self.add_rows, self.tab, self.key, self.copy_style, self.widgets_frame)
        return copy
    
class MyCheckBox(QCheckBox):
    """
    Initializes an instance of the MyCheckBox class.
    When it is checked, it sets the text to "True". When it is unchecked, it sets the text to "False".
    """

    def __init__(self, checked=False, widgets_frame=None, enabled=True):
        super().__init__()

        self.widgets_frame = widgets_frame
        self.widgets_frame.copyStyleAndSizePolicy(self, "checkBox") if widgets_frame is not None else None
        self.setChecked(checked)
        self.setEnabled(enabled)
        
        self.stateChanged.connect(self.updateText)
        self.updateText(self.checkState())

    def copy(self):
        copy = MyCheckBox(self.isChecked(), self.widgets_frame, self.isEnabled())
        return copy
    
    def updateText(self, state):
        if state == Qt.Checked:
            self.setText("True")
        else:
            self.setText("False")
  
class IntValidator(QValidator):
    """
    Validates int inputs for ScientificSpinBox
    """
    @staticmethod
    def valid_integer_string(string: str) -> bool:
        """
        Checks if string makes a valid integer, keeping in mind locale dependent decimal separators.
        """

        exp_count = string.count('e') + string.count('E')
        if exp_count == 1:
            match = exp_int_re.search(string)
        elif exp_count == 0:
            match = valid_int_re.search(string)
        else:
            return False
        return match.groups()[0] == string if match else False

    @staticmethod
    def intermediate_pos_integer_string(string: str) -> bool:
        """
        Checks if string makes a valid partial positive integer, keeping in mind locale dependent decimal separators.
        """

        # Normal notation.
        # Use regex to check if string is part of a valid positive float:
        match = partial_pos_int_re.search(string)
        return match.groups()[0] == string if match else False

    @staticmethod
    def intermediate_float_string(string: str) -> bool:
        """
        Checks if string makes a valid partial float, keeping in mind locale dependent decimal separators.
        """

        # Normal notation.
        # Use regex to check if string is part of a valid positive float:
        match = partial_float_re.search(string)
        return match.groups()[0] == string if match else False

    @staticmethod
    def intermediate_integer_string(string: str) -> bool:
        """
        Checks if string makes a valid partial integer, keeping in mind locale dependent decimal separators.
        """

        # Allow empty strings:
        if string == "":
            return True

        # Allow 0 or 1 combined instances of e and E:
        exp_count = string.count('e') + string.count('E')
        if exp_count > 1:
            return False

        if exp_count == 1:
            # Scientific notation.
            # Split string at exponential symbol and check that both substrings are valid:
            char = 'e' if string.count('e') > 0 else 'E'
            _, __ = string.split(char)
            if IntValidator.intermediate_float_string(_) and IntValidator.intermediate_pos_integer_string(__):
                return True
        else:
            # Normal notation.
            # Use regex to check if string is part of a valid int:
            match = partial_int_re.search(string)
            return match.groups()[0] == string if match else False

        return False

    def validate(self, string: str, position: int) -> QValidator.State:
        """
        Validates input string to see if it is a valid integer or partial integer.

        Notes
        -----
        Position is not used, but required because we are overriding an internal method.
        """

        if self.valid_integer_string(string):
            return QValidator.Acceptable
        if self.intermediate_integer_string(string):
            return QValidator.Intermediate
        else:
            return QValidator.Invalid

    def fixup(self, string: str) -> str:
        """
        Fixes up input text to create a valid integer. Puts an empty string on failure.
        """

        match = exp_int_re.search(string)
        return match.groups()[0] if match else ""


class ScientificSpinBox(QSpinBox):
    """
    Subclass of QSpinBox that is locale independent.
    """
    def __init__(self, widgets_frame:MyWidgetsFrame=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.widgets_frame = widgets_frame
        self.widgets_frame.copyStyleAndSizePolicy(self, "spinBox") if widgets_frame is not None else None
        
        # On 64 bit windows, QSpinBox maximum size is limited to 32 bit, so check for this here:
        self.validator = IntValidator()
        try:
            self.setRange(-int(10e16), int(10e16)) #@IgnoreException
        except OverflowError:
            self.setRange(-int(2 ** 31 - 1), int(2 ** 31 - 1))
        
    def validate(self, string: str, position: int) -> Tuple[QValidator.State, str, int]:
        """
        Returns the validity of the string, using a QValidator object.

        Notes
        -----
        Return type depends on whether PySide or PyQt is being used.
        """

        validity = self.validator.validate(string, position)

        # support 2 different PyQt APIs.
        if hasattr(QtCore, 'QString'):
            return QValidator.State(validity), string, position
        else:
            return validity, string, position

    def fixup(self, string: str) -> str:
        """
        Fixes up strings that are considered intermediate when spinbox focus is lost.
        """

        return self.validator.fixup(string)

    def valueFromText(self, string: str) -> int:
        """
        Turns user viewable string into an int.
        """

        if string == "":
            return self.value()

        string = string.replace(QtCore.QLocale().decimalPoint(), ".", 1)
        # Cannot convert scientific notation strings into ints directly, so convert to float first.
        value = int(float(string))

        if value > self.maximum():
            value = self.maximum()
        if value < self.minimum():
            value = self.minimum()

        return value

    def textFromValue(self, value: int) -> str:
        """
        Turns internal int value into user viewable string.
        """

        string = "{:g}".format(value).replace("e+", "e").replace(".", QtCore.QLocale().decimalPoint(), 1)
        string = re.sub(r"e(-?)0*(\d+)", r"e\1\2", string)
        return string

    def stepBy(self, steps: int):
        """
        Increases or decreases the value of the least significant digit by 'steps'.
        """

        text = self.cleanText()

        match = exp_int_re.search(text)
        if match is None:
            return

        groups = match.groups()

        val, _, _ = groups[1].partition(QtCore.QLocale().decimalPoint())
        significance = len(groups[1])-1
        if groups[1] is not None and len(groups[1]) > 0 and groups[1][0] == '-':
            significance -= 1
        val = float(val) + steps * 10**significance

        new_string = "{:g}".format(val) + (groups[3] if groups[3] else "")
        self.lineEdit().setText(new_string)

    def copy(self):
        copy = ScientificSpinBox(self.widgets_frame)
        copy.setRange(self.minimum(), self.maximum())
        copy.setValue(self.value())
        copy.setSingleStep(self.singleStep())
        copy.setPrefix(self.prefix())
        copy.setSuffix(self.suffix())
        copy.setDisplayIntegerBase(self.displayIntegerBase())
        return copy

class FloatValidator(QValidator):
    """
    Validates float inputs for ScientificDoubleSpinBox
    """
    @staticmethod
    def valid_float_string(string: str) -> bool:
        """
        Checks if string makes a valid float, keeping in mind locale dependent decimal separators.
        """

        match = exp_float_re.search(string)
        return match.groups()[0] == string if match else False

    @staticmethod
    def intermediate_integer_string(string: str) -> bool:
        """
        Checks if string makes a valid partial integer, keeping in mind locale dependent decimal separators.
        """

        match = partial_int_re.search(string)
        return match.groups()[0] == string if match else False

    @staticmethod
    def intermediate_float_string(string: str) -> bool:
        """
        Checks if string makes a valid partial float, keeping in mind locale dependent decimal separators.
        """

        # Allow empty strings:
        if string == "":
            return True

        # Allow 0 or 1 combined instances of e and E:
        exp_count = string.count('e') + string.count('E')
        if exp_count > 1:
            return False

        if exp_count == 1:
            # Scientific notation.
            # Split string at exponential symbol and check that both substrings are valid:
            char = 'e' if string.count('e') > 0 else 'E'
            _, __ = string.split(char)
            if FloatValidator.intermediate_float_string(_) and FloatValidator.intermediate_integer_string(__):
                return True
        else:
            # Normal notation.
            # Use regex to check if string is part of a valid float:
            match = partial_float_re.search(string)
            return match.groups()[0] == string if match else False

        return False

    def validate(self, string: str, position: int) -> QValidator.State:
        """
        Validates input string to see if it is a valid float or partial float.

        Notes
        -----
        State is not used, but required because we are overriding an internal method.
        """

        if self.valid_float_string(string):
            return QValidator.Acceptable
        if self.intermediate_float_string(string):
            return QValidator.Intermediate
        else:
            return QValidator.Invalid

    def fixup(self, string: str) -> str:
        """
        Fixes up input text to create a valid float. Puts an empty string on failure.
        """

        match = exp_float_re.search(string)
        return match.groups()[0] if match else ""


class ScientificDoubleSpinBox(QDoubleSpinBox):
    """
    Subclass of QDoubleSpinBox that allows for scientific notation and is locale independent.
    """
    def __init__(self, widgets_frame:MyWidgetsFrame=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set nice default values:
        self.widgets_frame = widgets_frame
        self.widgets_frame.copyStyleAndSizePolicy(self, "doubleSpinBox") if widgets_frame is not None else None
        self.setMinimum(-inf)
        self.setMaximum(inf)
        self.validator = FloatValidator()
        self.setDecimals(1000)
        
    def validate(self, string: str, position: int) -> Tuple[QValidator.State, str, int]:
        """
        Returns the validity of the string, using a QValidator object.

        Notes
        -----
        Return type depends on whether PySide or PyQt is being used.
        """

        validity = self.validator.validate(string, position)

        # support 2 different PyQt APIs.
        if hasattr(QtCore, 'QString'):
            return validity, str(string), position
        else:
            return validity, string, position

    def fixup(self, string: str) -> str:
        """
        Fixes up strings that are considered intermediate when spinbox focus is lost.
        """

        return self.validator.fixup(string)

    def textFromValue(self, value: float) -> str:
        """
        Turns internal float value into user viewable string.
        """

        string = "{:g}".format(value).replace("e+", "e").replace(".", QtCore.QLocale().decimalPoint(), 1)
        string = re.sub(r"e(-?)0*(\d+)", r"e\1\2", string)
        return string

    def valueFromText(self, string: str) -> float:
        """
        Turns user viewable string into a float.
        """

        if string == "":
            return self.value()

        string = string.replace(QtCore.QLocale().decimalPoint(), ".", 2)
        value = float(string)

        if value > self.maximum():
            value = self.maximum()
        if value < self.minimum():
            value = self.minimum()

        return value

    def stepBy(self, steps: int):
        """
        Increases or decreases the value of the least significant digit by 1.
        """

        text = self.cleanText()

        match = exp_float_re.search(text)
        if match is None:
            return

        groups = match.groups()

        # If we have digits after the decimal indicator:
        if groups[2] is not None:
            significance = len(groups[2])-1
            if len(groups[2]) > 0 and groups[2][0] == '-':
                significance -= 1
            val = float(groups[1]) + steps * 10**(-significance)

        else:
            val, _, _ = groups[1].partition(QtCore.QLocale().decimalPoint())
            significance = len(groups[1])-1
            if groups[1] is not None and len(groups[1]) > 0 and groups[1][0] == '-':
                significance -= 1
            val = float(val) + steps * 10**significance

        new_string = "{:g}".format(val) + (groups[3] if groups[3] else "")
        self.lineEdit().setText(new_string)

    def copy(self):
        copy = ScientificDoubleSpinBox(self.widgets_frame)
        copy.setRange(self.minimum(), self.maximum())
        copy.setValue(self.value())
        copy.setSingleStep(self.singleStep())
        copy.setPrefix(self.prefix())
        copy.setSuffix(self.suffix())
        copy.setDecimals(self.decimals())	        
        return copy
