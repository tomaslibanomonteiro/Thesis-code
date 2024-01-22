from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create QTextEdit and set its style
        self.textEdit = QTextEdit(self)
        self.textEdit.setStyleSheet("border: 0; border-right: 20px solid darkblue;")
        
        # Create a layout and add the QTextEdit to it
        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)

        # Create a central widget, set the layout on it, and set it as the central widget
        centralWidget = QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # Set a fixed size for the central widget
        centralWidget.setFixedSize(500, 500)  # Adjust the size as needed
        a= None

def main():
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec_()

if __name__ == "__main__":
    main()