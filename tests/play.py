import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QSizePolicy

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create a central widget and set it as the central widget of the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout
        layout = QVBoxLayout(central_widget)

        # Create widgets to add to the layout
        button1 = QPushButton("Button 1")
        button2 = QPushButton("Button 2")

        # Set the size policy for the widgets to expand horizontally and vertically
        button1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add widgets to the layout
        layout.addWidget(button1)
        layout.addWidget(button2)

        # Set the layout for the central widget
        central_widget.setLayout(layout)

        # Set the main window properties
        self.setWindowTitle("Automatic Stretch Layout Example")
        self.setGeometry(100, 100, 400, 300)

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
