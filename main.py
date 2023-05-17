from frontend.main_window import MyMainWindow
from PyQt5.QtWidgets import QApplication
from utils.get_defaults import Defaults

def main():
    
    # create the application
    app = QApplication([])
    
    # get the default values for algo prob and term in the pymoo framework
    defaults = Defaults()
    
    # start the main window of the application
    main_window = MyMainWindow(defaults)
    main_window.show()
    app.exec_()
        
if __name__ == '__main__':
    main()


