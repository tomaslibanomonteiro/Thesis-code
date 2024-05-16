from pymoo.problems import get_problem
from matplotlib import pyplot as plt


for name in ["zdt1", "zdt2", "zdt3"]:
    problem = get_problem(name)
    pf = problem.pareto_front()
    plt.scatter(pf[:,0], pf[:,1], color="green", alpha=0.5)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.savefig(f"{name}_pareto.png")
    plt.close()