from OptionsTableWidget import OptionsTableWidget

import sys
from PyQt5.QtWidgets import QApplication, QWidget

# Create the QApplication object
app = QApplication(sys.argv)

# Create your QWidget object(s)
widget = OptionsTableWidget()

widget.setupUi(widget)

# Show the widget
widget.show()

# Start the event loop
sys.exit(app.exec_())