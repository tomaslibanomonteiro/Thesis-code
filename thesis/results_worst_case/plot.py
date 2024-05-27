from matplotlib import pyplot as plt
from thesis.results_worst_case.problem import MultiObjectiveMixedTSP
import numpy as np

from frontend.plotting import QPlot, MplCanvas
from utils.utils import MyMessageBox
class TSPplot(QPlot):
    def __init__(self, f1_over_f2=1, plot_best='cost', labels=True):
        super().__init__("TSP Plot", True)
        self.f1_over_f2 = f1_over_f2
        self.plot_best = plot_best
        self.label = labels
    
    def createCanvas(self):
        if len(self.algos_dict) != 1 or len(self.run_types) != 1:
            MyMessageBox("Only one algorithm and run type can be selected for this plot. Plotting the ones selected first.")
        algo_id = list(self.algos_dict.keys())[0]
        run_type = list(self.run_types)[0]
        seed = self.getSeedFromIds(self.prob_id, algo_id, run_type)
        best_gen = self.run_thread.best_gen[(self.prob_id, algo_id, seed)]
        X, F = best_gen['X'], best_gen['F']
        
        fig, ax = plotTSP(self.prob_object, X, F, self.label, self.plot_best, self.f1_over_f2, ret=True)
        
        return MplCanvas(fig = fig, axes=ax)   

def plotTSP(prob: MultiObjectiveMixedTSP, X, F, label=True, plot_best='cost', f1_over_f2=1, ret=False):
    
    plot_best = plot_best.lower()
    if plot_best == 'cost':
        # get the path with the lowest cost
        best_idx = np.argmin(F[:, 1])
        x, f = X[best_idx, :], F[best_idx, :]
        title = "Best Cost:"
    elif plot_best == 'time':
        # get the path with the lowest time
        best_idx = np.argmin(F[:, 0])
        x, f = X[best_idx, :], F[best_idx, :]
        title = "Best Time:"
    elif plot_best == 'ratio': 
        # get the path with the lowest time/cost ratio
        normalizedF1 = F[:, 0] / np.max(F[:, 0])
        normalizedF2 = F[:, 1] / np.max(F[:, 1])
        best_idx = np.argmin(f1_over_f2 * normalizedF1 + normalizedF2)
        x = X[best_idx, :]
        f = F[best_idx, :]
        title = "Best Time/Cost Ratio:"
    else:
        raise ValueError("plot_best must be one of 'cost', 'time' or 'ratio'")
    
    with plt.style.context('ggplot'):
        
        cities, trp_options, path, trp = prob.cities_coord, prob.transport_options, x[:prob.n_cities], x[prob.n_cities:] 
        
        n_trp = len(trp_options)
        trp_colors = plt.cm.get_cmap('tab20', n_trp)
        
        fig, ax = plt.subplots()  # Create a new figure for each x

        # plot the line on the path
        for i in range(len(path)):
            current = path[i]
            next_ = path[(i + 1) % len(path)]
            ax.plot(cities[[current, next_], 0], cities[[current, next_], 1], color=trp_colors(trp[i]), label=trp_options[trp[i]])

        # plot cities using scatter plot
        ax.scatter(cities[:, 0], cities[:, 1], s=250, zorder=2)  # Add zorder parameter to bring scatter plot to front
        if label:
            # annotate cities
            for i, c in enumerate(cities):
                ax.annotate(str(i), xy=c, fontsize=10, ha="center", va="center", color="white")

        numbers = int(np.round(f[0])), int(np.round(f[1]))
        fig.suptitle(f"{title} {numbers} (Time/Cost)")

        handles, labels = ax.get_legend_handles_labels()
        # Using dict to remove duplicates, preserving the order
        by_label = dict(zip(labels, handles))
        if handles != {}:
            ax.legend(by_label.values(), by_label.keys())

        if ret:
            return fig, ax
    
    plt.show()
    
if __name__ == '__main__':
    from thesis.results_worst_case.main import main
    main()