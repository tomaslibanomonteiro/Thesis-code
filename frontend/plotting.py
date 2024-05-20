from pymoo.core.plot import Plot
from pymoo.visualization.scatter import Scatter, Plot
from pymoo.visualization.pcp import PCP

from PyQt5.QtWidgets import QVBoxLayout, QWidget
import pandas as pd
from abc import abstractmethod

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from utils.defines import PROB_KEY, ALGO_KEY, SEEDS_KEY, N_EVAL_KEY, CONVERT_KEY
from utils.utils import MyMessageBox, ordinal
from utils.useful_classes import MyFitnessLandscape

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100, fig=None, axes=None):
        fig = Figure(figsize=(width, height), dpi=dpi) if fig is None else fig
        self.axes = fig.add_subplot(111) if axes is None else axes
        super(MplCanvas, self).__init__(fig)

class QPlot(QWidget):
    def __init__(self, window_title, labels):
        super().__init__()
        self.window_title = window_title       
        self.labels = labels 
        # attributes to be set by the getPlotSectionArgs method
        self.plot_id = None
        self.prob_id = None
        self.prob_object = None
        self.pi_id = None
        self.algos_dict = None
        self.run_types = None
        self.run_thread = None
        self.stats_seeds_df = None
        # attribute to be set by the createCanvas method
        self.sc = None

    def getPlotSectionArgs(self, plot_id, prob_id, prob_object, pi_id, algo_ids, run_types, run_thread, stats_seeds_df):
        self.plot_id = plot_id
        self.prob_id = prob_id
        self.prob_object = prob_object
        self.pi_id = pi_id
        self.algos_dict = {}
        for algo_id in algo_ids:
            for run_args in run_thread.run_args_list:
                if run_args.algo_id == algo_id:
                    self.algos_dict[algo_id] = run_args.algo_object
                    break 
        self.run_types = run_types
        self.run_thread = run_thread
        self.stats_seeds_df = stats_seeds_df

    def getParetoFront(self):
        algo_ids = list(self.algos_dict.keys())
        # check if all algos have the same reference directions
        ref_dirs_classes = [self.algos_dict[algo_id].ref_dirs.__class__ 
                            if hasattr(self.algos_dict[algo_id], 'ref_dirs') else None for algo_id in algo_ids]
        
        # if all None
        if all(ref_dir_class is None for ref_dir_class in ref_dirs_classes):
            return self.prob_object.pareto_front()
        
        idx = ref_dirs_classes.index(next(filter(None, ref_dirs_classes)))
        
        # index of the first not None ref_dirs
        ref_dirs = self.algos_dict[algo_ids[idx]].ref_dirs
        
        try:
            pareto_front = self.prob_object.pareto_front(ref_dirs)
            if len(set(ref_dirs_classes)) != 1:
                MyMessageBox("Selected algorithms have different reference directions. Pareto Front calculated with the" 
                                f" reference directions of the {ordinal(idx+1)} selected algorithm")
        except:
            pareto_front = self.prob_object.pareto_front()
            MyMessageBox(f"Could not calculate the Pareto Front using reference directions from the {ordinal(idx+1)} selected algorithm." 
                            " Pareto Front calculated with the problem default reference directions.")
        
        return pareto_front
    
    @abstractmethod
    def createCanvas(self) -> MplCanvas:
        """Create the source to be plotted"""
        pass
    
    def getSeedFromIds(self, prob_id, algo_id, run_type):
        stats = self.stats_seeds_df
        seed = stats[(stats[ALGO_KEY] == algo_id) & (stats[PROB_KEY] == prob_id)][self.pi_id, run_type, SEEDS_KEY].values[0]
        return seed
    
    def drawSolutionsOnPlot(self, plot:Plot, **kwargs):
        
        stats, filtered_df = self.stats_seeds_df, pd.DataFrame()
        
        # Loop over each combination of 'algo' and 'value'
        for algo in self.algos_dict.keys():
            for run_type in self.run_types:
                # find the seed using the self.stats_seeds_df
                seed = self.getSeedFromIds(self.prob_id, algo, run_type)
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
        
    def plot(self):
        try:
            self.sc = self.createCanvas() #@IgnoreException
        except Exception as e: 
            MyMessageBox(f"Could not plot '{self.plot_id}'. The following error occurred:\n{e}")
            return
        
        if self.sc is None:
            MyMessageBox(f"Could not plot '{self.plot_id}'. No source was created")
            return
        
        if not self.labels:
            # remove all the labels in the plot
            self.sc.axes.legend().remove()
        # Create toolbar, passing canvas as first parament, parent (self, the CustomDialog) as second.
        toolbar = NavigationToolbar2QT(self.sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        self.setLayout(layout)
        self.setWindowTitle(self.window_title)
        self.show()
    
class QFitnessLandscape(QPlot):
    def __init__(self,
                 n_samples_2D=500,
                 n_samples_3D=30,
                 colorbar=False,
                 contour_levels=30,
                 max_n_solutions=100,
                 show_best_sol=True,
                 labels=True,
                 **kwargs):
        super().__init__("Fitness Landscape", labels)
        
        self.n_samples_2D = n_samples_2D
        self.n_samples_3D = n_samples_3D
        self.colorbar = colorbar
        self.contour_levels = contour_levels
        self.max_n_solutions = max_n_solutions
        self.show_best_sol = show_best_sol
        self.kwargs = kwargs
        self.pymoo_plot = None
            
    def createCanvas(self):
        pymoo_plot = MyFitnessLandscape(self.prob_object, n_samples_2D=self.n_samples_2D, n_samples_3D=self.n_samples_3D, colorbar=self.colorbar, 
                                        contour_levels=self.contour_levels, max_n_solutions=self.max_n_solutions, 
                                        show_best_sol=self.show_best_sol, **self.kwargs)
        
        self.drawSolutionsOnPlot(pymoo_plot)
        return MplCanvas(fig = pymoo_plot.fig, axes=pymoo_plot.ax)   
        
class QPCP(QPlot):
    def __init__(self,
                 plot_pareto_front=False,
                 show_bounds=True,
                 n_ticks=5,
                 normalize_each_axis=True,
                 bbox=False,
                 legend=True,
                 labels=True,
                 **kwargs):
        super().__init__("Parallel Coordinates Plot", labels)
        
        self.plot_pareto_front = plot_pareto_front
        self.show_bounds = show_bounds
        self.n_ticks = n_ticks
        self.normalize_each_axis = normalize_each_axis
        self.bbox = bbox
        self.kwargs = kwargs
        self.legend = legend
            
    def createCanvas(self):
        
        plot = PCP(show_bounds=self.show_bounds, n_ticks=self.n_ticks, normalize_each_axis=self.normalize_each_axis, 
                   bbox=self.bbox, legend=self.legend, **self.kwargs)
        
        if self.plot_pareto_front:
            pf = self.getParetoFront()
            plot.add(pf, label = self.prob_id)
            
        self.drawSolutionsOnPlot(plot)        
        
        canvas = MplCanvas(fig = plot.fig, axes=plot.ax)
        canvas.axes.set_title(f"Parallel Coordinates on Problem: '{self.prob_id}'", y=1.05)

        return canvas
    
class QParetoSets(QPlot):
    def __init__(self, plot_pareto_front=True, intial_angle_1 = 45, initial_angle_2= 45, prob_object = 'prob_object' + CONVERT_KEY, labels = True, **kwargs):
        super().__init__("Pareto Sets", labels)
        self.plot_pareto_front = plot_pareto_front
        self.intial_angle_1 = intial_angle_1
        self.initial_angle_2 = initial_angle_2
        self.prob_object = prob_object
        self.kwargs = kwargs
        
    def createCanvas(self):
        
        if self.prob_object.n_obj not in [2,3]:
            raise Exception("Pareto Sets can only be plotted for problems with 2 or 3 objectives") #@IgnoreException
        
        plot = Scatter(angle=(self.intial_angle_1, self.initial_angle_2))
    
        if self.plot_pareto_front:
            pf = self.getParetoFront()
            plot.add(pf, label = self.prob_id)
            
        self.drawSolutionsOnPlot(plot)
        
        return MplCanvas(fig = plot.fig, axes=plot.ax)
        
class QProgress(QPlot):
    def __init__(self, average_across_seeds = True, labels = True, **kwargs):
        super().__init__("Progress", labels)
        self.average_across_seeds = average_across_seeds
        self.kwargs = kwargs
    
    def createCanvas(self):        
        
        warning_sw = True
        canvas, pi_id, data = MplCanvas(), self.pi_id, self.run_thread.data
        df_prob = data[data[PROB_KEY] == self.prob_id]
        
        # get the data for the given algorithms
        for algo_id in self.algos_dict.keys():
            df_algo = df_prob[df_prob[ALGO_KEY] == algo_id]
            # get the data for the given performance indicator
            df_pi = df_algo[[SEEDS_KEY, N_EVAL_KEY, pi_id]]
            df_pi = df_pi.dropna(subset=[pi_id])  # Filter rows where pi_id has nan value
            
            if self.average_across_seeds:
                pi = df_pi.groupby(N_EVAL_KEY)[pi_id].mean()
                std = df_pi.groupby(N_EVAL_KEY)[pi_id].std()
                canvas.axes.plot(pi.index, pi.values, label=f"{algo_id}")
                canvas.axes.fill_between(pi.index, (pi-std).values, (pi+std).values, alpha=0.2)
                if len(self.run_types) > 0 and warning_sw:
                    warning_sw = False
                    MyMessageBox("Average across seeds selected. The specific choosen runs will be ignored"
                                    " and the average of the runs across all seeds will be plotted.")            
            else:
                for run_type in self.run_types:
                    seed = self.getSeedFromIds(self.prob_id, algo_id, run_type)
                    pi = df_pi[df_pi[SEEDS_KEY] == seed]
                    canvas.axes.plot(pi[N_EVAL_KEY], pi[pi_id], label=f"{algo_id} {run_type}")
                
        # name the plot
        canvas.axes.set_title(f"'{pi_id}' progress on problem '{self.prob_id}'")
        # add labels
        canvas.axes.set_xlabel("Function evaluations")
        canvas.axes.set_ylabel(pi_id)
        # add legend
        canvas.axes.legend()
        
        return canvas