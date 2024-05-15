from PyQt5.QtWidgets import QFrame, QTableWidget, QTableWidgetItem, QCheckBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor                    

import numpy as np
import pandas as pd

from backend.run import RunThread
from backend.run import RunThread
from utils.defines import (DESIGNER_RUN_TAB, PROB_KEY, ALGO_KEY, SEEDS_KEY, N_GEN_KEY, N_EVAL_KEY, VOTING_KEY, PI_KEY,
                           CLASS_KEY, TERM_KEY, PLOT_PROGRESS_KEY, PLOT_PS_KEY, PLOT_PC_KEY, PLOT_FL_KEY, MEDIAN_KEY,
                           BEST_KEY, WORST_KEY, AVG_KEY, VALUE_KEY)
from frontend.plotting import Plotter
from utils.utils import myFileManager, setBold, MyMessageBox, setCombobox, numberPresentation
class RunTab(QFrame):
    """
    Represents the tab in the GUI that is responsible for 
    managing and displaying the results of a run 

    Attributes
    ----------
        run_thread (RunThread): The thread from which the algorithm will or has run.
        pi_ids (list): List of performance indicator ids.
        term_data (DataFrame): The final generation data, averaged across seeds.
        prob_ids (list): List of problem ids.
        algo_ids (list): List of algorithm ids.
        plot_widgets (list): List of plot widgets to prevent them from being garbage collected.
        
    Important Methods
    -------
        setPlotOptionsTable(event=None, set_algos=False): Sets the checkboxes for the given ids in the tables, when the plotting
        mode changes, so the user chooses the seeds or the performance indicators to plot.
        changeTable(): Updates the table based on the selected item id.
        plot(): Calls the Plotter class to plot the results in the respective plot mode.
        saveRun(): Saves the run thread object.
        saveResult(): Saves the result of the run in a csv.
    """
    def __init__(self, run_thread: RunThread, label: str):
        super().__init__()
        loadUi(DESIGNER_RUN_TAB, self)
                
        # get the class variables
        self.run_thread = run_thread        
        self.pi_ids = run_thread.run_args_list[0].pi_ids

        # get the final generation for each seed
        self.term_df = self.run_thread.data.groupby([PROB_KEY, ALGO_KEY, SEEDS_KEY]).last().reset_index()
        
        # get the statistics (min, max, median, average) of the data
        self.stats_seeds_df, self.avg_df, self.colapsed_stats_df = self.getStatisticsDFs() 
           
        # get column by name
        self.prob_ids = list(self.term_df[PROB_KEY].unique())
        self.algo_ids = list(self.term_df[ALGO_KEY].unique())
        
        # store the plot dialogs so they are not garbage collected
        self.plot_widgets = []
        
        self.setUI(label)
    
    def getStatisticsDFs(self):
        
        # drop unnecessary columns
        df = self.term_df.drop(columns=[N_GEN_KEY, N_EVAL_KEY, SEEDS_KEY])
        # get the average, median, min and max of the data    
        df = df.groupby([PROB_KEY, ALGO_KEY]).agg(["min", "max", "median", "mean"]).reset_index()
        cols = tuple([(PROB_KEY, ''), (ALGO_KEY, '')] + [(pi_id,lvl2) for pi_id in self.pi_ids for lvl2 in [BEST_KEY, WORST_KEY, MEDIAN_KEY, AVG_KEY]])
        df.columns = pd.MultiIndex.from_tuples(cols)
        
        # set a three level column index for the data (pf, min/max/median/average, value/seed)
        cols = pd.MultiIndex.from_tuples(((PROB_KEY, '', ''), (ALGO_KEY, '', '')))
        stats_seeds_df = pd.DataFrame(columns=cols)
        stats_seeds_df[(PROB_KEY, '', '')] = df[(PROB_KEY, '')]
        stats_seeds_df[(ALGO_KEY, '', '')] = df[(ALGO_KEY, '')]
        
        # find the seeds for each performance indicator
        for pi_id in self.pi_ids:
            for lvl2 in [BEST_KEY, WORST_KEY, MEDIAN_KEY, AVG_KEY]:
                stats_seeds_df[(pi_id, lvl2, VALUE_KEY)] = df[(pi_id, lvl2)]
                if lvl2 == AVG_KEY:
                    # nan column of size of the data
                    seeds = np.nan * np.zeros(len(stats_seeds_df))
                else:
                    seeds = self.findSeeds(pi_id, lvl2, stats_seeds_df, self.term_df)
                stats_seeds_df[(pi_id, lvl2, SEEDS_KEY)] = seeds
                
        avg_df = df.copy()
        # get only the average column
        columns_to_drop_list = [[(pi_id, BEST_KEY), (pi_id, WORST_KEY), (pi_id, MEDIAN_KEY)] for pi_id in self.pi_ids]
        [avg_df.drop(columns=columns_to_drop, inplace=True) for columns_to_drop in columns_to_drop_list]
        new_cols = [col[0] for col in avg_df.columns]
        avg_df.columns = new_cols   

        # get the min, median, max columns of each pi to be displayed in different rows
        columns_to_drop_list = [[(pi_id, AVG_KEY)] for pi_id in self.pi_ids]
        [df.drop(columns=columns_to_drop, inplace=True) for columns_to_drop in columns_to_drop_list]
        lst = []
        for i in range(len(df)):
            prob_id, algo_id = df.iloc[i][PROB_KEY].values[0], df.iloc[i][ALGO_KEY].values[0]
            for lvl2 in [BEST_KEY, MEDIAN_KEY, WORST_KEY]:
                values = [ df.iloc[i][(pi_id, lvl2)] for pi_id in self.pi_ids ]
                lst.append([prob_id, algo_id + lvl2] + values)
                
        colapsed_stats_df = pd.DataFrame(lst, columns=[PROB_KEY, ALGO_KEY] + self.pi_ids)

        return stats_seeds_df, avg_df, colapsed_stats_df
    
    def findSeeds(self, pi_id, lvl2, data, term_data):
        
        seeds = np.zeros(len(data)).astype(float)
        for i, row in data.iterrows():
            prob_id, algo_id = row[(PROB_KEY, '', '')], row[(ALGO_KEY, '', '')]
            value = row[(pi_id, lvl2, VALUE_KEY)]
            
            # Calculate the absolute difference between the target value and each value in the column
            filt_term_data = term_data[(term_data[PROB_KEY] == prob_id) & (term_data[ALGO_KEY] == algo_id)]
            diff = abs(filt_term_data[pi_id] - value)
    
            # Find the index of the minimum value in the difference
            if diff.isna().all():
                idx = np.nan
            else:
                idx = diff.idxmin()
                            
            # Use this index to get the corresponding seed
            seeds[i] = term_data.loc[idx, SEEDS_KEY] if idx is not np.nan else np.nan
        
        return seeds
        
    def setUI(self, label):
        
        # header buttons
        self.save_result.clicked.connect(self.saveResult)
        self.save_table.clicked.connect(self.saveTable)
        self.save_run.clicked.connect(self.saveRun)
        
        # table section (options and table itself) 
        self.table.horizontalHeader().sectionDoubleClicked.connect(lambda col: self.headerClick(col, "horizontal"))
        self.table.verticalHeader().sectionDoubleClicked.connect(lambda row: self.headerClick(row, "vertical"))
        self.table.itemDoubleClicked.connect(self.tableItemClick)
        setCombobox(self.values_comboBox, center_items=True, index_changed_function=self.tableOptionsChanged)
        setCombobox(self.selected_id, center_items=True, index_changed_function=self.changeTable)
        setCombobox(self.showing_values, center_items=True, index_changed_function=self.changeTable)

        # plot section
        self.plot_button.clicked.connect(self.plot)
        items = [PLOT_PROGRESS_KEY, PLOT_PS_KEY, PLOT_PC_KEY] if self.run_thread.moo else [PLOT_FL_KEY, PLOT_PROGRESS_KEY]
        setCombobox(self.plot_comboBox, items, True, self.setPlotOptionsTable)
        setCombobox(self.plot_prob, self.prob_ids, True)
        setCombobox(self.plot_pi, self.pi_ids, True)

        # set the labels                         
        self.label.setText(label)
        seed_str = "seed" if self.run_thread.n_seeds == 1 else "different seeds"
        self.n_seeds_label.setText(f"Run on <b>{self.run_thread.n_seeds}</b> {seed_str}")
        self.n_seeds_label.setAlignment(Qt.AlignCenter)
        self.term_label.setText(f"Termination criteria: <b>{self.run_thread.term_id}</b> <br>(Double click to see parameters)</font>")
        self.term_label.setAlignment(Qt.AlignCenter)
        self.term_label.mouseDoubleClickEvent = self.seeTermination

        # make table non-editable
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) 
        
        # set the table
        self.tableOptionsChanged()
        self.setPlotOptionsTable(set_algos=True)

    def setPlotOptionsTable(self, event=None, set_algos=False):
        """set the checkboxes for the given ids in the tables"""

        # set the checkboxes for the algorithms in the first column
        if set_algos:
            for i, algo_id in enumerate(self.algo_ids):
                checkbox = QCheckBox(algo_id)
                self.checkBox_table.setCellWidget(i, 0, checkbox)
                checkbox.setChecked(i == 0)

        # if plot mode is progress, only display one column with the algorithms
        if self.plot_comboBox.currentText() == PLOT_PROGRESS_KEY:
            self.checkBox_table.setColumnCount(1)
        else:
            # else add a column with the best median and worst runs
            self.checkBox_table.setColumnCount(2)
            ids = [BEST_KEY, MEDIAN_KEY, WORST_KEY]
            header = "Run"
            
            # add the possibility to plot the problem if the plot mode is Pareto Set or Parallel Coordinates
            if self.plot_comboBox.currentText() in [PLOT_PS_KEY, PLOT_PC_KEY]:
                ids = [PROB_KEY] + ids
                header = "Prob/Run" 
            
            self.checkBox_table.setHorizontalHeaderItem(1, QTableWidgetItem(header))
        
            # put the ids checkboxes in self.checkBox_table second column
            row_count = len(ids)
            self.checkBox_table.setRowCount(row_count)
            for i, id in enumerate(ids):
                checkbox = QCheckBox(str(id))
                self.checkBox_table.setCellWidget(i, 1, checkbox)
                checkbox.setChecked(i == 0)
                        
    def tableOptionsChanged(self):
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
        
        if self.showing_values.currentText() == "Averaged across seeds":
            df = self.avg_df.copy()
            avg = True
        else:
            df = self.colapsed_stats_df.copy()
            rows = [i*3 for i in range(len(self.algo_ids))]
            avg = False
            
        selected_id = self.selected_id.currentText()
        if self.values_comboBox.currentText() == "Performance Indicator":
            df = df.pivot(index=ALGO_KEY, columns=PROB_KEY, values=selected_id)
        elif self.values_comboBox.currentText() == "Problem":
            df = df[df[PROB_KEY] == selected_id]
            df.drop(columns=[PROB_KEY], inplace=True)
            df = df.set_index(df.columns[0])
        else:
            raise ValueError("Voting by can only be Performance Indicator or Problem")
                
        # update the table widget
        df[VOTING_KEY] = [0 for _ in range(len(df))]
        
        n_cols = len(df.columns)
        n_rows = len(df.index)
        self.table.setColumnCount(n_cols)
        self.table.setRowCount(n_rows)
        
        # set the horizontal headers
        for j in range(n_cols):
            header_item = QTableWidgetItem(df.columns[j])
            self.table.setHorizontalHeaderItem(j, header_item)
                
        grey, light_grey = QColor(242, 242, 242), QColor(250, 250, 250)
        color = grey
        
        # set the non voting columns
        for i in range(n_rows):
            if (i % 3 == 0 and not avg) or avg:
                color = light_grey if color == grey else grey
            item = QTableWidgetItem(df.index[i])
            item.setBackground(color)
            self.table.setVerticalHeaderItem(i, item)
                
            # get the float into str representation and count the votes
            for j in range(n_cols-1):
                nice_string = numberPresentation(df.iloc[i, j])
                item = QTableWidgetItem(nice_string)
                # set text to bold if it is the smallest value in the column
                rows_to_check = [row + i % 3 for row in rows] if not avg else [ii for ii in range(len(self.algo_ids))]
                if df.iloc[i, j] == df.iloc[rows_to_check, j].min():
                    setBold(item)
                    df.loc[df.index[i], VOTING_KEY] += 1
                item.setBackground(color)
                self.table.setItem(i, j, item)
        
        color = grey
        # set the voting column
        for i in range(n_rows):
            if (i % 3 == 0 and not avg) or avg:
                color = light_grey if color == grey else grey
            nice_string = str(int(df.iloc[i, -1]))
            item = QTableWidgetItem(nice_string)
            self.table.setItem(i, n_cols-1, item)
            rows_to_check = [row + i % 3 for row in rows] if not avg else [ii for ii in range(len(self.algo_ids))]
            if df.iloc[i, -1] == df.iloc[rows_to_check, -1].max():
                setBold(item)
            item.setBackground(color)
            
        self.table_df = df.copy()

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
        if self.showing_values.currentText() != "Averaged across seeds" and key == ALGO_KEY:
            for end_key in [BEST_KEY, MEDIAN_KEY, WORST_KEY]:
                id = id[:-len(end_key)] if id.endswith(end_key) else id
                
        args = self.run_thread.parameters[key][id].copy()
        clazz = args.pop(CLASS_KEY)
        string = f"Parameters for {key} of class {clazz} with id \'{id}\': \n {args}"
        MyMessageBox(string, 'Parameters', warning_icon=False)

    def tableItemClick(self, item):
        """Handle a click on a table item"""
        
        if self.showing_values.currentText() == "Averaged across seeds":
            string = 'When showing Best, Median and Worst values, double click will show the seed of the respective run'
            MyMessageBox(string, 'Parameters', warning_icon=False)
            return
        
        row = item.row()
        col = item.column()
        
        # get the headers texts
        row_header = self.table.verticalHeaderItem(row).text()
        col_header = self.table.horizontalHeaderItem(col).text()
        
        if col_header == VOTING_KEY:
            return
        
        if row_header.endswith(BEST_KEY) or row_header.endswith(MEDIAN_KEY) or row_header.endswith(WORST_KEY):
            row_header = row_header[:-len(BEST_KEY)] if row_header.endswith(BEST_KEY) else row_header
            row_header = row_header[:-len(MEDIAN_KEY)] if row_header.endswith(MEDIAN_KEY) else row_header
            row_header = row_header[:-len(WORST_KEY)] if row_header.endswith(WORST_KEY) else row_header
            lvl2 = BEST_KEY if row_header.endswith(BEST_KEY) else MEDIAN_KEY if row_header.endswith(MEDIAN_KEY) else WORST_KEY
        
        algo_id = row_header
        if self.values_comboBox.currentText() == "Performance Indicator":
            prob_id = col_header
            pi_id = self.selected_id.currentText()
        elif self.values_comboBox.currentText() == "Problem":
            prob_id = self.selected_id.currentText()
            pi_id = col_header
        
        # get the seed
        seed = self.stats_seeds_df[(self.stats_seeds_df[PROB_KEY] == prob_id) & (self.stats_seeds_df[ALGO_KEY] == algo_id)][pi_id,lvl2,SEEDS_KEY].values[0]
        seed = int(seed) if seed == int(seed) else seed
        MyMessageBox(f"Run of problem {prob_id} with algorithm {algo_id} and performance indicator {pi_id}{lvl2} value was obtained with seed {seed}", 'Seed', warning_icon=False)

    def seeTermination(self, event):
        """See the termination criteria"""
        id = self.run_thread.term_id
        args = self.run_thread.parameters[TERM_KEY][id].copy()
        clazz = args.pop(CLASS_KEY)
        string = f"Parameters for {TERM_KEY} of class {clazz} with id \'{id}\': \n {args}"
        MyMessageBox(string, 'Parameters', warning_icon=False)
        
    # buttons methods
    
    def plot(self):
        """Plot the results"""
        # get prob id and prob object from the combobox
        prob_id = self.plot_prob.currentText()
        prob_object = None
        for run_args in self.run_thread.run_args_list:
            if run_args.prob_id == prob_id:
                prob_object = run_args.prob_object
                break
        if prob_object == None:
            raise ValueError(f'Prob Object not found with id {prob_id}')
        
        # get pi id from the combobox
        pi_id = self.plot_pi.currentText()
        
        # get algo ids from the checkboxes on the first column
        table = self.checkBox_table
        algo_ids = [table.cellWidget(i, 0).text() for i in range(len(self.algo_ids)) 
                    if table.cellWidget(i, 0).isChecked()]
        
        # get runs to plot from the checkboxes on the second column if it exists
        if table.columnCount() > 1:
            runs_to_plot = [table.cellWidget(i, 1).text() for i in range(table.rowCount()) 
                        if table.cellWidget(i, 1) is not None and table.cellWidget(i, 1).isChecked()]
        else:
            runs_to_plot = None
        
        # get the plot mode
        plot_mode = self.plot_comboBox.currentText()
        
        # create the plot
        plotter = Plotter(plot_mode, self.label.text(), self.run_thread, self.stats_seeds_df, 
                          pi_id, prob_id, prob_object, algo_ids, runs_to_plot)
        self.plot_widgets.append(plotter)
    
    def saveRun(self):
        """Save the run thread object"""
        
        data = {'parameters': self.run_thread.parameters,
                'run_options': self.run_thread.run_options,
                'best_gen': self.run_thread.best_gen,
                'data': self.run_thread.data,
                'run_counter': self.run_thread.run_counter,
                'moo': self.run_thread.moo}

        def_name = self.label.text() + ".pickle"
        myFileManager('Save Run Thread', def_name, data)
        
    def saveResult(self):
        """Save the result of the run"""
        name = self.label.text().replace("Run", "Result") + ".csv"
        myFileManager('Save Run Data', name, self.run_thread.data, ".csv", "CSV Files (*.csv)")

    def saveTable(self):
        """Save the table as a csv"""
        name = self.label.text().replace("Run", "Table") + ".csv"
        myFileManager('Save Table Data', name, self.table_df, ".csv", "CSV Files (*.csv)", save_csv_index=True)