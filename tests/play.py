import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
import pydevd
class MyThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        # do some work here 
        pydevd.settrace(suspend=False)
        print('hello')
        print('hello 2')
        for i in range(10):
            print(i)
            self.sleep(1) # add sleep method to enable stopping at breakpoints
        self.finished_signal.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.thread = MyThread()
        self.thread.finished_signal.connect(self.on_thread_finished)
        self.thread.start()

    def on_thread_finished(self):
        # do something when the thread finishes
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())