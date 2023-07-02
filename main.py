from PyQt5.QtWidgets import QApplication
from frontend.main_window import MyMainWindow

def main():
    from tests.tests_declaration import options_test1, options_test2, options_test3 
    options = options_test3
    
    # start the QApplication
    app = QApplication([])
    main_window = MyMainWindow(options['moo'], options)
    main_window.show()
    app.exec_()
        
        
if __name__ == '__main__':
    main()


