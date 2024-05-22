####################################################################################################
######################## MODIFY to full path to the project folder #################################
full_path = r"C:\Users\tomas\OneDrive - Universidade de Lisboa\Desktop\Tese\Thesis-code"
####################################################################################################
####################################################################################################

def main():

    import sys
    sys.path.insert(1, full_path)
    from pymoo.optimize import minimize
    from pymoo.termination.default import DefaultMultiObjectiveTermination
    from pymoo.visualization.scatter import Scatter

    from thesis.results_worst_case.problem import RandomMultiMixedTSP
    from thesis.results_worst_case.algorithm import PermutationNSGA2
    from thesis.results_worst_case.plot import plotTSP
    from utils.useful_classes import minusHypervolume

    algorithm = PermutationNSGA2()
    termination = DefaultMultiObjectiveTermination()
    # termination = ("n_gen", 10)
    problem = RandomMultiMixedTSP()

    res = minimize(
        problem,
        algorithm,
        termination,
        seed=1,
    )
    
    hv = minusHypervolume(pf=problem.pareto_front())
    hv_value = hv.do(res.F)
    
    print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))
    print("Hypervolume: %s" % hv_value)
    
    # Create the scatter plot
    Scatter(labels=['Time', 'Cost']).add(res.F).show()
    
    for plot_best in ['cost', 'time', 'ratio']:
        plotTSP(problem, res.X, res.F, plot_best=plot_best)
    
    from matplotlib import pyplot as plt
    plt.show()
    input()
    
if __name__ == '__main__':
    main()