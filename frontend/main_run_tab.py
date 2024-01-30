from PyQt5.QtWidgets import QFrame, QTableWidget, QTableWidgetItem, QCheckBox, QFileDialog
from PyQt5.uic import loadUi
from matplotlib import pyplot as plt
from PyQt5.QtCore import Qt
import numpy as np

from utils.defines import DESIGNER_RUN_TAB, PROB_KEY, ALGO_KEY, N_SEEDS_KEY, N_GEN_KEY, N_EVAL_KEY, VOTING_KEY, PI_KEY, CLASS_KEY, TERM_KEY, RUN_ID_KEY
from backend.run import RunThread
from frontend.my_widgets import MyMessageBox
from backend.run import RunThread

class RunTab(QFrame):
    def __init__(self, run_thread: RunThread, label: str):
        super().__init__()
        loadUi(DESIGNER_RUN_TAB, self)
        
        # connections
        self.save_data.clicked.connect(self.saveData)
        self.save_run.clicked.connect(self.saveRun)
        self.values_comboBox.currentIndexChanged.connect(self.changedChosenValue)
        self.selected_id.currentIndexChanged.connect(self.changeTable)
        self.table.horizontalHeader().sectionDoubleClicked.connect(lambda col: self.headerClick(col, "horizontal"))
        self.table.verticalHeader().sectionDoubleClicked.connect(lambda row: self.headerClick(row, "vertical"))
        self.plot_button.clicked.connect(self.plot)
        self.plot_comboBox.currentIndexChanged.connect(self.setCheckBoxes)
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
        self.pi_ids = run_thread.run_args_list[0].pi_ids
        
        # get the average, across seeds, of the pi on the final generation
        term_data = run_thread.data.groupby([PROB_KEY, ALGO_KEY, N_SEEDS_KEY]).last()
        self.term_data = term_data.groupby([PROB_KEY, ALGO_KEY]).mean().reset_index()
        
        # go through the pi columns, and if they do not exist, create them and fill them with NaN
        for pi_id in self.pi_ids:
            if pi_id not in self.term_data.columns:
                self.term_data[pi_id] = np.nan
                
        # get column by name
        self.prob_ids = list(self.term_data[PROB_KEY].unique())
        self.plot_prob.addItems(self.prob_ids)
        self.algo_ids = list(self.term_data[ALGO_KEY].unique())
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
        
        if self.plot_comboBox.currentText() == "Pareto Front":
            ids = list(range(self.run_thread.n_seeds))
            self.toolBox.setItemText(1, "Seeds")
        elif self.plot_comboBox.currentText() == "Progress":
            ids = self.pi_ids
            self.toolBox.setItemText(1, "Performance Indicators")

        # remove current checkboxes
        while self.page2_layout.count():
            item = self.page2_layout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()
        # put the ids checkboxs in self.page2_layout 
        for i, id in enumerate(ids):
            checkbox = QCheckBox(str(id))
            if i % 2 == 0:
                self.page2_layout.addWidget(checkbox, i // 2, 0)  # Add to col1
            else:
                self.page2_layout.addWidget(checkbox, i // 2, 1)  # Add to col2
        
        # set the first checkbox in each layout to checked
        self.algo_layout.itemAt(0).widget().setChecked(True)
        self.page2_layout.itemAt(0).widget().setChecked(True)
        
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
            df = self.term_data.pivot(index=ALGO_KEY, columns=PROB_KEY, values=selected_id)
        elif self.values_comboBox.currentText() == "Problem":
            df = self.term_data[self.term_data[PROB_KEY] == selected_id]
            df.drop(columns=[N_GEN_KEY, N_EVAL_KEY, PROB_KEY, RUN_ID_KEY], inplace=True)
            df = df.set_index(df.columns[0])
        else:
            raise ValueError("Voting by can only be Performance Indicator or Problem")
    
        # add the voting column. if the row has only NaN, the voting is 0
        df[VOTING_KEY] = df.idxmin(axis=0).value_counts()
        df[VOTING_KEY] = df[VOTING_KEY].fillna(0).astype(int)

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
                    # set text to bold if it is the smallest value in the column
                    if df.iloc[i, j] == df.iloc[:, j].min():
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                self.table.setItem(i, j, item)

    def headerClick(self, x:int, orientation:str):
        """Handle a click on a header item"""
        
        if orientation == "horizontal":
            item = self.table.horizontalHeaderItem(x)
            key = PROB_KEY if self.values_comboBox.currentText() == "Performance Indicator" else PI_KEY
        else:
            item = self.table.verticalHeaderItem(x)
            key = ALGO_KEY
        if item is None or item.text() == "voting":
            return
        
        id = item.text()
        args = self.run_thread.parameters[key][id].copy()
        clazz = args.pop(CLASS_KEY)
        string = f"Parameters for {key} of class {clazz} with id \'{id}\': \n {args}"
        MyMessageBox(string, 'Parameters', warning_icon=False)
        
    def plot(self):
        """Plot the results"""
        prob_id = self.plot_prob.currentText()
        algo_ids = [self.algo_layout.itemAt(i).widget().text() for i in range(self.algo_layout.count()) if self.algo_layout.itemAt(i).widget().isChecked()]
        other_ids = [self.page2_layout.itemAt(i).widget().text() for i in range(self.page2_layout.count()) if self.page2_layout.itemAt(i).widget().isChecked()]
        
        if len(algo_ids) == 0:
            MyMessageBox("Select at least one algorithm to plot")
        elif self.plot_comboBox.currentText() == "Pareto Front":
            if len(algo_ids) > 1:
                MyMessageBox("Select only one algorithm to plot the Pareto Front")
            else:
                algo_id = algo_ids[0]
                self.plotParetoFront(prob_id, algo_id, other_ids)
        elif self.plot_comboBox.currentText() == "Progress":
            if len(other_ids) == 0:
                MyMessageBox("Select at least one performance indicator to plot the progress")
            else:
                self.plotProgress(prob_id, algo_ids, other_ids)
        else:        
            raise ValueError("Plot by can only be Performance Indicator or Problem")
    
    def plotParetoFront(self, prob_id:str, algo_id:str, seeds:list):
        print("plot pareto front to be implemented") #!
        
    def plotProgress(self, prob_id:str, algo_ids:list, pi_ids:list):
        """Plot the progress of the checked algorithms for the given problem and checked performance indicators"""
        # get the data for the given problem
        df_prob = self.run_thread.data[self.run_thread.data[PROB_KEY] == prob_id]
        
        plt.close()
        plt.figure()
        # get the data for the given algorithms
        for algo_id in algo_ids:
            df_algo = df_prob[df_prob[ALGO_KEY] == algo_id]
            for pi_id in pi_ids:
                # get the data for the given performance indicator
                df_pi = df_algo[[N_EVAL_KEY, pi_id]]
                df_pi = df_pi.dropna(subset=[pi_id])  # Filter rows where pi_id has nan value
                
                # calculate mean and standard deviation
                mean = df_pi.groupby(N_EVAL_KEY)[pi_id].mean()
                std = df_pi.groupby(N_EVAL_KEY)[pi_id].std()

                # plot the data
                plt.plot(mean.index, mean.values, label=f"{algo_id}/{pi_id}")
                plt.fill_between(mean.index, (mean-std).values, (mean+std).values, alpha=0.2)
                
        # name the plot
        plt.title(f'Progress on prob: {prob_id}')
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
        defaultName = f"change_this.csv" #!
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", defaultName, "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            self.run_thread.data.to_csv(fileName, index=False)    
    
    def seeTermination(self, event):
        """See the termination criteria"""
        id = self.run_thread.term_id
        args = self.run_thread.parameters[TERM_KEY][id].copy()
        clazz = args.pop(CLASS_KEY)
        string = f"Parameters for {TERM_KEY} of class {clazz} with id \'{id}\': \n {args}"
        MyMessageBox(string, 'Parameters', warning_icon=False)
    
    def saveRun(self):
        """Save the run""" #!
        print("save run to be implemented")