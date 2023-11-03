import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QLabel

class TabCopyExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab Copy Example")
        self.setGeometry(100, 100, 400, 300)
        
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.add_tab_button = QPushButton("Add New Tab", self)
        self.add_tab_button.clicked.connect(self.add_new_tab)
        
        self.tab_widget.addTab(self.create_initial_tab(), "Tab 1")
        self.tab_widget.addTab(self.create_initial_tab(), "Tab 2")
        self.tab_widget.addTab(self.create_initial_tab(), "Tab 3")
        
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        layout = QVBoxLayout()
        layout.addWidget(self.add_tab_button)
        layout.addWidget(self.tab_widget)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def create_initial_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        label = QLabel("This is a tab content.")
        layout.addWidget(label)
        tab.setLayout(layout)
        return tab
    
    def add_new_tab(self):
        # Create a new tab
        new_tab = QWidget()
        new_tab_layout = QVBoxLayout()
        
        # Copy the content of the active tab to the new tab
        active_tab_index = self.tab_widget.currentIndex()
        active_tab = self.tab_widget.widget(active_tab_index)
        for widget in active_tab.findChildren(QWidget):
            widget_copy = widget.clone() if hasattr(widget, 'clone') else widget  # You may need to implement a custom clone method for your custom widgets
            new_tab_layout.addWidget(widget_copy)
        
        # Add the new tab to the tab widget
        self.tab_widget.addTab(new_tab, f"Tab {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentWidget(new_tab)
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
    
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TabCopyExample()
    window.show()
    sys.exit(app.exec_())
