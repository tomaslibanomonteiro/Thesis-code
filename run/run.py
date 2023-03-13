import numpy as np
import pandas as pd
import time
from pymoo.optimize import minimize
from pymoo.indicators.igd import IGD
from pymoo.core.callback import Callback
import pandas as pd
from pymoo.indicators.igd import IGD
from input.input import Input


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

def update_data(data, res):

    # get problem and algorithm name
    algo = res.algorithm.__class__.__name__
    prob = res.problem.__class__.__name__
    
    # get data from callback
    n_evals = res.algorithm.callback.n_evals
    pareto_hist = res.algorithm.callback.pareto_hist
    time = res.algorithm.callback.time
    time = [t - time[0] for t in time]
    true_pf = res.problem.pareto_front()
    metric = IGD(true_pf, zero_to_one=True)
    igd = [metric.do(pf) for pf in pareto_hist]

    # create data frame 
    prob_algo_data = pd.DataFrame([[prob] * len(igd), [algo] * len(igd), n_evals, time, igd]).transpose()
    prob_algo_data.columns = ['Problem','Algorithm', 'n_evals', 'time', 'IGD']
    
    return pd.concat([data, prob_algo_data])

class Run():
    def __init__(self, input_data: Input):
        self.data = pd.DataFrame()
        self.input_data = input_data
        self.run()
        
    def run(self):
        for prob in self.input_data.probs:
            for algo in self.input_data.algos:
                for seed in range(self.input_data.n_seeds):
                    res = minimize(prob,
                            algo,
                            ('n_gen', self.input_data.n_gen),
                            seed=seed,
                            verbose=False,
                            save_history=True,
                            callback=MyCallback())
                    self.data = update_data(self.data, res)
                    print(res.problem.__class__.__name__, res.algorithm.__class__.__name__, seed)
        return        
    