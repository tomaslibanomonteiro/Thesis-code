from PyQt5.QtWidgets import QFrame, QTableWidget, QTableWidgetItem, QCheckBox, QFileDialog, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from utils.defines import (DESIGNER_RUN_TAB, PROB_KEY, ALGO_KEY, N_SEEDS_KEY, N_GEN_KEY, N_EVAL_KEY, VOTING_KEY, PI_KEY,
                           CLASS_KEY, TERM_KEY, PLOT_PROGRESS_KEY, PLOT_PS_KEY, PLOT_PC_KEY, PLOT_FL_KEY)
from backend.run import RunThread
from frontend.my_widgets import MyMessageBox
from backend.run import RunThread
from pymoo.visualization.scatter import Scatter, Plot
from pymoo.visualization.pcp import PCP
from pymoo.visualization.fitness_landscape import FitnessLandscape

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, width=5, height=4, dpi=100, fig=None, axes=None):
        fig = Figure(figsize=(width, height), dpi=dpi) if fig is None else fig
        self.axes = fig.add_subplot(111) if axes is None else axes
        super(MplCanvas, self).__init__(fig)
    
class Plotter(QWidget):

    def __init__(self, plot_mode, prob_id:str, prob_object, run_thread:RunThread, algo_ids:list, other_ids:list):
        super().__init__()
        
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.sc = None
        self.run_thread = run_thread
        self.prob_id = prob_id
        self.prob_object = prob_object
        self.algo_ids = algo_ids
        self.other_ids = other_ids

        if len(algo_ids) == 0:
            MyMessageBox("Select at least one Algorithm to plot")
            return
        elif len(other_ids) == 0 and plot_mode != PLOT_FL_KEY:
            MyMessageBox("Select at least one Seed/Problem to plot")
            return
        elif plot_mode == PLOT_PROGRESS_KEY:
            self.plotProgress()
        elif plot_mode == PLOT_PS_KEY:
            self.plotParetoSets()
        elif plot_mode == PLOT_PC_KEY:
            self.plotPCP()
        elif plot_mode == PLOT_FL_KEY:
            self.plotFitnessLandscape()
        else:        
            raise ValueError(f"Plot mode can only be {PLOT_PROGRESS_KEY}, {PLOT_PC_KEY}, {PLOT_PS_KEY} or {PLOT_FL_KEY}") 

        if self.sc is None:
            return
        # Create toolbar, passing canvas as first parament, parent (self, the CustomDialog) as second.
        toolbar = NavigationToolbar2QT(self.sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        self.setLayout(layout)
        self.setWindowTitle(f'Ploting Mode: {plot_mode}')
        self.show()

    def plotProgress(self):
        """Plot the progress of the checked algorithms for the given problem and checked performance indicators"""
        # get the data for the given problem
        
        self.sc = MplCanvas()
        
        data = self.run_thread.data.copy()
        df_prob = data[data[PROB_KEY] == self.prob_id]
        
        # get the data for the given algorithms
        for algo_id in self.algo_ids:
            df_algo = df_prob[df_prob[ALGO_KEY] == algo_id]
            for pi_id in self.other_ids:
                # get the data for the given performance indicator
                df_pi = df_algo[[N_EVAL_KEY, pi_id]]
                df_pi = df_pi.dropna(subset=[pi_id])  # Filter rows where pi_id has nan value
                
                # calculate mean and standard deviation
                mean = df_pi.groupby(N_EVAL_KEY)[pi_id].mean()
                std = df_pi.groupby(N_EVAL_KEY)[pi_id].std()

                # plot the data
                self.sc.axes.plot(mean.index, mean.values, label=f"{algo_id}/{pi_id}")
                self.sc.axes.fill_between(mean.index, (mean-std).values, (mean+std).values, alpha=0.2)
                
        # name the plot
        self.sc.axes.set_title(f'Progress on problem: {self.prob_id}')
        # add labels
        self.sc.axes.set_xlabel('Number of evaluations')
        self.sc.axes.set_ylabel('Performance Indicator')
        # add legend
        self.sc.axes.legend()

    def plotPCP(self):
        """Plot the Parallel Coordinates of the checked algorithms for the given problem and checked seeds"""
            
        plot = PCP()
        
        # see if other ids contain 'Problem', if so, get it out of the list
        if 'Problem' in self.other_ids:
            pareto_front = self.prob_object.pareto_front()
            if pareto_front is None:
                MyMessageBox(f"Problem '{self.prob_id}' does not have a Pareto Front available")
            else:
                plot.add(pareto_front, label = self.prob_id)
            self.other_ids.remove('Problem')
            
        self.plotSolutions(plot)        
        self.sc.axes.set_title(f"Paralel Coordinates on Problem: {self.prob_id}", y=1.05)

    def plotParetoSets(self):
        """Plot the Pareto front of the checked algorithms for the given problem and checked seeds"""
            
        plot = Scatter(title=f"Scatter Plot on Problem: {self.prob_id}")
    
        # see if other ids contain 'Problem', if so, get it out of the list
        if 'Problem' in self.other_ids:
            if self.prob_object.pareto_front() is None:
                MyMessageBox(f"Problem '{self.prob_id}' does not have a Pareto Front available")
            else:
                plot.add(self.prob_object.pareto_front(), label = self.prob_id)
            self.other_ids.remove('Problem')
            
        self.plotSolutions(plot)
        
    def plotFitnessLandscape(self):
        """Plot the fitness landscape of the checked algorithms for the given problem and checked seeds"""
        
        plot = MyFitnessLandscape(self.prob_object, title=f"Fitness Landscape on Problem: {self.prob_id}")
        self.plotSolutions(plot)
            
    def plotSolutions(self, plot:Plot, **kwargs):
        
        plot.legend = True
        self.other_ids = [int(id) for id in self.other_ids]
        data = self.run_thread.data.copy()
        filtered_data = data[(data[PROB_KEY] == self.prob_id) & data[ALGO_KEY].isin(self.algo_ids) & data[N_SEEDS_KEY].isin(self.other_ids)]
        filtered_data = filtered_data[[PROB_KEY, ALGO_KEY, N_SEEDS_KEY]].drop_duplicates()
        
        for prob_id, algo_id, n_seeds in filtered_data.values:
            # get the best solution for each run_id
            best_gen = self.run_thread.best_gen[(prob_id, algo_id, n_seeds)]
            # plot the best solution
            plot.add(best_gen, label = f"Algo: '{algo_id}'/Seed: {n_seeds}", **kwargs)
        
        plot.do()
        handles, labels = plot.ax.get_legend_handles_labels()
        # Using dict to remove duplicates, preserving the order
        by_label = dict(zip(labels, handles))
        plot.ax.legend(by_label.values(), by_label.keys())
        
        self.sc = MplCanvas(fig = plot.fig, axes=plot.ax)   
    
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
        self.plot_widgets = []
        
        self.setUI(label)
        
    def setUI(self, label):
        
        # connections
        self.save_data.clicked.connect(self.saveData)
        self.save_run.clicked.connect(self.saveRun)
        self.values_comboBox.currentIndexChanged.connect(self.changedChosenValue)
        self.table.horizontalHeader().sectionDoubleClicked.connect(lambda col: self.headerClick(col, "horizontal"))
        self.table.verticalHeader().sectionDoubleClicked.connect(lambda row: self.headerClick(row, "vertical"))
        self.plot_button.clicked.connect(self.plot)
        self.selected_id.currentIndexChanged.connect(self.changeTable)
        items = [PLOT_PROGRESS_KEY, PLOT_PS_KEY, PLOT_PC_KEY] if self.run_thread.moo else [PLOT_FL_KEY, PLOT_PROGRESS_KEY]
        self.plot_comboBox.addItems(items)
        self.plot_comboBox.currentIndexChanged.connect(self.setCheckBoxes)
        self.plot_prob.addItems(self.prob_ids)
        self.plot_comboBox.lineEdit().setAlignment(Qt.AlignCenter)
        self.plot_comboBox.lineEdit().setReadOnly(True)
        self.values_comboBox.lineEdit().setAlignment(Qt.AlignCenter)
        self.values_comboBox.lineEdit().setReadOnly(True)
        self.selected_id.lineEdit().setAlignment(Qt.AlignCenter)
        self.selected_id.lineEdit().setReadOnly(True)
        self.plot_prob.lineEdit().setAlignment(Qt.AlignCenter)
        self.plot_prob.lineEdit().setReadOnly(True)

        # set the labels                         
        self.label.setText(label)
        seed_str = "seed" if self.run_thread.n_seeds == 1 else "seeds"
        self.n_seeds_label.setText(f"Averaged on: <b>{self.run_thread.n_seeds} {seed_str}</b>")
        self.n_seeds_label.setAlignment(Qt.AlignCenter)
        self.term_label.setText(f"Termination criteria: <b>{self.run_thread.term_id}</b> <br>(Double click to see parameters)</font>")
        self.term_label.setAlignment(Qt.AlignCenter)
        self.term_label.mouseDoubleClickEvent = self.seeTermination

        # set the table
        self.changedChosenValue()
        self.setCheckBoxes(set_algos=True)

    def setCheckBoxes(self, event=None, set_algos=False):
        """set the checkboxes for the given ids in the tables"""


        if self.plot_comboBox.currentText() != PLOT_PROGRESS_KEY:
            ids = [seed for seed in self.run_thread.data[N_SEEDS_KEY].unique()]
            header = "Seed"
            if self.plot_comboBox.currentText() in [PLOT_PS_KEY, PLOT_PC_KEY]:
                ids = ["Problem"] + ids
                header = "Prob/Seed" 
            self.checkBox_table.setHorizontalHeaderItem(1, QTableWidgetItem(header))
        else:
            ids = self.pi_ids
            self.checkBox_table.setHorizontalHeaderItem(1, QTableWidgetItem("Perf. Ind."))

        # put the ids checkboxes in self.checkBox_table second column
        row_count = max(len(self.algo_ids), len(ids))
        self.checkBox_table.setRowCount(row_count)
        # clear column 2
        [self.checkBox_table.setCellWidget(i, 1, None) for i in range(row_count)]
        for i, id in enumerate(ids):
            checkbox = QCheckBox(str(id))
            self.checkBox_table.setCellWidget(i, 1, checkbox)
            checkbox.setChecked(i == 0)
        
        if set_algos:
            for i, algo_id in enumerate(self.algo_ids):
                checkbox = QCheckBox(algo_id)
                self.checkBox_table.setCellWidget(i, 0, checkbox)
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
            df.drop(columns=[N_GEN_KEY, N_EVAL_KEY, PROB_KEY], inplace=True)
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
        prob_object = None
        for run_args in self.run_thread.run_args_list:
            if run_args.prob_id == prob_id:
                prob_object = run_args.prob_object
                break
        if prob_object == None:
            raise ValueError(f'Prob Object not found with id {prob_id}')
        
        table = self.checkBox_table
        algo_ids = [table.cellWidget(i, 0).text() for i in range(len(self.algo_ids)) 
                    if table.cellWidget(i, 0).isChecked()]
        
        other_ids = [table.cellWidget(i, 1).text() for i in range(table.rowCount()) 
                    if table.cellWidget(i, 1) is not None and table.cellWidget(i, 1).isChecked()]
                
        plot_mode = self.plot_comboBox.currentText()
        self.plot_widgets.append(Plotter(plot_mode, prob_id, prob_object, self.run_thread, algo_ids, other_ids))
        
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


class MyFitnessLandscape(FitnessLandscape):
    def __init__(self,
                 problem,
                 _type="surface",
                 n_samples=30,
                 colorbar=False,
                 contour_levels=30,
                 kwargs_surface=dict(cmap="summer", rstride=1, cstride=1, alpha=0.2),
                 kwargs_contour=None,
                 kwargs_contour_labels=None,
                 **kwargs):
        
        super().__init__(problem, _type, n_samples, colorbar, contour_levels, kwargs_surface, kwargs_contour, kwargs_contour_labels, **kwargs)
        super().do()
        
    def add(self, points, label, **kwargs):
        # get the points coordinates from the points arg
        cutoff = 10
        best_point = points[0, :]
        if len(points[:, 0]) > cutoff:
            points = points[np.random.choice(len(points[:, 0]), cutoff, replace=False), :]
            word = 'random'
        else:
            word = '(all)'
        gen_label = label + f"\n({len(points[:, 0])} {word} points of last gen)"
        best_label = label + f"\n(Best point)"
        
        # if points have 2 dimensions, add the third dimension with the fitness value
        if len(points[0]) in [2, 3]:
            x,y,z = points[:, 0], points[:, 1], 0
            best_x, best_y, best_z = best_point[0], best_point[1], 0
            if len(points[0]) == 3:
                z, best_z = points[:, 2], best_point[2]
        else:
            MyMessageBox(f"Points have {len(points[0])} dimensions, only 2 or 3 are supported")
            return
        
        self.ax.scatter(x, y, z, s=50, label=gen_label, alpha=0.8, **kwargs)
        self.ax.scatter(best_x, best_y, best_z, s=100, label=best_label, alpha=1, **kwargs)
        
        # set the axes maximum and minimum values to the best and worst points
        # self.ax.set_xlim([min(np.min(x),best_x), max(np.max(x),best_x)])
        # self.ax.set_ylim([min(np.min(y),best_y), max(np.max(y),best_y)])
        # self.ax.set_zlim([min(np.min(z),best_z), max(np.max(z),best_z)]) if len(points[0]) == 3 else None
        
    def do(self):
        pass