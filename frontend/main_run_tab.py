from PyQt5.QtWidgets import QFrame, QTableWidget, QTableWidgetItem, QCheckBox, QFileDialog, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from utils.defines import DESIGNER_RUN_TAB, PROB_KEY, ALGO_KEY, N_SEEDS_KEY, N_GEN_KEY, N_EVAL_KEY, VOTING_KEY, PI_KEY, CLASS_KEY, TERM_KEY, RUN_ID_KEY
from backend.run import RunThread
from frontend.my_widgets import MyMessageBox
from backend.run import RunThread
from pymoo.visualization.scatter import Scatter

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class PlotDialog(QWidget):

    def __init__(self, run_data, prob_id:str, algo_ids:list, pi_ids:list, title:str='Plot'):
        super().__init__()

        sc = MplCanvas(width=5, height=4, dpi=100)
        self.plotProgress(sc, run_data, prob_id, algo_ids, pi_ids)

        # Create toolbar, passing canvas as first parament, parent (self, the CustomDialog) as second.
        toolbar = NavigationToolbar2QT(sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.show()

    def plotProgress(self, sc:MplCanvas, run_data, prob_id:str, algo_ids:list, pi_ids:list):
        """Plot the progress of the checked algorithms for the given problem and checked performance indicators"""
        # get the data for the given problem
        df_prob = run_data[run_data[PROB_KEY] == prob_id]
        
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
                sc.axes.plot(mean.index, mean.values, label=f"{algo_id}/{pi_id}")
                sc.axes.fill_between(mean.index, (mean-std).values, (mean+std).values, alpha=0.2)
                
        # name the plot
        sc.axes.set_title(f'Progress on problem: {prob_id}')
        # add labels
        sc.axes.set_xlabel('Number of evaluations')
        sc.axes.set_ylabel('Performance Indicator')
        # add legend
        sc.axes.legend()
        
class RunTab(QFrame):
    def __init__(self, run_thread: RunThread, label: str):
        super().__init__()
        loadUi(DESIGNER_RUN_TAB, self)
                
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
        self.algo_ids = list(self.term_data[ALGO_KEY].unique())
        
        # store the plot dialogs so they are not garbage collected
        self.plot_dialogs = []
        
        self.setUI(label)
        
    def setUI(self, label):
        
        # connections
        self.save_data.clicked.connect(self.saveData)
        self.save_run.clicked.connect(self.saveRun)
        self.values_comboBox.currentIndexChanged.connect(self.changedChosenValue)
        self.selected_id.currentIndexChanged.connect(self.changeTable)
        self.table.horizontalHeader().sectionDoubleClicked.connect(lambda col: self.headerClick(col, "horizontal"))
        self.table.verticalHeader().sectionDoubleClicked.connect(lambda row: self.headerClick(row, "vertical"))
        self.plot_button.clicked.connect(self.plot)
        self.plot_comboBox.currentIndexChanged.connect(self.setCheckBoxes)
        self.plot_prob.addItems(self.prob_ids)

        # set the labels                         
        self.label.setText(label)
        seed_str = "seed" if self.run_thread.n_seeds == 1 else "seeds"
        self.n_seeds_label.setText(f"Averaged on: <b>{self.run_thread.n_seeds} {seed_str}</b>")
        self.n_seeds_label.setAlignment(Qt.AlignCenter)
        self.term_label.setText(f"Termination criteria: <b>{self.run_thread.term_id}</b> <br><font size='2'>(Double click to see parameters)</font>")
        self.term_label.setAlignment(Qt.AlignCenter)
        self.term_label.mouseDoubleClickEvent = self.seeTermination

        # set the table
        self.changedChosenValue()
        self.setCheckBoxes(set_algos=True)

    def setCheckBoxes(self, event=None, set_algos=False):
        """set the checkboxes for the given ids in the tables"""

        if set_algos:
            # put the algorithm checkboxes in self.algo_table
            self.algo_table.setRowCount(len(self.algo_ids))
            self.algo_table.clear()
            for i, algo_id in enumerate(self.algo_ids):
                checkbox = QCheckBox(algo_id)
                self.algo_table.setCellWidget(i, 0, checkbox)
                checkbox.setChecked(i == 0)

        # set the name of the second page of the toolbox
        if self.plot_comboBox.currentText() == "Pareto Front":
            ids = list(range(self.run_thread.n_seeds))
            self.toolBox.setItemText(1, "Seeds")
        elif self.plot_comboBox.currentText() == "Progress":
            ids = self.pi_ids
            self.toolBox.setItemText(1, "Performance Indicators")

        # put the ids checkboxes in self.page2_table
        self.page2_table.setRowCount(len(ids))
        self.page2_table.clear()
        for i, id in enumerate(ids):
            checkbox = QCheckBox(str(id))
            self.page2_table.setCellWidget(i, 0, checkbox)
            checkbox.setChecked(i == 0)
        
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
            df = self.term_data[self.term_data[PROB_KEY] == selected_id].copy()
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
        if item is None or item.text() == VOTING_KEY:
            return
        
        id = item.text()
        args = self.run_thread.parameters[key][id].copy()
        clazz = args.pop(CLASS_KEY)
        string = f"Parameters for {key} of class {clazz} with id \'{id}\': \n {args}"
        MyMessageBox(string, 'Parameters', warning_icon=False)
            
    def plot(self):
        """Plot the results"""
        prob_id = self.plot_prob.currentText()
        
        algo_ids = [self.algo_table.cellWidget(i, 0).text() for i in range(self.algo_table.rowCount()) 
                    if self.algo_table.cellWidget(i, 0).isChecked()]
        
        other_ids = [self.page2_table.cellWidget(i, 0).text() for i in range(self.page2_table.rowCount()) 
                    if self.page2_table.cellWidget(i, 0).isChecked()]        
        if len(algo_ids) == 0:
            MyMessageBox("Select at least one algorithm to plot")
        elif self.plot_comboBox.currentText() == "Pareto Front":
            if len(algo_ids) > 1:
                MyMessageBox("Select only one algorithm to plot the Pareto Front")
            else:
                self.plotParetoFront(prob_id, algo_ids[0], other_ids)
        elif self.plot_comboBox.currentText() == "Progress":
            if len(other_ids) == 0:
                MyMessageBox("Select at least one performance indicator to plot the progress")
            else:
                self.plot_dialogs.append(PlotDialog(self.run_thread.data, prob_id, algo_ids, other_ids))
        else:        
            raise ValueError("Plot by can only be Performance Indicator or Problem")
    
    def plotParetoFront(self, prob_id:str, algo_id:str, seeds:list):
        print("plot pareto front to be implemented") #!
                
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