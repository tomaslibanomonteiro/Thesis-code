import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.uic import loadUi

class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("C:/Users/tomas/OneDrive - Universidade de Lisboa/Desktop/Tese/Thesis-code/frontend/designer_templates/test.ui", self)
        self.pushButton_ref_dirs.clicked.connect(self.show_warning)
        self.pushButton_sampling.clicked.connect(self.show_warning)
        self.pushButton_crossover.clicked.connect(self.show_warning)
        self.pushButton_selection.clicked.connect(self.show_warning)
        self.pushButton_decomposition.clicked.connect(self.show_warning)

    def show_warning(self):
        sender = self.sender()
        message = f"You pressed the {sender.text()} button"
        QMessageBox.warning(self, "Warning", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = MyDialog()
    dialog.show()
    sys.exit(app.exec_())