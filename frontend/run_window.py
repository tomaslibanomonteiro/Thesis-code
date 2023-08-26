from PyQt5.QtCore import QThread, QThreadPool
from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem
from PyQt5.uic import loadUi
from backend.run import Run
from utils.defines import (DESIGNER_RUN_WINDOW, DEBUG_MODE)
from matplotlib import pyplot as plt

class MyThread(QThread):
    def __init__(self, run_obj: Run):
        super().__init__()
        self.run_obj = run_obj 
        
    def run(self):
        if DEBUG_MODE:
            import pydevd
            pydevd.settrace(suspend=False)
        self.run_obj.run()
      
class RunWindow(QDialog):
    def __init__(self, run: Run, window_title: str, ui_file=DESIGNER_RUN_WINDOW, save_path=None):
        super().__init__()
        loadUi(ui_file, self)

        self.setWindowTitle(window_title)
        self.label.setText(window_title)
        self.run = run 
        self.save_path = save_path
        
        # make the run in a separate thread (has to be called in another class)
        self.my_thread = MyThread(self.run)
        self.my_thread.finished.connect(self.afterRun)
                
    def startRun(self):
        self.my_thread.start()
         
    def afterRun(self):                
        # update the combo box with the performance indicators
        pi_ids = [key for key in self.run.dfs_dict.keys()]
        self.comboBox_pi.addItems(pi_ids)
        self.comboBox_pi.currentIndexChanged.connect(self.changeTable)
        self.comboBox_pi.setCurrentIndex(0)
        
        # update table widget and show the window
        self.changeTable()
        self.show()
                                 
    def changeTable(self):
        """Change the table widget to display the results for the selected performance indicator"""
        
        # get the performance indicator id and the corresponding dataframe
        pi_id = self.comboBox_pi.currentText()
        df = self.run.dfs_dict[pi_id]
        
        # update the table widget
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers) # make table non-editable
        self.tableWidget.setColumnCount(len(df.columns))
        self.tableWidget.setRowCount(len(df.index))
        
        # set the horizontal headers
        self.tableWidget.horizontalHeader().sectionDoubleClicked.connect(lambda col: self.horizontalHeaderClick(col))
        for j in range(len(df.columns)):
            header_item = QTableWidgetItem(df.columns[j])
            self.tableWidget.setHorizontalHeaderItem(j, header_item)

        # set the rest of the table    
        self.tableWidget.verticalHeader().sectionDoubleClicked.connect(lambda row: self.VerticalHeaderClick(row))
        for i in range(len(df.index)):
            self.tableWidget.setVerticalHeaderItem(i, QTableWidgetItem(df.index[i]))
            # get the float into str representation, last column is voting (int)
            for j in range(len(df.columns)):                
                if j == len(df.columns)-1:
                    item = QTableWidgetItem(str(df.iloc[i, -1]))
                else:
                    nice_string = "{:.3e}".format(df.iloc[i, j]) 
                    item = QTableWidgetItem(nice_string)
                self.tableWidget.setItem(i, j, item)

    def horizontalHeaderClick(self, col):
        """Handle a click on a horizontal header item"""
        item = self.tableWidget.horizontalHeaderItem(col)
        if item is not None:
            print(f"Header {col} clicked, content: {item.text()}")
        text = item.text()
        pi_id = self.comboBox_pi.currentText()
        self.plot_prob(text, pi_id)
            
    def VerticalHeaderClick(self, row):
        """Handle a click on a vertical header cell"""
        item = self.tableWidget.verticalHeaderItem(row)
        if item is not None:
            print(f"Header {row} clicked, content: {item.text()}")

    def plot_prob(self, prob_id: str, pi_id: str):
        """Plot the results of the optimization for a given problem and performance indicator"""

        df = self.run.data[self.run.data['problem_id'] == prob_id]

        # get df with columns: algorithm_id, seed, n_eval, n_gen, pi_id
        df = df[['algorithm_id', 'seed', 'n_eval', 'n_gen', pi_id]]

        # average across seeds
        df = df.groupby(['algorithm_id', 'n_eval', 'n_gen']).mean()

        # plot by algorithm, with n_eval on the x axis and pi_id on the y axis using matplotlib
        for var in ['n_gen', 'n_eval']:
            plt.figure()
            for algo_id in df.index.levels[0]:
                df_algo = df.loc[algo_id]
                plt.plot(df_algo.index.get_level_values(var), df_algo[pi_id], label=algo_id)

            plt.legend()
            plt.xlabel(var)
            plt.ylabel(pi_id)
            plt.show()