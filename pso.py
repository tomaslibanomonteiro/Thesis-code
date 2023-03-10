import numpy as np
import pandas as pd
import time
from pymoo.optimize import minimize
from pymoo.problems import get_problem
from matplotlib import pyplot as plt
from pymoo.core.callback import Callback
from pymoo.algorithms.soo.nonconvex.pso import PSO

# DEBUG AND PLOTTING
JUST_PLOT = False # if True, just plot the data
DEBUG_PRINT = True # if True, print info about the optimization
LABEL_HYPERPARAMS = False # if True, label the plot with the hyperparameters
FIG_NAME = 'pso' # name of the figure

# PROB
PROB_NAMES = ['Rastrigin', 'Griewank', 'Ackley', 'Rosenbrock']

# PSO
POP_SIZE_LIST = [5, 10]
ADAPTATIVE = False # if True, w, c1, c2 are updated during the optimization
W_LIST = [0.4, 0.9]
C1_LIST = [2]
C2_LIST = [2]

# SOLVER
N_SEEDS = 3 # number of seeds for each problem/algo combination
N_EVALS = 400 # number of function evaluations until the optimization stops
VERBOSE = False # print info about the optimization
SAVE_HISTORY = False # save history of the optimization

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
def setLabel(algo, df, label_hyperparams = False, txt_name=None):
    """ Set label for the plot """

    # write labels to txt file
    if txt_name is not None:
        with open(txt_name, 'a') as f:
            f.write(algo + ' w=' + str(round(df['w'].iloc[0], 2)) + ' c1=' + str(round(df['c1'].iloc[0], 2)) + ' c2=' + str(round(df['c2'].iloc[0], 2)) + ' pop_size=' + str(int(df['pop_size'].iloc[0])) + '\n')
        
    if label_hyperparams:
        return algo + ' w=' + str(round(df['w'].iloc[0], 2)) + ' c1=' + str(round(df['c1'].iloc[0], 2)) + ' c2=' + str(round(df['c2'].iloc[0], 2)) + ' pop_size=' + str(int(df['pop_size'].iloc[0]))
    else:
        return str(algo)

def legendPlot(x=None, y=None, title=None, figname=None, save=True):
    plt.legend()
    if x is not None:
        plt.xlabel(x)
    if y is not None:
        plt.ylabel(y)
    if title is not None:
        plt.title(title)
    if save is True and figname is not None:
        plt.savefig(figname)
    plt.clf()

def plotPM(data, save=True):
    """ Plot performance metric for each problem and algorithm. 
        save is a boolean to save the plot or not"""

    # average over runs with different seeds for each problem and algorithm
    data = data.groupby(['prob', 'algo', 'n_evals']).mean().reset_index()

    for prob in data['prob'].unique():
        for algo in data['algo'].unique():
            
            # get data for each problem and algorithm and plot it  
            df = data[(data['prob'] == prob) & (data['algo'] == algo)]
            plt.plot(df['n_evals'], df['best'], label=setLabel(algo, df, LABEL_HYPERPARAMS, 'figures/'+ FIG_NAME+'.txt' ))

        # legend and save plot 
        if LABEL_HYPERPARAMS:
            figname = 'figures/' + FIG_NAME + '_' + prob + '_hyperparams.png'
        else:
            figname = 'figures/' + FIG_NAME + '_' + prob + '.png'
        legendPlot(x='Function evaluations', y='Best Solution Found' , title=prob, figname=figname, save=save)

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

################################### GET PROB AND ALGO ######################################
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

def set_prob_list(prob_names):
    prob_list = []
    for prob_name in prob_names:
        prob_list.append(get_problem(prob_name))

    return prob_list

def set_pso_list():

    parameters = [(pop_size, w, c1, c2) for pop_size in POP_SIZE_LIST for w in W_LIST for c1 in C1_LIST for c2 in C2_LIST]
    
    pso_list = []
    for pop_size, w, c1, c2 in parameters:
        pso = PSO(pop_size=pop_size, w=w, c1=c1, c2=c2, adaptive=ADAPTATIVE, pertube_best=False)
        pso_list.append(pso)

    return pso_list

################################### MAIN ######################################

def main():
    # clear txt file
    with open('figures/'+ FIG_NAME+'.txt', 'w') as f:
        f.truncate(0)

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
    plotPM(data, save=True)

def just_plot():
    data = pd.read_csv('data.csv')
    plotPM(data, save=True)

if __name__ == '__main__':
    if JUST_PLOT:
        just_plot()
    else:
        main()


