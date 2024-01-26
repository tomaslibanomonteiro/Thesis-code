from PyQt5.QtWidgets import QFrame, QTableWidget, QTableWidgetItem, QTabWidget, QCheckBox
from PyQt5.uic import loadUi
from backend.run import RunThread
from utils.defines import DESIGNER_RUN_TAB, DESIGNER_RESULT_FRAME, PROB_KEY, ALGO_KEY, N_SEEDS_KEY, PI_KEY, N_GEN_KEY, N_EVAL_KEY
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
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
        self.values_comboBox.currentIndexChanged.connect(self.changedChosenValue)
        self.selected_id.currentIndexChanged.connect(self.changeTable)
        self.table.horizontalHeader().sectionDoubleClicked.connect(lambda col: self.horizontalHeaderClick(col))
        self.table.verticalHeader().sectionDoubleClicked.connect(lambda row: self.VerticalHeaderClick(row))
        self.plot_button.clicked.connect(self.plot)
        
        # set the label                         
        self.label.setText(label)
        seed_str = "seed" if run_thread.n_seeds == 1 else "seeds"
        self.n_seeds_label.setText(f"Averaged on: <b>{run_thread.n_seeds} {seed_str}</b>")
        self.n_seeds_label.setAlignment(Qt.AlignCenter)
        self.term_label.setText(f"Termination criteria: <b>{run_thread.term_id}</b> <br>(Double click to see parameters)")
        self.term_label.setAlignment(Qt.AlignCenter)
        self.term_label.mouseDoubleClickEvent = self.seeTermination
        
        # get the class variables
        self.run_thread = run_thread        
        self.pi_ids = run_thread.single_run_args_list[0].pi_ids
        
        # get the average, across seeds, of the pi on the final generation
        avg_data = run_thread.data.groupby([PROB_KEY, ALGO_KEY, N_SEEDS_KEY]).last()
        self.avg_data = avg_data.groupby([PROB_KEY, ALGO_KEY]).mean().reset_index()
        # get column by name
        self.prob_ids = list(self.avg_data[PROB_KEY].unique())
        self.plot_prob.addItems(self.prob_ids)
        self.algo_ids = list(self.avg_data[ALGO_KEY].unique())
        # set the table
        self.changedChosenValue()
        self.setCheckBoxes()
            
    def setCheckBoxes(self):
        """set the checkboxes for the given ids in the layout """
        
        # put the algorithm checkboxs in self.algo_layout
        for i, algo_id in enumerate(self.algo_ids):
            checkbox = QCheckBox(algo_id)
            if i % 2 == 0:
                self.algo_layout.addWidget(checkbox, i // 2, 0)  # Add to col1
            else:
                self.algo_layout.addWidget(checkbox, i // 2, 1)  # Add to col2
                
        # put the performance indicator checkboxs in self.pi_layout 
        for i, pi_id in enumerate(self.pi_ids):
            checkbox = QCheckBox(pi_id)
            if i % 2 == 0:
                self.pi_layout.addWidget(checkbox, i // 2, 0)  # Add to col1
            else:
                self.pi_layout.addWidget(checkbox, i // 2, 1)  # Add to col2
        
        # set the first checkbox in each layout to checked
        self.algo_layout.itemAt(0).widget().setChecked(True)
        self.pi_layout.itemAt(0).widget().setChecked(True)
        
    def changedChosenValue(self):
        """Change the table widget to display the results for the selected performance indicator"""
                
        if self.values_comboBox.currentText() == "Performance Indicator":
            selected_items = self.pi_ids
        elif self.values_comboBox.currentText() == "Problem":
            selected_items = self.prob_ids
        else:
            raise ValueError("Voting by can only be Performance Indicator or Problem")
        
        self.selected_id.currentIndexChanged.disconnect(self.changeTable)
        self.selected_id.clear()
        self.selected_id.currentIndexChanged.connect(self.changeTable)
        self.selected_id.addItems(selected_items)    
        if self.selected_id.currentIndex() != 0:
            self.selected_id.setCurrentIndex(0)
        else:
            self.selected_id.setCurrentIndex(0)
            self.changeTable()
    
    def changeTable(self):
        # get the selected item id and the corresponding dataframe
        selected_id = self.selected_id.currentText()
        if self.values_comboBox.currentText() == "Performance Indicator":
            df = self.avg_data.pivot(index=ALGO_KEY, columns=PROB_KEY, values=selected_id)
        elif self.values_comboBox.currentText() == "Problem":
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
        
    def VerticalHeaderClick(self, row):
        """Handle a click on a vertical header cell"""
        item = self.table.verticalHeaderItem(row)
        if item is not None:
            print(f"Header {row} clicked, content: {item.text()}") #!
        text = item.text()

    def plot(self):
        """Plot the results"""
        prob_id = self.plot_prob.currentText()
        algo_ids = [self.algo_layout.itemAt(i).widget().text() for i in range(self.algo_layout.count()) if self.algo_layout.itemAt(i).widget().isChecked()]
        pi_ids = [self.pi_layout.itemAt(i).widget().text() for i in range(self.pi_layout.count()) if self.pi_layout.itemAt(i).widget().isChecked()]
        
        if len(algo_ids) == 0:
            MyMessageBox("Select at least one algorithm to plot")
        elif self.plot_comboBox.currentText() == "Pareto Front":
            if len(algo_ids) > 1:
                MyMessageBox("Select only one algorithm to plot the Pareto Front")
            else:
                algo_id = algo_ids[0]
                self.plotParetoFront(prob_id, algo_id)
        elif self.plot_comboBox.currentText() == "Progress":
            self.plotProgress(prob_id, algo_ids, pi_ids)
        else:        
            raise ValueError("Plot by can only be Performance Indicator or Problem")
    
    def plotParetoFront(self, prob_id:str, algo_id:str):
        print("plot pareto front to be implemented") #!
        
    def plotProgress(self, prob_id:str, algo_ids:list, pi_ids:list):
        """Plot the progress of the checked algorithms for the given problem and checked performance indicators"""
        # get the data for the given problem
        df_prob = self.run_thread.data[self.run_thread.data[PROB_KEY] == prob_id]
        
        # get the data for the given algorithms
        for algo_id in algo_ids:
            df_algo = df_prob[df_prob[ALGO_KEY] == algo_id]
            for pi_id in pi_ids:
                # get the data for the given performance indicator
                df_pi = df_algo[[N_EVAL_KEY, pi_id]]
                # plot the data
                plt.plot(df_pi[N_EVAL_KEY], df_pi[pi_id], label=f"{algo_id}/{pi_id}")    
        # name the plot
        plt.title(f'Progress on {prob_id}')
        # add labels
        plt.xlabel('Number of evaluations')
        plt.ylabel('Performance Indicator')
        # add legend
        plt.legend()
        # show the plot
        plt.show()
        
    def saveData(self):
        """Save the results of the run"""
        options = QFileDialog.Options()
        defaultName = f"{self.run_name}.csv"
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", defaultName, "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.run_thread.data.to_csv(fileName, index=False)    
    
    def seeTermination(self, event):
        """See the termination criteria"""
        print("see termination to be implemented") #!
    
    def saveRun(self):
        """Save the run""" #!
        print("save run to be implemented")