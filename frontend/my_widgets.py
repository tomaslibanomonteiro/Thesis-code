import re
from typing import Tuple

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidget, QComboBox, QMessageBox, QCheckBox, QSpinBox, QDoubleSpinBox, QTextEdit, QMenu, QAction
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QValidator

from utils.defines import ID_COL, VARIANT

class MyMessageBox(QMessageBox):
    def __init__(self, text, title="Warning", warning_icon=True, execute = True):
        super().__init__()

        self.setIcon(QMessageBox.Warning) if warning_icon else None
        self.setText(text)
        self.setWindowTitle(title)
        self.setStandardButtons(QMessageBox.Ok)
        self.exec_() if execute else None

class MyTextEdit(QTextEdit):
    itemsSignal = pyqtSignal(str, list)
    def __init__(self, text="", tab=None, read_only=False):
        super().__init__()

        self.setText(text)
        self.setReadOnly(read_only)
        self.tab = tab
        self.recorded_text = text
        
    def text(self):
        return self.toPlainText()

    def focusOutEvent(self, event):
        # emit a signal to update the comboboxes
        self.setText(self.text().strip())
        if self.recorded_text != self.text():
            self.recorded_text = self.text()
            self.emitSignal()
        super().focusOutEvent(event)
        
    def emitSignal(self):
        if self.tab is not None and not self.isReadOnly():
            items = self.makeUnique()
            self.itemsSignal.emit(self.tab.key, items)
        
    def makeUnique(self):        
        # check if the text is different from the rest of the table
        self.setText("can't be empty") if self.text() in ["", "\n", " "] else None
        
        table = self.tab.table
        count = 2
        while count > 1:
            items = [table.cellWidget(row, ID_COL).text() if table.cellWidget(row, ID_COL) is not None else None for row in range(table.rowCount())]
            count = items.count(self.text())
            if count > 1:
                self.setText(self.text() + "_1")
        
        items = [item for item in items if item is not None]
        items.sort() 
        return items 
        
    def copy(self):
        copy = MyTextEdit(self.text(), self.tab, self.isReadOnly())
        copy.setStyleSheet(self.styleSheet())
        return copy
    
class MyComboBox(QComboBox):
    def __init__(self, items=[], initial_index: int=-1, enabled: bool=True, table: QTableWidget=None, 
                 col:int=0, row:int=None, add_rows:bool=False, tab=None, key=None):
        super().__init__()

        self.table = table # table in which the combobox is located
        self.add_rows = add_rows
        self.col = col
        self.row = row
        self.tab = tab
        self.key = key
        tab.edit_window.operatorUpdates.connect(self.receiveSignal) if key is not None else None
        
        self.addItems(items)
        self.setCurrentIndex(initial_index) 
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
            if isinstance(widget, MyTextEdit) and widget.text() == text:
                break
        
        # change id
        new_id = self.table.cellWidget(row_to_copy, ID_COL).text() + VARIANT
        widget = self.table.cellWidget(self.row, ID_COL)
        widget.setText(new_id)
        widget.emitSignal()
        
        # change args
        for col in range(self.col+1, self.table.columnCount()):
            widget = self.table.cellWidget(row_to_copy, col)
            # if it is a combobox, print the comboBox options
            if isinstance(widget, MyComboBox):
                new_widget = widget.copy()
            new_widget = widget.copy() if widget is not None else None
            self.table.setCellWidget(self.row, col, new_widget)
    
    def receiveSignal(self, key, items):
        if key == self.key:
            self.updateItems(items)
                    
    def updateItems(self, items:list):
        # store current text
        current_text = self.currentText()
        # Clear the current items
        self.clear()
        # Add the new items
        self.addItems(items)
        # check if the current text is in the new items
        if current_text in items:
            self.setCurrentText(current_text)
        else:
            self.setCurrentIndex(-1)

    def copy(self):
        items = [self.itemText(i) for i in range(self.count())]
        copy = MyComboBox(items, self.currentIndex(), self.isEnabled(), self.table, self.col, self.row, self.add_rows, self.tab, self.key)
        copy.setStyleSheet(self.styleSheet())
        return copy
    
"""
This code has been adapted from: https://gist.github.com/jdreaver/0be2e44981159d0854f5
Changes made are support for PyQt5, localisation, better intermediate state detection and better stepping.
Some inspiration taken from: https://github.com/pyqtgraph/pyqtgraph/blob/develop/pyqtgraph/widgets/SpinBox.py
"""

decimal_point = re.escape(QtCore.QLocale().decimalPoint())
int_exp_regex = r'(([+-]?\d+(' + decimal_point + r'\d*)?|' + decimal_point + r'\d+)([eE][+]?\d+)?)'
exp_int_re = re.compile(int_exp_regex)
partial_int_re = re.compile(r'([+-]?(\d?))')
valid_int_re = re.compile(r'([+-]?\d*)')
partial_pos_int_regex = re.compile(r'([+]?(\d?))')
partial_pos_int_re = re.compile(partial_pos_int_regex)
partial_float_regex = r'([+-]?((\d*' + decimal_point + r'?))?\d*)'
partial_float_re = re.compile(partial_float_regex)

class MyCheckBox(QCheckBox):
    def __init__(self, checked=False, enabled=True):
        super().__init__()

        self.setChecked(checked)
        self.setEnabled(enabled)
    
    def copy(self):
        copy = MyCheckBox(self.isChecked(), self.isEnabled())
        copy.setStyleSheet(self.styleSheet())
        return copy
  
class IntValidator(QValidator):
    """
    Validates integer inputs for ScientificSpinBox
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
    Subclass of QSpinBox that allows for scientific notation and is locale independent.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # On 64 bit windows, QSpinBox maximum size is limited to 32 bit, so check for this here:
        self.validator = IntValidator()
        try:
            self.setRange(-int(10e16), int(10e16)) #@IgnoreException
        except OverflowError:
            self.setRange(-int(2 ** 31 - 1), int(2 ** 31 - 1))

    from typing import Tuple

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
        copy = ScientificSpinBox()
        copy.setRange(self.minimum(), self.maximum())
        copy.setValue(self.value())
        copy.setSingleStep(self.singleStep())
        copy.setPrefix(self.prefix())
        copy.setSuffix(self.suffix())
        copy.setDisplayIntegerBase(self.displayIntegerBase())
        copy.setStyleSheet(self.styleSheet())
        return copy

from numpy import inf

"""
This code has been adapted from: https://gist.github.com/jdreaver/0be2e44981159d0854f5
Changes made are support for PyQt5, localisation, better intermediate state detection and better stepping.
Some inspiration taken from: https://github.com/pyqtgraph/pyqtgraph/blob/develop/pyqtgraph/widgets/SpinBox.py
"""

decimal_point = re.escape(QtCore.QLocale().decimalPoint())
exp_regex = r'(([+-]?\d+(' + decimal_point + r'\d*)?|' + decimal_point + r'\d+)([eE][+-]?\d+)?)'
exp_float_re = re.compile(exp_regex)
partial_int_re = re.compile(r'([+-]?(\d?))')
partial_float_regex = r'([+-]?((\d*' + decimal_point + r'?))?\d*)'
partial_float_re = re.compile(partial_float_regex)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set nice default values:
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
        copy = ScientificDoubleSpinBox()
        copy.setRange(self.minimum(), self.maximum())
        copy.setValue(self.value())
        copy.setSingleStep(self.singleStep())
        copy.setPrefix(self.prefix())
        copy.setSuffix(self.suffix())
        copy.setDecimals(self.decimals())	
        copy.setStyleSheet(self.styleSheet())
  
        return copy
