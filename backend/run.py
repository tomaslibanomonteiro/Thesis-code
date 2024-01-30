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
from utils.defines import N_SEEDS_KEY, ALGO_KEY, PROB_KEY, N_EVAL_KEY, N_GEN_KEY, RUN_ID_KEY

class MyCallback(Callback):

    def __init__(self, pi_ids:list, pi_objects:list):
        super().__init__()
        
        self.pi_ids = pi_ids
        self.data = {N_EVAL_KEY: [], N_GEN_KEY: []}
        for pi_id in pi_ids:
            self.data[pi_id] = []
        
        self.pi_objects = pi_objects

    def notify(self, algo: Algorithm):
        if algo.opt is None or algo.pop is None:
            return

        self.data[N_EVAL_KEY].append(algo.evaluator.n_eval)
        self.data[N_GEN_KEY].append(algo.n_gen)
        feas = np.where(algo.opt.get("feasible"))[0]
        best_sol = algo.pop.get("F")[feas]
                
        # get the performance indicators values
        for pi_id, pi_object in zip(self.pi_ids, self.pi_objects):
            pi = pi_object.do(best_sol)
            if isinstance(pi_object, Hypervolume): # invert the hypervolume for voting
                pi = -pi
            # add the data to the data frame    
            self.data[pi_id].append(pi)


class RunArgs():
    def __init__(self, prob_id: str, prob_object, algo_id: str, algo_object, pi_ids: list, pi_objects: list): 
        self.prob_id = prob_id
        self.prob_object = prob_object 
        self.algo_id = algo_id
        self.algo_object = algo_object
        self.pi_ids = pi_ids
        self.pi_objects = pi_objects                
        
class RunThread(QThread):
    progressSignal = pyqtSignal(str, int)

    def __init__(self, run_args_list:list, term_id, term_object, n_seeds:int, moo:bool, parameters:dict, run_options:dict):
        super().__init__()
        
        self.parameters = parameters
        self.run_options = run_options
        self.n_seeds = n_seeds
        self.term_id = term_id
        self.term_object = term_object
        self.run_args_list = run_args_list
        self.moo = moo
        self.data = pd.DataFrame()
        self.run_counter = 0
        self.total_runs = len(run_args_list)*n_seeds
        self.canceled = False  
        self.best_sol = {} # dictionary of the best solution(s) for each run_id to plot the pf

    def cancel(self):
        self.canceled = True    

    def run(self):
        #!
        import debugpy
        debugpy.debug_this_thread()
        run_id = 0
        for run_args in self.run_args_list:
            for seed in range(self.n_seeds):
                if self.canceled:
                    return
                self.progressUpdate(run_args.algo_id, run_args.prob_id, seed)
                res = self.singleRun(run_args, seed, self.term_object)
                self.updateData(run_args, res, seed, run_id, res.algorithm.callback)
                run_id += 1
                
    def singleRun(self, run_args: RunArgs, seed: int, termination) -> Result:
        try:
            res = minimize(algorithm=run_args.algo_object,
                        problem=run_args.prob_object,
                        termination=termination,
                        seed=seed,
                        verbose=False,
                        save_history=False,
                        progress_bar=True,
                        callback=MyCallback(run_args.pi_ids, run_args.pi_objects))
        except Exception as e: 
            res = None
            self.canceled = True
            error_message = (f"Error while running {run_args.algo_id} on {run_args.prob_id}, seed {seed}:\n{e}"
                             "\nPlease Make sure the algorithm is compatible with the problem.")
            self.progressSignal.emit(error_message, -1)
                
        return res

    def progressUpdate(self, algo_id: str, prob_id: str, seed: int):
        """Update the progress bar and the text in the status bar"""
        
        text = f"Running algo {algo_id} on problem {prob_id}, seed {seed}"
        percentage = self.run_counter/self.total_runs*100                
        self.run_counter += 1    
        self.progressSignal.emit(text, percentage)
        
        debug_print(f"{percentage:.0f}%  - ",text) #!
        
    def updateData(self, run_args: RunArgs, res: Result, seed:int, run_id:int, callback: MyCallback):
        
        if res is None:
            return
        
        run_length = len(callback.data[N_EVAL_KEY])

        single_run_data = {N_SEEDS_KEY: [seed] * run_length,
                           PROB_KEY: [run_args.prob_id] * run_length,
                           ALGO_KEY: [run_args.algo_id] * run_length, 
                           RUN_ID_KEY: [run_id] * run_length}
        
        single_run_data.update(callback.data)
        if self.data.empty:
            self.data = pd.DataFrame(single_run_data)
        else:
            self.data = pd.concat([self.data, pd.DataFrame(single_run_data)])
        
        best_sol = res.algorithm.opt.get("F")[np.where(res.algorithm.opt.get("feasible"))[0]]
        if len(best_sol) == 0:
            self.best_sol[run_id] = np.nan
        elif self.moo:
            self.best_sol[run_id] = best_sol
        else:
            self.best_sol[run_id] = best_sol[0][0]        
