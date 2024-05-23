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
    from pymoo.core.crossover import Crossover
    from thesis.results_worst_case.problem import RandomMultiMixedTSP
    from thesis.results_worst_case.algorithm import PermutationNSGA2, ACO_NSGA2
    from thesis.results_worst_case.plot import plotTSP
    from utils.useful_classes import minusHypervolume

    algorithms = [PermutationNSGA2(), ACO_NSGA2(), ACO_NSGA2(crossover=Crossover(n_parents=2, n_offsprings=2, prob=0.0))]
    # termination = DefaultMultiObjectiveTermination()
    termination = ("n_gen", 100)
    problem = RandomMultiMixedTSP()

    for algorithm in algorithms:
        hv_values = []
        for seed in range(5):
            res = minimize(
                problem,
                algorithm,
                termination,
                seed=seed,
            )
            
            hv = minusHypervolume(pf=problem.pareto_front())
            hv_values.append(hv.do(res.F))
            print(f"seed: {seed}, hv: {hv.do(res.F)}")
            # # Create the scatter plot
            # Scatter(labels=['Time', 'Cost']).add(res.F).show()

            # for plot_best in ['cost', 'time', 'ratio']:
            #     plotTSP(problem, res.X, res.F, plot_best=plot_best)

            # from matplotlib import pyplot as plt
            # plt.show()
        
    
        print(f"algorithm: {algorithm}, hv avg: {sum(hv_values)/len(hv_values)}")
    
if __name__ == '__main__':
    main()