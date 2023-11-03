from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QRadioButton, QLabel

class SingleObjectiveWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.single_objective_label = QLabel("Single Objective Page")
        layout.addWidget(self.single_objective_label)
        self.setLayout(layout)

class MultiObjectiveWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.multi_objective_label = QLabel("Multi-Objective Page")
        layout.addWidget(self.multi_objective_label)
        self.setLayout(layout)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimization App")
        self.setGeometry(100, 100, 400, 300)

        self.stacked_widget = QStackedWidget()
        self.single_objective_widget = SingleObjectiveWidget()
        self.multi_objective_widget = MultiObjectiveWidget()
        self.stacked_widget.addWidget(self.single_objective_widget)
        self.stacked_widget.addWidget(self.multi_objective_widget)

        self.radio_single_objective = QRadioButton("Single Objective")
        self.radio_multi_objective = QRadioButton("Multi-Objective")
        self.radio_single_objective.toggled.connect(self.show_single_objective_page)
        self.radio_multi_objective.toggled.connect(self.show_multi_objective_page)

        layout = QVBoxLayout()
        layout.addWidget(self.radio_single_objective)
        layout.addWidget(self.radio_multi_objective)
        layout.addWidget(self.stacked_widget)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_single_objective_page(self, checked):
        if checked:
            self.stacked_widget.setCurrentIndex(0)

    def show_multi_objective_page(self, checked):
        if checked:
            self.stacked_widget.setCurrentIndex(1)

if __name__ == '__main__':
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()
