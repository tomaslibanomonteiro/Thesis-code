import numpy as np
import pandas as pd
from pymoo.core.algorithm import Algorithm
from pymoo.core.callback import Callback
from pymoo.core.result import Result
from pymoo.optimize import minimize
import matplotlib.pyplot as plt

from utils.debug import debug_print


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

class SingleRunArgs():
    def __init__(self, prob_id: str, prob_object, algo_id: str, algo_object, pi_ids: list, pi_objects: list): 
        self.prob_id = prob_id
        self.prob_object = prob_object 
        self.algo_id = algo_id
        self.algo_object = algo_object
        self.pi_ids = pi_ids
        self.pi_object = pi_objects                
        
class Run():
    def __init__(self, single_run_args: list, term_id, term_object, n_seeds: int, moo: bool):
        self.n_seeds = n_seeds
        self.term_id = term_id
        self.term_object = term_object
        self.single_run_args_list = single_run_args
        self.moo = moo
        self.data = pd.DataFrame()
        self.dfs_dict = {}
        
    def run(self):
        for run_args in self.single_run_args_list:
            for seed in range(self.n_seeds):
                debug_print(run_args.algo_id, run_args.prob_id, seed)
                res = self.single_run(run_args, seed, self.term_object)
                self.data = self.update_data(run_args, res, res.algorithm.callback)
        
        self.dfs_dict = self.get_DFs_dict(self.single_run_args_list[0].pi_ids)
        
    def single_run(self, run_args: SingleRunArgs, seed: int, termination) -> Result:
        res = minimize(algorithm=run_args.algo_object,
                       problem=run_args.prob_object,
                       termination=termination,
                       seed=seed,
                       verbose=False,
                       save_history=False,
                       progress_bar=True,
                       callback=MyCallback())
        
        return res

    def update_data(self, run_args: SingleRunArgs, res: Result, callback: MyCallback):
        data = self.data

        run_length = len(callback.n_evals)

        single_run = {'seed': [res.algorithm.seed] * run_length,
                      'problem_id': [run_args.prob_id] * run_length,
                      'algorithm_id': [run_args.algo_id] * run_length,
                      'n_eval': callback.n_evals,
                      'n_gen': callback.n_gen}
        
        # get the performance indicators values
        for pi_id, pi_object in zip(run_args.pi_ids, run_args.pi_object):
            if pi_id == "best_default":
                # get the float values in the callback.best list
                pi_data = [None if len(item) == 0 else float(item[0]) for item in callback.best]                    
            else:
                pi_data = [pi_object.do(pf) for pf in callback.best]
            # add the data to the data frame    
            single_run[pi_id] = pi_data
        
        single_run = pd.DataFrame(single_run)

        return pd.concat([data, single_run])

    def print_data(self):
        print(self.data)
        
    def get_DFs_dict(self, pi_ids: list):
        """ returns a dictionary of pi_ids, where each entry is a dataframe
        where the columns are the different problems and the rows the different 
        algorithms, and each cell is the mean of the performance indicator
        of that combination across the different seeds"""
        
        # first get only the last generation for each combination of problem, algorithm and seed
        last_gen = self.data.groupby(['problem_id', 'algorithm_id', 'seed']).last()
        
        # then get the mean of the performance indicator across the different seeds
        result = last_gen.groupby(['problem_id', 'algorithm_id'])[pi_ids].mean()
        
        dfs_dict = {}
        for pi_id in pi_ids:
            dfs_dict[pi_id] = result[pi_id].unstack().T      
            
            # add another column with the sum of all the instances where the algorithm was the best for each problem 
            if pi_id == "hv":
                dfs_dict[pi_id]['voting'] = dfs_dict[pi_id].idxmax(axis=0).value_counts()
                dfs_dict[pi_id]['voting'] = dfs_dict[pi_id]['voting'].fillna(0).astype(int)
            else:
                dfs_dict[pi_id]['voting'] = dfs_dict[pi_id].idxmin(axis=0).value_counts()
                dfs_dict[pi_id]['voting'] = dfs_dict[pi_id]['voting'].fillna(0).astype(int)
            
        return dfs_dict
    
    def save_data(self, filename: str):
        self.data.to_csv(filename, index=False)
        
    def plot_prob(self, prob_id: str, pi_id: str):
        df = self.data[self.data['problem_id'] == prob_id]

        # get df with columns: algorithm_id, seed, n_eval, n_gen, pi_id
        df = df[['algorithm_id', 'seed', 'n_eval', 'n_gen', pi_id]]

        # average across seeds
        df = df.groupby(['algorithm_id', 'n_eval', 'n_gen']).mean()

        # plot by algorithm, with n_eval on the x axis and pi_id on the y axis using matplotlib
        for var in ['n_gen', 'n_eval']:
            plt.figure()
            for algo_id in df.index.levels[0]:
                df_algo = df.loc[algo_id]
                plt.plot(df_algo.index.get_level_values(var), df_algo[pi_id], label=algo_id)

            plt.legend()
            plt.xlabel(var)
            plt.ylabel(pi_id)
            plt.show()