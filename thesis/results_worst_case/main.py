####################################################################################################
######################## MODIFY to full path to the project folder #################################
full_path = r"C:\Users\tomas\OneDrive - Universidade de Lisboa\Desktop\Tese\Thesis-code"
####################################################################################################
####################################################################################################


def start(): 
    import pickle
    from utils.defines import ALGO_KEY, PROB_KEY, SAMP_KEY, CROSS_KEY
    with open(f'thesis/results_worst_case/moo_run_options.pickle', 'rb') as file:
        run_options = pickle.load(file) #@IgnoreException

    with open(f'thesis/results_worst_case/moo_parameters.pickle', 'rb') as file:
        parameters = pickle.load(file) #@IgnoreException
    
    from backend.defaults import Defaults
    def_parameters = Defaults(moo=True).parameters
    
    return {}, {}, run_options, parameters

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
    
    from thesis.results_worst_case.operators import InversionFlipMutation
    from backend.get import get_crossover
    crossover = get_crossover('none')
    
    algorithms = [ACO_NSGA2(crossover=crossover, mutation=InversionFlipMutation(only_flip=True)), 
                #   ACO_NSGA2()
                  ]
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
                verbose=True,
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