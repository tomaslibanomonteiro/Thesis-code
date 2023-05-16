from PyQt5.QtWidgets import QApplication, QDoubleSpinBox, QVBoxLayout, QWidget

app = QApplication([])
window = QWidget()

layout = QVBoxLayout()
spin_box = QDoubleSpinBox()
spin_box.setDecimals(-2)
spin_box.setValue(1.23e-45)
layout.addWidget(spin_box)
window.setLayout(layout)

window.show()
app.exec_()