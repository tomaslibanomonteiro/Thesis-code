import numpy as np
import pandas as pd
from pymoo.core.algorithm import Algorithm
from pymoo.core.callback import Callback
from pymoo.core.result import Result
from pymoo.optimize import minimize
from pymoo.indicators.hv import Hypervolume
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

from utils.debug import debug_print
from utils.defines import N_SEEDS_KEY, ALGO_KEY, PROB_KEY, N_EVAL_KEY, N_GEN_KEY

class MyCallback(Callback):

    def __init__(self) -> None:
        super().__init__()
        self.best = []
        self.n_eval = []
        self.n_gen = []

    def notify(self, algo: Algorithm):
        if algo.opt is not None and algo.pop is not None:
            feas = np.where(algo.opt.get("feasible"))[0]
            self.best.append(algo.pop.get("F")[feas])
            self.n_eval.append(algo.evaluator.n_eval)
            self.n_gen.append(algo.n_gen)

class SingleRunArgs():
    def __init__(self, prob_id: str, prob_object, algo_id: str, algo_object, pi_ids: list, pi_objects: list): 
        self.prob_id = prob_id
        self.prob_object = prob_object 
        self.algo_id = algo_id
        self.algo_object = algo_object
        self.pi_ids = pi_ids
        self.pi_object = pi_objects                
        
class RunThread(QThread):
    progressSignal = pyqtSignal(str, int)

    def __init__(self, single_run_args: list, term_id, term_object, n_seeds: int, moo: bool):
        super().__init__()
                
        self.n_seeds = n_seeds
        self.term_id = term_id
        self.term_object = term_object
        self.single_run_args_list = single_run_args
        self.moo = moo
        self.data = pd.DataFrame()
        self.run_counter = 0
        self.total_single_runs = len(single_run_args)*n_seeds
        self.canceled = False  

    def cancel(self):
        self.canceled = True    

    def run(self):
        #!
        import debugpy
        debugpy.debug_this_thread()
         
        for run_args in self.single_run_args_list:
            for seed in range(self.n_seeds):
                if self.canceled:
                    return
                self.progressUpdate(run_args.algo_id, run_args.prob_id, seed)
                res = self.single_run(run_args, seed, self.term_object)
                if res is not None:
                    self.data = self.update_data(run_args, res, res.algorithm.callback)
                
    def progressUpdate(self, algo_id: str, prob_id: str, seed: int):
        """Update the progress bar and the text in the status bar"""
        
        text = f"Running algo {algo_id} on problem {prob_id}, seed {seed}"
        percentage = self.run_counter/self.total_single_runs*100                
        self.run_counter += 1    
        self.progressSignal.emit(text, percentage)
        
        debug_print(f"{percentage:.0f}%  - ",text) #!
        
    def single_run(self, run_args: SingleRunArgs, seed: int, termination) -> Result:
        try:
            res = minimize(algorithm=run_args.algo_object,
                        problem=run_args.prob_object,
                        termination=termination,
                        seed=seed,
                        verbose=False,
                        save_history=False,
                        progress_bar=True,
                        callback=MyCallback())
        except Exception as e: 
            res = None
            self.canceled = True
            error_message = (f"Error while running {run_args.algo_id} on {run_args.prob_id}, seed {seed}:\n{e}"
                             "\nPlease Make sure the algorithm is compatible with the problem.")
            integer = -1
            self.progressSignal.emit(error_message, integer)
                
        return res

    def update_data(self, run_args: SingleRunArgs, res: Result, callback: MyCallback):
                
        data = self.data

        run_length = len(callback.n_eval)

        single_run = {N_SEEDS_KEY: [res.algorithm.seed] * run_length,
                      PROB_KEY: [run_args.prob_id] * run_length,
                      ALGO_KEY: [run_args.algo_id] * run_length,
                      N_EVAL_KEY: callback.n_eval,
                      N_GEN_KEY: callback.n_gen}
        
        # get the performance indicators values
        for pi_id, pi_object in zip(run_args.pi_ids, run_args.pi_object):
            if pi_id == "best_default":
                # get the float values in the callback.best list
                pi_data = [None if len(item) == 0 else float(item[0]) for item in callback.best]                    
            else:
                if isinstance(pi_object, Hypervolume): # invert the hypervolume values
                    pi_data = [-item for item in callback.best]
                else:
                    pi_data = [pi_object.do(pf) for pf in callback.best]
            
            # add the data to the data frame    
            single_run[pi_id] = pi_data
        
        single_run = pd.DataFrame(single_run)

        return pd.concat([data, single_run])
        
    def save_data(self, filename: str):
        self.data.to_csv(filename, index=False)
        
