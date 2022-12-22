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
N_GEN = 100
DEBUG_PRINT = True
VERBOSE = False
SAVE_HISTORY = False
PROB_NAMES = ['Rastrigin', 'Ackley', 'Griewank']
ALGO_NAMES = ['PSO']

OTHER_MAIN = True

################################### AUX FUNCTIONS ######################################
def debug_print(msg):
    if DEBUG_PRINT:
        print(msg)

def get_algo(algo_name, problem):
        
    n_dim = problem.n_obj
    ref_dirs = get_reference_directions("das-dennis", n_dim, n_partitions= 4*n_dim)
    pop_size = len(ref_dirs)
    if algo_name == 'NSGA2':
        return NSGA2(pop_size=pop_size)
    elif algo_name == 'NSGA3':
        return NSGA3(ref_dirs)
    elif algo_name == 'MOEAD':
        return MOEAD(ref_dirs)

################################### DATA HANDLING ######################################
def plotIND(data, ind = 'IGD', each_plot = 'prob', plotting_mode = 'by_evals', save=True):
    """ Plot performance indicator for each problem and algorithm. 
        each_plot can be 'prob', 'algo' or 'prob_algo' 
        plotting_mode can be 'by_evals' or 'by_time'
        ind can be 'IGD' or ... 
        save is a boolean to save the plot or not"""

    if plotting_mode == 'by_evals':
        x = 'n_evals'
    elif plotting_mode == 'by_time':
        x = 'time'
    else:
        raise ValueError("plotting_mode must be 'by_evals' or 'by_time'")

    if each_plot == 'prob':
        for prob in data['Problem'].unique():
            for algo in data['Algorithm'].unique():
                df = data[(data['Problem'] == prob) & (data['Algorithm'] == algo)] 
                plt.plot(df[x], df[ind], label=algo)
            plt.legend()
            plt.xlabel(x)
            plt.ylabel(ind)
            plt.title(prob)
            if save:
                plt.savefig('figures/prob_' + prob + '-ind_' + ind +'-x=' + x + '.png')
            plt.clf()
    elif each_plot == 'algo':
        for algo in data['Algorithm'].unique():
            for prob in data['Problem'].unique():
                df = data[(data['Problem'] == prob) & (data['Algorithm'] == algo)] 
                plt.plot(df[x], df[ind], label=prob)
            plt.legend()
            plt.xlabel(x)
            plt.ylabel(ind)
            plt.title(algo)
            if save:
                plt.savefig('figures/algo_' + algo + '-ind_' + ind +'-x=' + x + '.png')
            plt.clf()
    elif each_plot == 'prob_algo':
        for prob in data['Problem'].unique():
            for algo in data['Algorithm'].unique():
                df = data[(data['Problem'] == prob) & (data['Algorithm'] == algo)] 
                plt.plot(df[x], df[ind], label=algo)
                plt.legend()
                plt.xlabel(x)
                plt.ylabel(ind)
                plt.title(prob + ' - ' + algo)
                if save:
                    plt.savefig('figures/prob_' + prob + '-algo_' + algo + '-ind_' + ind +'-x=' + x + '.png')
                plt.clf()
    else:
        raise ValueError("each_plot must be 'by_problem', 'by_algo' or 'all_plots'")

def update_data(data, res, ind='IGD'):

    # get problem and algorithm name
    algo = res.algorithm.__class__.__name__
    prob = res.problem.__class__.__name__
    
    # get data from callback
    n_evals = res.algorithm.callback.n_evals
    pareto_hist = res.algorithm.callback.pareto_hist
    time = res.algorithm.callback.time
    time = [t - time[0] for t in time]
    true_pf = res.problem.pareto_front()

    if ind == 'IGD':
        # compute IGD
        metric = IGD(true_pf, zero_to_one=True)
        igd = [metric.do(pf) for pf in pareto_hist]

    # create data frame 
    prob_algo_data = pd.DataFrame([[prob] * len(ind), [algo] * len(ind), n_evals, time, ind]).transpose()
    prob_algo_data.columns = ['Problem','Algorithm', 'n_evals', 'time', ind ]
    
    return pd.concat([data, prob_algo_data])

################################### ALGORITHM ######################################
class MyCallback(Callback):

    def __init__(self) -> None:
        super().__init__()
        self.pareto_hist = []
        self.n_evals = []
        self.time = []

    def notify(self, algo):
        feas = np.where(algo.opt.get("feasible"))[0]
        self.pareto_hist.append(algo.pop.get("F")[feas])
        self.n_evals.append(algo.evaluator.n_eval)
        self.time.append(time.perf_counter())

def main():
    data = pd.DataFrame()   
    for prob_name in PROB_NAMES:
        debug_print("Problem: " + prob_name)
        for algo_name in ALGO_NAMES:  
            debug_print("   Algorithm: " + algo_name)
            prob = get_problem(prob_name)
            algo = get_algo(algo_name, prob)
            res = minimize(prob,
                        algo,
                        ('n_gen', N_GEN),
                        seed=1,
                        verbose=VERBOSE,
                        save_history=SAVE_HISTORY,
                        callback=MyCallback())
            data = update_data(data, res)
    # save data
    data.to_csv('data.csv', index=False)

    # plot data
    plotIND(data, each_plot = 'prob', plotting_mode = 'by_evals', save=True)
    plotIND(data, each_plot = 'prob', plotting_mode = 'by_time', save=True)

def other_main():
    data = pd.read_csv('data.csv')
    plotIND(data, each_plot = 'prob', plotting_mode = 'by_evals', save=True)
    plotIND(data, each_plot = 'prob', plotting_mode = 'by_time', save=True)

if __name__ == '__main__':
    if OTHER_MAIN:
        other_main()
    else:
        main()


