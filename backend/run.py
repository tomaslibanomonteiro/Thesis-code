import pandas as pd
from pymoo.optimize import minimize
from pymoo.core.callback import Callback
import pandas as pd
from input import Input, RunArgs
from utils.debug import debug_print
from pymoo.core.algorithm import Algorithm
import numpy as np
from pymoo.core.result import Result

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

class Run():
    def __init__(self, input: Input): 
        self.data = pd.DataFrame()
        self.run(input)
            
    def run(self, input: Input):
        for run_id, run_args in enumerate(input.run_args_list):
            for seed in range(input.n_seeds):
                self.single_run(run_args, seed, input.term_object, run_id)    

                debug_print(run_id, run_args.algo_id, run_args.prob_id, seed)

    def single_run(self, run_args: RunArgs, seed: int, termination, run_id: int):
        res = minimize( algorithm=run_args.algo_object,
                        problem=run_args.prob_object,
                        termination = termination,
                        seed=seed,
                        verbose=False,
                        save_history=False,
                        progress_bar=True,
                        callback=MyCallback())

        # update data with the result of the run
        self.data = self.update_data(run_args, res, res.algorithm.callback, run_id)                      
                    
    def update_data(self, run_args: RunArgs, res: Result, callback: MyCallback, run_id: int):

        data = self.data
        
        run_lenght = len(callback.n_evals)
            
        single_run = {  'run_id': [run_id] * run_lenght,
                        'seed': [res.algorithm.seed] * run_lenght,
                        'problem_id': [run_args.prob_id] * run_lenght,
                        'algorithm_id': [run_args.algo_id] * run_lenght,
                        'n_eval': callback.n_evals,
                        'n_gen': callback.n_gen}
        
        # get the performance indicators values
        for pi_id, pi in run_args.pi_dict.items():
            if pi_id == "best":
                pi_data = callback.best
            else:
                pi_data = [pi.do(pf) for pf in callback.best]
            # add the data to the data frame    
            single_run[pi_id] = pi_data
        
        # create data frame with columns ['run_id', 'seed', 'Problem','Algorithm', 'n_evals', 'n_gen', 'PM1', 'PM2', 'PM3']
        single_run = pd.DataFrame(single_run)
    
        return pd.concat([data, single_run])
 