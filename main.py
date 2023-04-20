
# frontend imports
from frontend.my_ui import MyMainWindow
from PyQt5.QtWidgets import QApplication

# backend imports

def main():
    app = QApplication([])
    main_window = MyMainWindow()
    main_window.show()
    app.exec_()
    
    # tables = Tables()
    # input = Input(tables)
    # run = Run(input)
        
if __name__ == '__main__':
    main()


