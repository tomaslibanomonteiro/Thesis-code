from pymoo.core.plot import Plot
from pymoo.util.misc import all_combinations
from PyQt5.QtWidgets import QVBoxLayout, QWidget
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

                
class MyFitnessLandscape(Plot):

    def __init__(self,
                 problem,
                 n_samples_2D=500,
                 n_samples_3D=30,
                 colorbar=False,
                 contour_levels=30,
                 kwargs_surface=None,
                 kwargs_contour=None,
                 kwargs_contour_labels=None,
                 **kwargs):


        super().__init__(**kwargs)
        self.problem = problem
        self.n_samples_2D = n_samples_2D
        self.n_samples_3D = n_samples_3D
        self.colorbar = colorbar
        self.sets_of_points = []
        self.sets_labels = []
        self.contour_levels = contour_levels

        self.kwargs_surface = kwargs_surface
        if self.kwargs_surface is None:
            self.kwargs_surface = dict(cmap="summer", rstride=1, cstride=1, alpha=0.2)

        self.kwargs_contour = kwargs_contour
        if self.kwargs_contour is None:
            self.kwargs_contour = dict(linestyles="solid", offset=-1)

        self.kwargs_contour_labels = kwargs_contour_labels

    def _do(self):

        problem, sets_of_points = self.problem, self.sets_of_points

        # find the min and max values of the decision variable between the sets of points
        if sets_of_points == []:
            x_min, x_max = problem.xl[0], problem.xu[0]
        else:
            x_min = min([min(points[:, 0]) for points in sets_of_points])
            x_max = max([max(points[:, 0]) for points in sets_of_points])

        if problem.n_var == 1 and problem.n_obj == 1:

            self.init_figure()
            X = np.linspace(x_min, x_max, self.n_samples_2D)[:, None]
            Z = problem.evaluate(X, return_values_of=["F"])
            self.ax.plot(X, Z, alpha=0.2)
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("f(x)")
            
            self.plot_points()

        elif problem.n_var == 2 and problem.n_obj == 1:
            n_samples = self.n_samples_3D
            if sets_of_points == []:
                y_min, y_max = problem.xl[1], problem.xu[1]
            else:
                y_min = min([min(points[:, 1]) for points in sets_of_points])
                y_max = max([max(points[:, 1]) for points in sets_of_points])
            
            A = np.linspace(x_min, x_max, n_samples)
            B = np.linspace(y_min, y_max, n_samples)
            X = all_combinations(A, B)

            F = np.reshape(problem.evaluate(X, return_values_of=["F"]), (n_samples, n_samples))

            _X = X[:, 0].reshape((n_samples, n_samples))
            _Y = X[:, 1].reshape((n_samples, n_samples))
            _Z = F.reshape((n_samples, n_samples))

            self.init_figure(plot_3D=True)

            surf = self.ax.plot_surface(_X, _Y, _Z, **self.kwargs_surface)
            if self.colorbar:
                self.fig.colorbar(surf)
            
            self.plot_points()
        else:
            raise Exception("Only landscapes of problems with one or two variables and one objective can be visualized.")

    def plot_points(self):
        
        for points, (best_label, gen_label), in zip(self.sets_of_points, self.sets_labels):
            # if points have 2 dimensions, add the third dimension with the fitness value
            if len(points[0]) in [2,3]:
                x,y = points[1:, 0], points[1:, 1]
                best_x, best_y = points[0, 0], points[0, 1]
                if len(points[0]) == 2:
                    self.ax.scatter(x, y, s=10, label=gen_label, alpha=0.5)
                    self.ax.scatter(best_x, best_y, s=50, label=best_label, alpha=1)
                if len(points[0]) == 3:
                    z, best_z = points[1:, 2], points[0, 2]
                    self.ax.scatter(x, y, z, s=20, label=gen_label, alpha=0.5)
                    self.ax.scatter(best_x, best_y, best_z, s=100, label=best_label, alpha=1)
            else:
                self.sets_of_points = []
                MyMessageBox(f"Solutions have {len(points[0])-1} dimensions in decision space, only 1 or 2 are supported")
                    
    def add(self, points, label):
        
        self.legend = True
        
        # get the points coordinates from the points arg
        best_point = points[0, :]
        
        # if the number of points is greater than 10, get a random sample of 10 points
        cutoff = 10
        if len(points[:, 0]) > cutoff:
            points = points[np.random.choice(len(points[1:, 0]), cutoff, replace=False), :]
            word = 'random'
        else:
            word = '(all)'
        gen_label = label + f"\n({len(points[:, 0])} {word} points of last gen)"
        best_label = label + f"\n(Best point)"
        
        points = np.concatenate((best_point[np.newaxis,:], points))
        self.sets_of_points.append(points)  
        self.sets_labels.append((best_label, gen_label))
        
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, width=5, height=4, dpi=100, fig=None, axes=None):
        fig = Figure(figsize=(width, height), dpi=dpi) if fig is None else fig
        self.axes = fig.add_subplot(111) if axes is None else axes
        super(MplCanvas, self).__init__(fig)
    
class Plotter(QWidget):

    def __init__(self, plot_mode, prob_id:str, prob_object, run_thread:RunThread, algo_ids:list, other_ids:list, title='Plot'):
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
        self.setWindowTitle(title)
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
        self.sc.axes.set_title(f"Progress on problem: '{self.prob_id}'")
        # add labels
        self.sc.axes.set_xlabel('Number of evaluations')
        self.sc.axes.set_ylabel('Performance Indicator')
        # add legend
        self.sc.axes.legend()

    def plotPCP(self):
        """Plot the Parallel Coordinates of the checked algorithms for the given problem and checked seeds"""
            
        plot = PCP(legend=True)
        
        # see if other ids contain 'Problem', if so, get it out of the list
        if 'Problem' in self.other_ids:
            pareto_front = self.prob_object.pareto_front()
            if pareto_front is None:
                MyMessageBox(f"Problem '{self.prob_id}' does not have a Pareto Front available")
            else:
                plot.add(pareto_front, label = self.prob_id)
            self.other_ids.remove('Problem')
            
        self.plotSolutions(plot)        
        self.sc.axes.set_title(f"Paralel Coordinates on Problem: '{self.prob_id}'", y=1.05)

    def plotParetoSets(self):
        """Plot the Pareto front of the checked algorithms for the given problem and checked seeds"""
            
        plot = Scatter(title=f"Scatter Plot on Problem: '{self.prob_id}'", legend=True)
    
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
        
        plot = MyFitnessLandscape(self.prob_object, title=f"Fitness Landscape on Problem: '{self.prob_id}'")
        self.plotSolutions(plot)
        if plot.sets_of_points == []:
            plot.ax.get_legend().remove()
            
    def plotSolutions(self, plot:Plot, **kwargs):
        
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
        if handles != {}:
            plot.ax.legend(by_label.values(), by_label.keys())
        
        self.sc = MplCanvas(fig = plot.fig, axes=plot.ax)   
    
