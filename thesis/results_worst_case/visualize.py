from matplotlib import pyplot as plt

def visualize(problem, x, fig=None, ax=None, show=True, label=True):
    with plt.style.context('ggplot'):

        if fig is None or ax is None:
            fig, ax = plt.subplots()

        # plot cities using scatter plot
        ax.scatter(problem.cities[:, 0], problem.cities[:, 1], s=250)
        if label:
            # annotate cities
            for i, c in enumerate(problem.cities):
                ax.annotate(str(i), xy=c, fontsize=10, ha="center", va="center", color="white")

        # plot the line on the path
        for i in range(len(x)):
            current = x[i]
            next_ = x[(i + 1) % len(x)]
            ax.plot(problem.cities[[current, next_], 0], problem.cities[[current, next_], 1], 'r--')

        fig.suptitle("Route length: %.4f" % problem.get_route_length(x))

        if show:
            fig.show()
