from PyQt5.QtWidgets import QFrame, QTableWidget, QTableWidgetItem, QTabWidget
from PyQt5.uic import loadUi
from backend.run import RunThread
from utils.defines import DESIGNER_RUN_TAB, DESIGNER_RESULT_FRAME, PROB_KEY, ALGO_KEY, N_SEEDS_KEY, PI_KEY, N_GEN_KEY, N_EVAL_KEY
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QFileDialog

from frontend.my_widgets import MyMessageBox

class ResultFrame(QFrame):
    def __init__(self, tabWidget: QTabWidget, run_thread: RunThread, run_name: str):
        super().__init__()
        loadUi(DESIGNER_RESULT_FRAME, self)
        
        self.run_name = run_name
        self.label.setText(run_name)
        self.tabWidget = tabWidget
                
        # cancel button
        self.cancel_button.clicked.connect(self.cancel_run)

        # make the run in a separate thread (has to be called in another class) 
        self.run_thread = run_thread                
        self.run_thread.progressSignal.connect(self.receiveUpdate)
        self.run_thread.finished.connect(self.afterRun)
        self.run_thread.start()

    def afterRun(self):
        """After the run is finished, add the tab to the run window and show it"""
        if self.run_thread.canceled:
            return
        
        self.tab = RunTab(self.run_thread, self.run_name)
        self.progressBar.setValue(100)
        self.progress_label.setText("")
        self.save_run.setEnabled(True)
        self.save_run.clicked.connect(self.tab.saveRun)
        self.save_data.setEnabled(True)
        self.save_data.clicked.connect(self.tab.saveData)
        self.openTab_button.setEnabled(True)
        self.openTab_button.clicked.connect(self.openTab)
        self.openTab()

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
        index = self.tabWidget.addTab(self.tab, self.run_name)
        self.tabWidget.setCurrentIndex(index)
    
    def receiveUpdate(self, label: str, value: int):
        """Update the progress bar and label with the current run"""
        if value == -1:
            MyMessageBox(label)
            self.erase()
        else:
            self.progressBar.setValue(value)
            self.progress_label.setText(label)
                
    def erase(self):
        """Erase the run"""
        self.tabWidget.results_layout.removeWidget(self)
        # remove tab if it exists
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i) == self.run_name:
                self.tabWidget.removeTab(i)
                break
        self.deleteLater()     
    
    def cancel_run(self):
        """Cancel the run"""
        self.run_thread.cancel()
        self.erase()
        
class RunTab(QFrame):
    def __init__(self, run_thread: RunThread, label: str):
        super().__init__()
        loadUi(DESIGNER_RUN_TAB, self)
        
        # connections
        self.save_data.clicked.connect(self.saveData)
        self.save_run.clicked.connect(self.saveRun)
        self.voting_by.currentIndexChanged.connect(self.changedVoting)
        self.selected.currentIndexChanged.connect(self.changeTable)
        self.table.horizontalHeader().sectionDoubleClicked.connect(lambda col: self.horizontalHeaderClick(col))
        self.table.verticalHeader().sectionDoubleClicked.connect(lambda row: self.VerticalHeaderClick(row))
        
        # set the label                         
        self.label.setText(label)
        seed_str = "seed" if run_thread.n_seeds == 1 else "seeds"
        self.n_seeds_label.setText(f"{run_thread.n_seeds} {seed_str}")
        
        # get the class variables
        self.run_thread = run_thread        
        self.pi_ids = run_thread.single_run_args_list[0].pi_ids
        
        # get the average, across seeds, of the pi on the final generation
        avg_data = run_thread.data.groupby([PROB_KEY, ALGO_KEY, N_SEEDS_KEY]).last()
        self.avg_data = avg_data.groupby([PROB_KEY, ALGO_KEY]).mean().reset_index()
        # get column by name
        self.prob_ids = list(self.avg_data[PROB_KEY].unique())
        
        # set the table
        self.changedVoting()
        
    def changedVoting(self):
        """Change the table widget to display the results for the selected performance indicator"""
        
        if self.voting_by.currentText() == "Performance Indicator":
            selected_items = self.pi_ids
            self.double_click_label.setText("<b>Double click</b> on a <b>Problem</b> to plot the Algorithms on the Indicator through the generations")
        elif self.voting_by.currentText() == "Problem":
            selected_items = self.prob_ids
            self.double_click_label.setText("<b>Double click</b> on an <b>Algorithm</b> to plot the Indicators on the Problem through the generations")
        else:
            raise ValueError("Voting by can only be Performance Indicator or Problem")
        
        self.selected.currentIndexChanged.disconnect(self.changeTable)
        self.selected.clear()
        self.selected.currentIndexChanged.connect(self.changeTable)
        self.selected.addItems(selected_items)    
        if self.selected.currentIndex() != 0:
            self.selected.setCurrentIndex(0)
        else:
            self.selected.setCurrentIndex(0)
            self.changeTable()
    
    def changeTable(self):
        # get the selected item id and the corresponding dataframe
        selected_id = self.selected.currentText()
        if self.voting_by.currentText() == "Performance Indicator":
            df = self.avg_data.pivot(index=ALGO_KEY, columns=PROB_KEY, values=selected_id)
        elif self.voting_by.currentText() == "Problem":
            df = self.avg_data[self.avg_data[PROB_KEY] == selected_id]
            df.drop(columns=[N_GEN_KEY, N_EVAL_KEY, PROB_KEY], inplace=True)
            df = df.set_index(df.columns[0])
            
        else:
            raise ValueError("Voting by can only be Performance Indicator or Problem")
    
        # add the voting column 
        df['voting'] = df.idxmax(axis=0).value_counts()
        df['voting'] = df['voting'].fillna(0).astype(int)

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
                # set voting column                
                if j == len(df.columns)-1:
                    item = QTableWidgetItem(str(df.iloc[i, -1]))
                # set value columns
                else:
                    nice_string = "{:.3e}".format(df.iloc[i, j]) 
                    item = QTableWidgetItem(nice_string)
                    # set text to bold if it is the biggest value in the column
                    if df.iloc[i, j] == df.iloc[:, j].max():
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                self.table.setItem(i, j, item)

    def horizontalHeaderClick(self, col):
        """Handle a click on a horizontal header item"""
        item = self.table.horizontalHeaderItem(col)
        if item is not None:
            print(f"Header {col} clicked, content: {item.text()}") #!
        text = item.text()
        if self.voting_by.currentText() == "Performance Indicator":
            pi_id = self.selected.currentText()
            self.plotAlgos(text, pi_id)
        
    def VerticalHeaderClick(self, row):
        """Handle a click on a vertical header cell"""
        item = self.table.verticalHeaderItem(row)
        if item is not None:
            print(f"Header {row} clicked, content: {item.text()}") #!
        text = item.text()
        if self.voting_by.currentText() == "Problem":
            prob_id = self.selected.currentText()
            self.plotIndicators(text, prob_id)

    def plotAlgos(self, prob_id: str, pi_id: str):
        """Plot the results of the optimization for a given problem and performance indicator"""

        # get the data for the given problem
        df = self.run_thread.data[self.run_thread.data[PROB_KEY] == prob_id]

        # get df with columns: algorithm_id, seed, n_eval, n_gen, pi_id
        df = df[[ALGO_KEY, N_SEEDS_KEY, N_EVAL_KEY, N_GEN_KEY, pi_id]]

        # average across seeds
        df = df.groupby([ALGO_KEY, N_EVAL_KEY, N_GEN_KEY]).mean()

        # plot by algorithm, with n_eval on the x axis and pi_id on the y axis using matplotlib 
        plt.figure()
        plt.title(f"Problem: {prob_id}, Performance Indicator: {pi_id}")
        for algo_id in df.index.levels[0]:
            df_algo = df.loc[algo_id]
            plt.plot(df_algo.index.get_level_values(N_EVAL_KEY), df_algo[pi_id], label=algo_id)

        plt.xlabel(N_EVAL_KEY)
        plt.ylabel(pi_id)
        plt.legend()
        plt.show()

    def plotIndicators(self, algo_id: str, prob_id: str):
        df = self.run_thread.data
        df = df[(df[ALGO_KEY] == algo_id) & (df[PROB_KEY] == prob_id)]
        df = df[[N_EVAL_KEY] + self.pi_ids]

        # Plot the performance indicators
        plt.figure()
        plt.title(f'Problem: {prob_id}, Algorithm: {algo_id}')
        for pi_id in self.pi_ids:
            plt.plot(df[N_EVAL_KEY], df[pi_id], label=pi_id)
        
        plt.xlabel(N_EVAL_KEY)
        plt.legend()
        plt.show()
        
    def saveData(self):
        """Save the results of the run"""
        options = QFileDialog.Options()
        defaultName = f"{self.run_name}.csv"
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", defaultName, "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.run_thread.data.to_csv(fileName, index=False)    
    
    def saveRun(self):
        """Save the run""" #!
        print("save run to be implemented")