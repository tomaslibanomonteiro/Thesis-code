from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QHeaderView

class MyComboBox(QComboBox):
    def __init__(self, items = [], initial_index=-1, initial_text="", enabled = True):
        super().__init__()
        
        for item in items:
            self.addItem(item)
        self.setCurrentIndex(initial_index)
        self.setEnabled(enabled)
        self.setEditText(initial_text)
                        
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        loadUi('frontend/designer_main.ui', self)
        
        tableWidget_list = [self.tableWidget_run_pi, self.tableWidget_run_algo, self.tableWidget_run_prob]
        comboBox_items_list = [["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"], ["Item 1", "Item 2", "Item 3"]]

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