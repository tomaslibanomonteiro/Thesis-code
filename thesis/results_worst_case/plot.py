from matplotlib import pyplot as plt
from problem import MultiObjectiveMixedTSP
from pymoo.visualization.scatter import Scatter
import numpy as np

def plotTSP(prob: MultiObjectiveMixedTSP, X, F, label=True):
    
    # Create the scatter plot
    Scatter(labels=['Time', 'Cost']).add(F).show()
    
    with plt.style.context('ggplot'):
        
        for x, f in zip(X, F):
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

            fig.suptitle("Time/Cost: " + str(np.round(f)))

            handles, labels = ax.get_legend_handles_labels()
            # Using dict to remove duplicates, preserving the order
            by_label = dict(zip(labels, handles))
            if handles != {}:
                ax.legend(by_label.values(), by_label.keys())

            plt.show(block=False)  # Display the figure without blocking the execution of the program

    plt.show()  # Keep the program running until all figures are closed
    
    
if __name__ == '__main__':
    from main import main
    main()