from PyQt5.QtWidgets import QFrame, QTableWidget, QTableWidgetItem, QTabWidget
from PyQt5.uic import loadUi
from backend.run import RunThread
from utils.defines import DESIGNER_RUN_FRAME, DESIGNER_RESULT_FRAME
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QFileDialog

class ResultFrame(QFrame):
    def __init__(self, run_thread: RunThread, run_name: str, tabWidget: QTabWidget):
        super().__init__()
        loadUi(DESIGNER_RESULT_FRAME, self)
        
        self.run_name = run_name
        self.label.setText(run_name)
        self.tabWidget = tabWidget
                
        # buttons
        self.openTab_button.clicked.connect(self.openTab)
        self.saveResults_button.clicked.connect(self.saveResults)
        # self.reproduceRun_button.clicked.connect(self.reproduce_run)
        self.cancel_button.clicked.connect(self.cancel_run)

        # make the run in a separate thread (has to be called in another class) 
        self.run_thread = run_thread                
        self.run_thread.progressSignal.connect(self.receiveUpdate)
        self.run_thread.start()
        self.run_thread.finished.connect(self.afterRun)

    def afterRun(self):
            """After the run is finished, add the tab to the run window and show it"""
            index = self.tabWidget.addTab(RunTab(self.run_thread, self.run_name), self.run_name)
            self.tabWidget.setCurrentIndex(index)
            self.progressBar.setValue(100)
            self.progress_label.setText("")
            self.openTab_button.setEnabled(True)
            self.saveResults_button.setEnabled(True)
            
            # change the erase button to cancel button
            self.cancel_button.setText("Erase")
            self.cancel_button.clicked.connect(self.erase)
            
    def closeTab(self, index):
        """Close the tab at the given index"""
        self.tabWidget.removeTab(index)       

    def openTab(self):
        """Check if any of the tabs has the same name as the run, if not, call afterRun"""
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == self.run_name:
                self.tabWidget.setCurrentIndex(i)
                return
        self.afterRun()
    
    def receiveUpdate(self, label: str, value: int):
        """Update the progress bar and label with the current run"""
        self.progressBar.setValue(value)
        self.progress_label.setText(label)
             
    def saveResults(self):
        """Save the results of the run"""
        options = QFileDialog.Options()
        defaultName = f"{self.run_name}.csv"
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", defaultName, "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.run_thread.data.to_csv(fileName, index=False)    
        
    def erase(self):
        """Erase the run"""
        self.tabWidget.results_layout.removeWidget(self)
        self.deleteLater()     
    
    def cancel_run(self):
        """Cancel the run"""
        self.run_thread.cancel()
        self.erase()
        
class RunTab(QFrame):
    def __init__(self, run_thread: RunThread, label: str):
        super().__init__()
        loadUi(DESIGNER_RUN_FRAME, self)
        
        self.label.setText(label)
        self.run_thread = run_thread
        
        # update the combo box with the performance indicators
        pi_ids = [key for key in self.run_thread.dfs_dict.keys()]
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
        df = self.run_thread.dfs_dict[pi_id]
        
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

        df = self.run_thread.data[self.run_thread.data['problem_id'] == prob_id]

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
            