import pandas as pd
from pymoo.optimize import minimize
from pymoo.core.callback import Callback
import pandas as pd
from pymoo.indicators.igd import IGD
from input.input import Input
from input.input import RunArgs
from utils.debug import debug_print
from pymoo.core.algorithm import Algorithm
import numpy as np
from pymoo.core.result import Result
from utils.get import get_performance_indicator

################################### ALGORITHM ######################################
class MyCallback(Callback):

    def __init__(self) -> None:
        super().__init__()
        self.best = []
        self.n_evals = []
        self.n_gen = []

    def notify(self, algo: Algorithm):
        feas = np.where(algo.opt.get("feasible"))[0]
        self.best.append(algo.pop.get("F")[feas])
        self.n_evals.append(algo.evaluator.n_eval)
        self.n_gen.append(algo.n_gen)

def update_data(data, res: Result, callback: MyCallback, run_args: RunArgs):

    PM_list = run_args.PM
    
    # get problem and algorithm name
    algo = res.algorithm.__class__.__name__ 
    prob = res.problem.__class__.__name__ 
    seed = res.algorithm.seed
    run_id = run_args.run_id
    
    # get n_evals, n_gen, pareto front and PM values from the result    
    n_evals = callback.n_evals
    n_gen = callback.n_gen
        
    if res.problem.n_obj == 1:
        # if the problem is single objective, the best is a list of the best solutions at each generation
        pm1 = callback.best
        pm2 = [""] * len(pm1)
        pm3 = [""] * len(pm1)
    else:
        true_pf = res.problem.pareto_front()
            
        metric1 = get_performance_indicator(PM_list[0], true_pf)
        pm1 = [metric1.do(pf) for pf in callback.best]
        
        if len(PM_list) > 1:
            metric2 = get_performance_indicator(PM_list[1], true_pf)
            pm2 = [metric2.do(pf) for pf in callback.best]
        else:
            pm2 = [""] * len(pm1)
        
        if len(PM_list) > 2:
            metric3 = get_performance_indicator(PM_list[2], true_pf)
            pm3 = [metric3.do(pf) for pf in callback.best]
        else:
            pm3 = [""] * len(pm1)
            
    # create data frame with columns ['run_id', 'seed', 'Problem','Algorithm', 'n_evals', 'n_gen', 'PM1', 'PM2', 'PM3']
    run_data = pd.DataFrame({'run_id': [run_id] * len(n_evals),
                             'seed': [seed] * len(n_evals),
                             'Problem': [prob] * len(n_evals),
                             'Algorithm': [algo] * len(n_evals),
                             'n_evals': n_evals,
                             'n_gen': n_gen,
                             'PM1': pm1,
                             'PM2': pm2,
                             'PM3': pm3})
    
    return pd.concat([data, run_data])

class Run():
    def __init__(self, input_data: Input):
        self.data = pd.DataFrame()
        self.input_data = input_data
        self.run()
        
    def run(self):
        for run_args in self.input_data.run_args_list:
            self.run_cycle(run_args)
    
    def run_cycle(self, run_args: RunArgs):
        for seed in range(run_args.n_seeds):
                res = minimize(run_args.problem,
                        run_args.algorithm,
                        termination=run_args.termination,
                        seed=seed,
                        verbose=False,
                        save_history=False,
                        progress_bar=True,
                        callback=MyCallback())
                self.data = update_data(self.data, res, res.algorithm.callback, run_args)
                debug_print(res.problem.__class__.__name__, res.algorithm.__class__.__name__, seed)
        return        