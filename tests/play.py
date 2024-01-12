from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QDoubleSpinBox, QSpinBox, QLineEdit
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Assuming this is your dictionary
        self.params_dict = {
            'algorithm1': {
                'param1': 1.23,
                'param2': 4,
                'param3': 'hello'
            },
            'algorithm2': {
                'param1': 2.34,
                'param2': 5,
                'param3': 'world'
            }
        }

        # Create the table view and model
        self.table = QTableView(self)
        self.setCentralWidget(self.table)
        self.model = QStandardItemModel()
        self.table.setModel(self.model)

        # Set the headers
        self.model.setHorizontalHeaderLabels(max(self.params_dict.values(), key=len).keys())
        self.model.setVerticalHeaderLabels(self.params_dict.keys())

        # Populate the model
        for row, (algorithm_id, parameters) in enumerate(self.params_dict.items()):
            for column, (parameter_name, parameter_value) in enumerate(parameters.items()):
                item = QStandardItem()
                self.model.setItem(row, column, item)

                if isinstance(parameter_value, float):
                    widget = QDoubleSpinBox()
                    widget.setValue(parameter_value)
                elif isinstance(parameter_value, int):
                    widget = QSpinBox()
                    widget.setValue(parameter_value)
                elif isinstance(parameter_value, str):
                    widget = QLineEdit()
                    widget.setText(parameter_value)
                else:
                    widget = QLineEdit()
                    widget.setText(str(parameter_value))

                self.table.setIndexWidget(item.index(), widget)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
    