from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt

app = QApplication([])

window = QWidget()

# Create the layout
layout = QVBoxLayout()
window.setLayout(layout)

# Create the frames
frame1 = QFrame()
frame1.setFrameShape(QFrame.StyledPanel)
frame2 = QFrame()
frame2.setFrameShape(QFrame.StyledPanel)

# Add the frames to the layout
layout.addWidget(frame1)
layout.addWidget(frame2)

# Align the frames at the top of the layout
layout.setAlignment(Qt.AlignTop)

window.show()

app.exec_()