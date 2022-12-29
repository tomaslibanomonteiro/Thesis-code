import numpy as np
import pandas as pd
import time
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2 
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.indicators.igd import IGD
from pymoo.problems import get_problem
from matplotlib import pyplot as plt
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.core.callback import Callback
from pymoo.algorithms.soo.nonconvex.pso import PSO

# DEFINES
N_EVALS = 200
DEBUG_PRINT = True
VERBOSE = False
SAVE_HISTORY = False
PROB_NAMES = ['Rastrigin']

# PSO
POP_SIZE_LIST = [5, 10, 20]
W_LIST = [0.7]
C1_LIST = [0.7]
C2_LIST = [0.7]

# number of times the algorithm is run for each combination of parameters
N_SEEDS = 20

JUST_PLOT = False

################################### AUX FUNCTIONS ######################################
def debug_print(msg, debug_print):
    if debug_print:
        print(msg)

def print_pso(algo, algo_id, seed, debug_print):
    if not debug_print:
        return

    print(" algo name: ", algo.__class__.__name__, algo_id, "seed: ", seed)
    print("     Parameterers:  w=", algo.w, "  c1=", algo.c1, "  c2=", algo.c2, "  pop_size=", algo.pop_size)

################################### PLOTTING ######################################

def legendPlot(x, pm_name, prob, figname=None):
    plt.legend()
    plt.xlabel(x)
    plt.ylabel(pm_name)
    plt.title(prob)
    if figname:
        plt.savefig(figname)
    plt.clf()

def plotPM(data, each_plot = 'prob', plotting_mode = 'by_evals', save=True, pm_name='best'):
    """ Plot performance metric for each problem and algorithm. 
        each_plot can be 'prob', 'algo' or 'prob_algo' 
        plotting_mode can be 'by_evals' or 'by_time'
        pm_name can be 'IGD' or 'best'
        save is a boolean to save the plot or not"""

    if plotting_mode == 'by_evals':
        x = 'n_evals'
    elif plotting_mode == 'by_time':
        x = 'time'
    else:
        raise ValueError("plotting_mode must be 'by_evals' or 'by_time'")

    # average over runs with different seeds for each problem and algorithm
    data = data.groupby(['prob', 'algo', 'n_evals']).mean().reset_index()

    if each_plot == 'prob':        
        for prob in data['prob'].unique():
            for algo in data['algo'].unique():
                df = data[(data['prob'] == prob) & (data['algo'] == algo)]
                # set label with algo name and parameters with 2 decimal places each
                
                label = algo.split('_')[0] + ' w=' + str(round(df['w'].iloc[0], 2)) + ' c1=' + str(round(df['c1'].iloc[0], 2)) + ' c2=' + str(round(df['c2'].iloc[0], 2)) + ' pop_size=' + str(df['pop_size'].iloc[0])
                plt.plot(df[x], df[pm_name], label=label)
            legendPlot(x, pm_name, prob, 'figures/prob_' + prob + '-pm_' + pm_name +'-x=' + x + '.png')

    elif each_plot == 'algo':
        for algo in data['algo'].unique():
            for prob in data['prob'].unique():
                label = algo.split('_')[0] + ' w=' + str(round(df['w'].iloc[0], 2)) + ' c1=' + str(round(df['c1'].iloc[0], 2)) + ' c2=' + str(round(df['c2'].iloc[0], 2)) + ' pop_size=' + str(df['pop_size'].iloc[0])
                plt.plot(df[x], df[pm_name], label=label)
            legendPlot(x, pm_name, algo, 'figures/algo_' + algo + '-pm_' + pm_name +'-x=' + x + '.png')

    elif each_plot == 'prob_algo':
        for prob in data['prob'].unique():
            for algo in data['algo'].unique():
                df = data[(data['prob'] == prob) & (data['algo'] == algo)] 
                label = algo.split('_')[0] + ' w=' + str(round(df['w'].iloc[0], 2)) + ' c1=' + str(round(df['c1'].iloc[0], 2)) + ' c2=' + str(round(df['c2'].iloc[0], 2)) + ' pop_size=' + str(df['pop_size'].iloc[0])
                plt.plot(df[x], df[pm_name], label=label)
                legendPlot(x, pm_name, prob, 'figures/prob_' + prob + '-pm_' + pm_name +'-x=' + x + '.png')

    else:
        raise ValueError("each_plot must be 'by_problem', 'by_algo' or 'all_plots'")

################################### DATA HANDLING ######################################

def update_data(data, res, algo_id, run_id, seed):

    # get data from callback
    n_evals = res.algorithm.callback.n_evals
    pm = res.algorithm.callback.best
    time = res.algorithm.callback.time
    time = [t - time[0] for t in time]

    # get data in 
    algo = [res.algorithm.__class__.__name__ + '_' + str(algo_id)] * len(pm)
    pop_size = [res.algorithm.pop_size] * len(pm)
    w = [res.algorithm.w] * len(pm)
    c1 = [res.algorithm.c1] * len(pm)
    c2 = [res.algorithm.c2] * len(pm)
    prob = [res.problem.__class__.__name__] * len(pm)
    run_id = [run_id] * len(pm)
    seed = [seed] * len(pm)

    # create data frame 
    run_data = pd.DataFrame({'run_id': run_id, 'prob': prob, 'algo': algo, 'seed': seed, 'pop_size': pop_size, 
                                    'w': w, 'c1': c1, 'c2': c2, 'best': pm, 'n_evals': n_evals, 'time': time})
    
    return pd.concat([data, run_data])

################################### PROBLEM ######################################

def set_prob_list(prob_names):
    prob_list = []
    for prob_name in prob_names:
        prob_list.append(get_problem(prob_name))

    return prob_list

################################### ALGORITHM ######################################
class MyCallback(Callback):

    def __init__(self) -> None:
        super().__init__()
        self.best = []
        self.n_evals = []
        self.time = []

    def notify(self, algo):
        feas = np.where(algo.opt.get("feasible"))[0]
        self.best.append(algo.pop.get("F")[feas][0][0])
        self.n_evals.append(algo.evaluator.n_eval)
        self.time.append(time.perf_counter())

def set_pso_list():

    parameters = [(pop_size, w, c1, c2) for pop_size in POP_SIZE_LIST for w in W_LIST for c1 in C1_LIST for c2 in C2_LIST]
    
    pso_list = []
    for pop_size, w, c1, c2 in parameters:
        pso = PSO(pop_size=pop_size, w=w, c1=c1, c2=c2, adaptative=False, pertube_best=False)
        pso_list.append(pso)

    return pso_list

def main():
    data = pd.DataFrame()   
    run_id = 0
    for prob in set_prob_list(PROB_NAMES):
        debug_print("prob: " + prob.__class__.__name__, DEBUG_PRINT)
        for algo_id, algo in enumerate(set_pso_list()):  
            for seed in range(N_SEEDS):
                    
                print_pso(algo, algo_id, seed, DEBUG_PRINT)
                
                res = minimize(prob,
                            algo,
                            ('n_evals', N_EVALS),
                            seed=seed,
                            verbose=VERBOSE,
                            save_history=SAVE_HISTORY,
                            callback=MyCallback())

                data = update_data(data, res, algo_id, run_id, seed)
                run_id += 1

    # save data
    data.to_csv('data.csv', index=False)

    # plot data
    plotPM(data, each_plot = 'prob', plotting_mode = 'by_evals', save=True)
    plotPM(data, each_plot = 'prob', plotting_mode = 'by_time', save=True)

def just_plot():
    data = pd.read_csv('data.csv')
    plotPM(data, each_plot = 'prob', plotting_mode = 'by_evals', save=True)
    plotPM(data, each_plot = 'prob', plotting_mode = 'by_time', save=True)

if __name__ == '__main__':
    if JUST_PLOT:
        just_plot()
    else:
        main()


