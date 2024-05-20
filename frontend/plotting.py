from pymoo.core.plot import Plot
from pymoo.util.misc import all_combinations
from pymoo.visualization.scatter import Scatter, Plot
from pymoo.visualization.pcp import PCP

from PyQt5.QtWidgets import QVBoxLayout, QWidget
import pandas as pd
import numpy as np
from abc import abstractmethod

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from backend.run import RunThread
from backend.run import RunThread
from utils.defines import PROB_KEY, ALGO_KEY, SEEDS_KEY, N_EVAL_KEY, CONVERT_KEY
from utils.utils import MyMessageBox
from utils.useful_classes import MyFitnessLandscape

class PlotSectionOptions():
    def __init__(self, pi: bool, exclusive_pi: bool, prob: bool, avg: bool):
        self.pi = pi
        self.exclusive_pi = exclusive_pi
        self.prob = prob
        self.avg = avg
        
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100, fig=None, axes=None):
        fig = Figure(figsize=(width, height), dpi=dpi) if fig is None else fig
        self.axes = fig.add_subplot(111) if axes is None else axes
        super(MplCanvas, self).__init__(fig)

class QPlot(QWidget):
    """
        Abstract class for plotting in the GUI. It is a QWidget that contains a MplCanvas and a NavigationToolbar2QT.
        The plot_id is the identifier of the plot, and the window_title is the title of the window.
        Child classes must implement the sendPlotSectionOptions and _plot methods.
    """
    def __init__(self, plot_id, window_title):
        super().__init__()
        self.plot_id = plot_id
        self.window_title = window_title        
        self.sc = None

    def getPlotSectionArgs(self, algo_ids, prob_id, pi_id, runs_to_plot, run_thread, stats_seeds_df):
        self.algo_ids = algo_ids
        self.prob_id = prob_id
        self.pi_id = pi_id
        self.runs_to_plot = runs_to_plot
        self.run_thread = run_thread
        self.stats_seeds_df = stats_seeds_df

    @staticmethod
    @abstractmethod
    def sendPlotSectionOptions() -> PlotSectionOptions:
        """Return the options to set the plot section"""
        pass
    
    @abstractmethod
    def createCanvas(self) -> MplCanvas:
        """Create the source to be plotted"""
        pass
    
    def plot(self):
        try:
            self.sc = self.createCanvas() #@IgnoreException
        except Exception as e: 
            MyMessageBox(f"Could not plot '{self.plot_id}'. The following error occurred:\n{e}")
            return
        
        if self.sc is None:
            MyMessageBox(f"Could not plot '{self.plot_id}'. No source was created")
            return
        
        # Create toolbar, passing canvas as first parament, parent (self, the CustomDialog) as second.
        toolbar = NavigationToolbar2QT(self.sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        self.setLayout(layout)
        self.setWindowTitle(self.window_title)
        self.show()

    def drawSolutionsOnPlot(self, plot:Plot, **kwargs):
        
        stats, filtered_df = self.stats_seeds_df, pd.DataFrame()
        
        # Loop over each combination of 'algo' and 'value'
        for algo in self.algo_ids:
            for run_type in self.runs_to_plot:
                # find the seed using the self.stats_seeds_df
                seed = stats[(stats[ALGO_KEY] == algo) & (stats[PROB_KEY] == self.prob_id)][self.pi_id, run_type, SEEDS_KEY].values[0]
                # add row to temp_df with the prob_id, algo_id and seed
                temp_df = pd.DataFrame([[self.prob_id, algo, seed, run_type]], columns=[PROB_KEY, ALGO_KEY, SEEDS_KEY, 'Run Type'])
                # Append the results to 'filtered_df'
                filtered_df = pd.concat([filtered_df, temp_df])
        
        # Reset the index of 'filtered_df'
        filtered_df.reset_index(drop=True, inplace=True)            
            
        for prob_id, algo_id, seed, run_type in filtered_df.values:
            # get the best solution for each run_id
            best_gen = self.run_thread.best_gen[(prob_id, algo_id, seed)]
            # plot the best solution
            plot.add(best_gen, label = f"Algo '{algo_id}'{run_type}", **kwargs)
        
        plot.do()
        handles, labels = plot.ax.get_legend_handles_labels()
        # Using dict to remove duplicates, preserving the order
        by_label = dict(zip(labels, handles))
        if handles != {}:
            plot.ax.legend(by_label.values(), by_label.keys())
        
    
class QFitnessLandscape(QPlot):
    def __init__(self,
                 problem='prob_object' + CONVERT_KEY,
                 n_samples_2D=500,
                 n_samples_3D=30,
                 colorbar=False,
                 contour_levels=30,
                 max_n_solutions=100,
                 show_best_sol=True,
                 labels=True,
                 **kwargs):
        super().__init__("fitness_landscape", "Fitness Landscape")
        
        self.problem = problem
        self.n_samples_2D = n_samples_2D
        self.n_samples_3D = n_samples_3D
        self.colorbar = colorbar
        self.contour_levels = contour_levels
        self.max_n_solutions = max_n_solutions
        self.show_best_sol = show_best_sol
        self.labels = labels
        self.kwargs = kwargs
        self.pymoo_plot = None
            
    def createCanvas(self):
        pymoo_plot = MyFitnessLandscape(self.problem, n_samples_2D=self.n_samples_2D, n_samples_3D=self.n_samples_3D,
                                             colorbar=self.colorbar, contour_levels=self.contour_levels,
                                             max_n_solutions=self.max_n_solutions, show_best_sol=self.show_best_sol,
                                             labels=self.labels, **self.kwargs)
        
        self.drawSolutionsOnPlot(pymoo_plot)
        return MplCanvas(fig = pymoo_plot.fig, axes=pymoo_plot.ax)   
        
    def sendPlotSectionOptions() -> PlotSectionOptions:
        return PlotSectionOptions(pi=False, exclusive_pi=False, prob=False, avg=False)

    # def plotProgress(self):
    #     """Plot the progress of the checked algorithms for the given problem and checked performance indicators"""
    #     # get the data for the given problem
        
    #     if len(self.algo_ids) == 0:
    #         raise Exception("No algorithms were selected") #@IgnoreException
            
    #     self.sc, pi_id, data = MplCanvas(), self.pi_id, self.run_thread.data
        
    #     df_prob = data[data[PROB_KEY] == self.prob_id]
        
    #     # get the data for the given algorithms
    #     for algo_id in self.algo_ids:
    #         df_algo = df_prob[df_prob[ALGO_KEY] == algo_id]
    #         # get the data for the given performance indicator
    #         df_pi = df_algo[[N_EVAL_KEY, pi_id]]
    #         df_pi = df_pi.dropna(subset=[pi_id])  # Filter rows where pi_id has nan value
            
    #         # calculate mean and standard deviation
    #         mean = df_pi.groupby(N_EVAL_KEY)[pi_id].mean()
    #         std = df_pi.groupby(N_EVAL_KEY)[pi_id].std()

    #         # plot the data
    #         self.sc.axes.plot(mean.index, mean.values, label=f"{algo_id}")
    #         self.sc.axes.fill_between(mean.index, (mean-std).values, (mean+std).values, alpha=0.2)
                
    #     # name the plot
    #     self.sc.axes.set_title(f"'{pi_id}' progress on problem '{self.prob_id}'")
    #     # add labels
    #     self.sc.axes.set_xlabel('Number of evaluations')
    #     self.sc.axes.set_ylabel('Performance Indicator')
    #     # add legend
    #     self.sc.axes.legend()

    # def plotPCP(self):
    #     """Plot the Parallel Coordinates of the checked algorithms for the given problem and checked seeds"""
        
    #     if PROB_KEY not in self.runs_to_plot and len(self.algo_ids) == 0:
    #         raise Exception("No algorithms or problem were selected to be plotted") #@IgnoreException
        
    #     plot = PCP(legend=True)
        
    #     # see if other ids contain PROB_KEY, if so, get it out of the list
    #     if PROB_KEY in self.runs_to_plot:
    #         pareto_front = self.prob_object.pareto_front()
    #         if pareto_front is None:
    #             raise Exception(f"Problem '{self.prob_id}' does not have a Pareto Front available") #@IgnoreException
    #         else:
    #             plot.add(pareto_front, label = self.prob_id)
    #         self.runs_to_plot.remove(PROB_KEY)
            
    #     self.plotSolutions(plot)        
    #     self.sc.axes.set_title(f"Parallel Coordinates on Problem: '{self.prob_id}'", y=1.05)

    # def plotParetoSets(self):
    #     """Plot the Pareto front of the checked algorithms for the given problem and checked seeds"""
        
    #     if self.prob_object.n_obj not in [2,3]:
    #         raise Exception("Pareto Sets can only be plotted for problems with 2 or 3 objectives") #@IgnoreException
        
    #     plot = Scatter(title=f"Scatter Plot on Problem: '{self.prob_id}'", legend=True)
    
    #     # see if other ids contain PROB_KEY, if so, get it out of the list
    #     if PROB_KEY in self.runs_to_plot:
    #         if self.prob_object.pareto_front() is None:
    #             MyMessageBox(f"Problem '{self.prob_id}' does not have a Pareto Front available")
    #         else:
    #             plot.add(self.prob_object.pareto_front(), label = self.prob_id)
    #         self.runs_to_plot.remove(PROB_KEY)
            
    #     self.plotSolutions(plot)
        
    # def plotFitnessLandscape(self):
    #     """Plot the fitness landscape of the checked algorithms for the given problem and checked seeds"""
        
    #     # raises its own exceptions
    #     plot = MyFitnessLandscape(self.prob_object, title=f"Fitness Landscape on Problem: '{self.prob_id}'")
    #     self.plotSolutions(plot)
    #     if plot.sets_of_points == []:
    #         plot.ax.get_legend().remove()
        
    
