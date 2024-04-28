import numpy as np
import pandas as pd

from pymoo.core.algorithm import Algorithm
from pymoo.core.callback import Callback
from pymoo.core.result import Result
from pymoo.optimize import minimize
from pymoo.indicators.hv import Hypervolume

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

from utils.utils import debug_print
from utils.defines import SEEDS_KEY, ALGO_KEY, PROB_KEY, N_EVAL_KEY, N_GEN_KEY

class MyCallback(Callback):
    def __init__(self, pi_ids:list, pi_objects:list):
        super().__init__()
        
        self.pi_ids = pi_ids
        self.data = {N_EVAL_KEY: [], N_GEN_KEY: []}
        for pi_id in pi_ids:
            self.data[pi_id] = []
        
        self.pi_objects = pi_objects

    def notify(self, algo: Algorithm):
        if algo.opt is None:
            return

        self.data[N_EVAL_KEY].append(algo.evaluator.n_eval)
        self.data[N_GEN_KEY].append(algo.n_gen)
    
        feas = np.where(algo.pop.get("feasible"))[0] #! fica assim?
        algo_pop = algo.pop.get("F")[feas]
        from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
        non_dom_pop_idx = NonDominatedSorting().do(algo_pop, only_non_dominated_front=True)
        best_sol = algo_pop[non_dom_pop_idx] 
                
        # get the performance indicators values
        for pi_id, pi_object in zip(self.pi_ids, self.pi_objects):
            pi = pi_object.do(best_sol)
            if isinstance(pi_object, Hypervolume): # invert the hypervolume for voting
                pi = -pi
            # add the data to the data frame    
            self.data[pi_id].append(pi)


class RunArgs():
    def __init__(self, prob_id, prob_object, algo_id, algo_object, pi_ids, pi_objects, term_object):
        self.prob_id = prob_id
        self.prob_object = prob_object 
        self.algo_id = algo_id
        self.algo_object = algo_object
        self.pi_ids = pi_ids
        self.pi_objects = pi_objects
        self.term_object = term_object                
        
class RunThread(QThread):
    """
        A class that extends QThread to run the optimization process in a separate thread,
        calling the minimize function from pymoo.

        It emits a signal to update the progress bar and the status bar.
        The run can be canceled by calling the cancel method.
        
        AFTER RUN:
        -----------
        self.data
        -----------
        
        stores the data from all runs in a pandas DataFrame with structure:
        number of seeds | algorithm name | problem name | number of evaluations | number of generations | performance indicators values  
        
        -----------
        self.best_gen
        -----------
        
        It stores the last generation of solutions and the best solution so far, depending on the problem type:
        
        If SOO, the format is:
        (problem name, algorithm name, seed): 
        -> [solution coordinates in decision space, solution value in objective space]
        
        so that the Fitness Landscape can be plotted later.
        
        If MOO, the format is:
        (problem name, algorithm name, seed):
        -> [objective values of the best pareto set]
    """
    progressSignal = pyqtSignal(str, int)
    
    def __init__(self, run_args_list:list, term_id, n_seeds:int, moo:bool, parameters:dict, run_options:dict, fixed_seeds:bool):
        super().__init__()
        
        self.parameters = parameters
        self.run_options = run_options
        self.n_seeds = n_seeds
        self.term_id = term_id
        self.run_args_list = run_args_list
        self.moo = moo
        self.fixed_seeds = fixed_seeds
        
        self.total_runs = len(run_args_list)*n_seeds
        self.canceled = False
        self.best_gen = {} 
        self.data = pd.DataFrame()
        self.run_counter = 0

    def cancel(self):
        self.canceled = True    

    def run(self):
        #!
        import debugpy
        debugpy.debug_this_thread()
        seeds = np.arange(self.n_seeds) if self.fixed_seeds else np.random.choice(100000, size=self.n_seeds, replace=False)
        for run_args in self.run_args_list:
            for seed in seeds:
                if self.canceled:
                    return
                self.progressUpdate(run_args.algo_id, run_args.prob_id, seed)
                res = self.singleRun(run_args, seed)
                self.updateData(run_args, res, seed, res.algorithm.callback) if res is not None else None
                
    def singleRun(self, run_args: RunArgs, seed: int) -> Result:
        try:
            res = minimize(algorithm=run_args.algo_object, #@IgnoreException
                        problem=run_args.prob_object,
                        termination=run_args.term_object,
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
        
        text = f"Running Algorithm '{algo_id}' on Problem '{prob_id}', seed {seed}"
        percentage = self.run_counter/self.total_runs*100                
        self.progressSignal.emit(text, percentage)
        debug_print(f"{percentage:.0f}%  - ",text) #!
        self.run_counter += 1    
        
    def updateData(self, run_args: RunArgs, res: Result, seed:int, callback: MyCallback):
                
        run_length = len(callback.data[N_EVAL_KEY])

        single_run_data = {SEEDS_KEY: [seed] * run_length,
                           PROB_KEY: [run_args.prob_id] * run_length,
                           ALGO_KEY: [run_args.algo_id] * run_length}
        
        single_run_data.update(callback.data)
        if self.data.empty:
            self.data = pd.DataFrame(single_run_data)
        else:
            self.data = pd.concat([self.data, pd.DataFrame(single_run_data)])
        
        feas = np.where(res.algorithm.opt.get("feasible"))[0]
        optimal_pareto = res.algorithm.opt.get("F")[feas]
        key = (run_args.prob_id, run_args.algo_id, seed)
        
        if len(optimal_pareto) == 0:
            # no feasible solution found
            self.best_gen[key] = np.nan
        elif self.moo:
            # store best pareto set
            self.best_gen[key] = optimal_pareto
        else:
            # for SOO, record the best value coordinates in decision space followed by the value in objective space
            best_sol = np.concatenate((res.algorithm.opt.get("X")[0], optimal_pareto[0]))

            # Get all the solutions from the last generation
            last_generation = res.algorithm.pop

            # Get the decision variables and objective values for each solution
            decision_variables = np.array([indiv.get("X") for indiv in last_generation])
            objective_values = np.array([indiv.get("F") for indiv in last_generation])

            solutions = np.array([np.concatenate((x, f)) for x, f in zip(decision_variables, objective_values)])

            # concatenate the best solution to the solutions array
            solutions = np.vstack((best_sol, solutions))
            
            # Sort the solutions by objective value
            solutions = solutions[solutions[:, -1].argsort()]

            # Store the solutions
            self.best_gen[key] = solutions