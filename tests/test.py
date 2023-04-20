from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox
from PyQt5.uic import loadUi


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('test.ui', self)
        
        

def main():
    app = QApplication([])
    window = QMainWindow()
    app.exec_()

if __name__ == '__main__':
    main()    