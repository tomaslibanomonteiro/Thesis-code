from PyQt5.QtWidgets import QFrame, QTableWidget, QTableWidgetItem, QTabWidget
from PyQt5.uic import loadUi
from backend.run import Run
from utils.defines import DESIGNER_RUN_FRAME, DESIGNER_RESULTS_FRAME
from matplotlib import pyplot as plt
from PyQt5.QtCore import QThread

class MyThread(QThread):
    def __init__(self, run_obj: Run):
        super().__init__()
        self.run_obj = run_obj     

    def run(self):
        import pydevd
        pydevd.settrace(suspend=False)
        self.run_obj.run()            

class ResultFrame(QFrame):
    def __init__(self, run: Run, run_name: str, tabWidget: QTabWidget):
        super().__init__()
        loadUi(DESIGNER_RESULTS_FRAME, self)
        
        self.run = run
        self.run_name = run_name
        self.tabWidget = tabWidget
        # make the run in a separate thread (has to be called in another class)
        self.my_thread = MyThread(run)
        self.my_thread.finished.connect(self.afterRun)
        self.my_thread.start()
                
    def afterRun(self):
        """After the run is finished, add tabs to the run window and show it"""
        self.tabWidget.addTab(RunFrame(self.run, self.run_name), self.run_name)
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)

      
class RunFrame(QFrame):
    def __init__(self, run: Run, label: str):
        super().__init__()
        loadUi(DESIGNER_RUN_FRAME, self)
        
        self.label.setText(label)
        self.run = run 
                 
        # update the combo box with the performance indicators
        pi_ids = [key for key in self.run.dfs_dict.keys()]
        self.pi.addItems(pi_ids)
        self.pi.currentIndexChanged.connect(self.changeTable)
        self.pi.setCurrentIndex(0)
        
        # things to set only once
        self.table.horizontalHeader().sectionDoubleClicked.connect(lambda col: self.horizontalHeaderClick(col))
        self.table.verticalHeader().sectionDoubleClicked.connect(lambda row: self.VerticalHeaderClick(row))
        
        # update table widget and show the window
        self.changeTable()
        self.show()
                                 
    def changeTable(self):
        """Change the table widget to display the results for the selected performance indicator"""
        
        # get the performance indicator id and the corresponding dataframe
        pi_id = self.pi.currentText()
        df = self.run.dfs_dict[pi_id]
        
        # update the table widget
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # make table non-editable
        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df.index))
        
        # set the horizontal headers
        for j in range(len(df.columns)):
            header_item = QTableWidgetItem(df.columns[j])
            self.table.setHorizontalHeaderItem(j, header_item)

        # set the rest of the table    
        for i in range(len(df.index)):
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(df.index[i]))
            # get the float into str representation, last column is voting (int)
            for j in range(len(df.columns)):                
                if j == len(df.columns)-1:
                    item = QTableWidgetItem(str(df.iloc[i, -1]))
                else:
                    nice_string = "{:.3e}".format(df.iloc[i, j]) 
                    item = QTableWidgetItem(nice_string)
                self.table.setItem(i, j, item)

    def horizontalHeaderClick(self, col):
        """Handle a click on a horizontal header item"""
        item = self.table.horizontalHeaderItem(col)
        if item is not None:
            print(f"Header {col} clicked, content: {item.text()}")
        text = item.text()
        pi_id = self.pi.currentText()
        self.plot_prob(text, pi_id)
            
    def VerticalHeaderClick(self, row):
        """Handle a click on a vertical header cell"""
        item = self.table.verticalHeaderItem(row)
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