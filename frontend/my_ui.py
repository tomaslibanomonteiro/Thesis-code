from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QHeaderView

import inspect

class MyComboBox(QComboBox):
    def __init__(self, items = [], initial_index=-1, initial_text="", enabled = True):
        super().__init__()
        
        for item in items:
            self.addItem(item)
        self.setCurrentIndex(initial_index)
        self.setEnabled(enabled) # TODO: this is not working
        self.setEditText(initial_text)

class EditWindow(QDialog):
    def __init__(self, window_title="Edit", label="Edit", table=None):
        super().__init__()
        loadUi('frontend/designer_edit_window.ui', self)
        # set window title
        self.setWindowTitle(window_title)
        # set big label
        self.label.setText(label)
        
        # set table data
        
        
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        loadUi('frontend/designer_main.ui', self)
        self.edit_windows = []
        
        tables_list = [self.tableWidget_run_pi, self.tableWidget_run_algo, self.tableWidget_run_prob]
        items_list = [["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"]]
        self.setTablesToComboBoxes(tables_list, items_list)
                
        buttons = [self.pushButton_edit_pi, self.pushButton_edit_algo, self.pushButton_edit_prob, self.pushButton_edit_term]
        labels = ["Edit Performance Indicators", "Edit Algorithms", "Edit Problems", "Edit Terminations"]
        default_tables = self.get_default_tables()         
        self.setEditWindows(buttons, labels, default_tables)
        
    def get_default_tables(self):
        # TODO: get default tables from classes
        default_tables = []
        default_tables.append([["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"]])
        default_tables.append([["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"]])
        default_tables.append([["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"]])
        default_tables.append([["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"]])
        return default_tables
                
    def setEditWindows(self, buttons, labels, tables):
        for button, label, table in zip(buttons, labels, tables):
            window = EditWindow(window_title=label, label=label, table=table)
            self.edit_windows.append(window)
            button.clicked.connect(window.show)
            
    def setTablesToComboBoxes(self, tableWidget_list, comboBox_items_list):
        for table, items in zip(tableWidget_list, comboBox_items_list):
            # strech the table to fit the window
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row in range(table.rowCount()):
                initial_text = table.item(row, 0).text() if table.item(row, 0) else ""
                enabled = True if row == 0 else False
                combobox = MyComboBox(items, initial_text=initial_text, enabled=enabled)
                table.setCellWidget(row, 0, combobox)
                if row < table.rowCount() - 1:
                    combobox.currentIndexChanged.connect(lambda i, table=table, row=row+1: self.enableTableComboBox(table, row, 0))

    def enableTableComboBox(self, table, row, col, enabled=True):
        if row < table.rowCount() and col < table.columnCount():
            table.cellWidget(row, col).setEnabled(enabled)
                    
    
def main():
    app = QApplication([])
    main_window = MyMainWindow()
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()    