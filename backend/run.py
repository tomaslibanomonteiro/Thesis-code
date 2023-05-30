import pandas as pd
from pymoo.optimize import minimize
from pymoo.core.callback import Callback
import pandas as pd
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
        if algo.opt is not None and algo.pop is not None:
            feas = np.where(algo.opt.get("feasible"))[0]
            self.best.append(algo.pop.get("F")[feas])
            self.n_evals.append(algo.evaluator.n_eval)
            self.n_gen.append(algo.n_gen)

class RunArgs():
    def __init__(self, prob_id: str, prob_object, algo_id: str, algo_object, pi_id: str, pi_object): 
        self.prob_id = prob_id
        self.prob_object = prob_object
        self.algo_id = algo_id
        self.algo_object = algo_object
        self.pi_id = pi_id
        self.pi_object = pi_object                

class Run():
    def __init__(self, prob_ids, prob_objects, algo_ids, algo_objects, pi_ids, pi_objects, term_id, term_object, n_seeds: int):
        self.n_seeds = n_seeds
        self.term_id = term_id
        self.term_object = term_object
        self.run_args = self.getRunArgs(prob_ids, prob_objects, algo_ids, algo_objects, pi_ids, pi_objects)
        self.data = pd.DataFrame()

    def getRunArgs(self, prob_ids: str, prob_objects, algo_ids: str, algo_objects, pi_ids: str, pi_objects):
        run_args = []
        for prob_id, prob_object, pi_id, pi_object in zip(prob_ids, prob_objects, pi_ids, pi_objects):
            for algo_id, algo_object in zip(algo_ids, algo_objects):
                run_args.append(RunArgs(prob_id, prob_object, algo_id, algo_object, pi_id, pi_object))
                
        return run_args
            
    def run(self):
        for run_id, run_args in enumerate(self.run_args):
            for seed in range(self.n_seeds):  # type: ignore
                self.single_run(run_args, seed, self.term_object, run_id)    
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
                        'seed': [res.algorithm.seed] * run_lenght,  # type: ignore
                        'problem_id': [run_args.prob_id] * run_lenght,
                        'algorithm_id': [run_args.algo_id] * run_lenght,
                        'n_eval': callback.n_evals,
                        'n_gen': callback.n_gen}
        
        # get the performance indicators values
        # for pi_id, pi in run_args.pi_dict.items():
        #     if pi_id == "best":
        #         pi_data = callback.best
        #     else:
        #         pi_data = [pi.do(pf) for pf in callback.best]
        
        pi_id = "best"
        pi_data = callback.best
        # add the data to the data frame    
        single_run[pi_id] = pi_data
        
        # create data frame with columns
        single_run = pd.DataFrame(single_run)
    
        return pd.concat([data, single_run])
    
    def printData(self):
        print(self.data)