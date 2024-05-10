###################################################################################################
################################## CHANGE THIS TO YOUR PATH  ######################################
PATH_TO_REPO_FOLDER = r"C:\Users\tomas\OneDrive - Universidade de Lisboa\Desktop\Tese\Thesis-code"
###################################################################################################


import sys
sys.path.insert(1, PATH_TO_REPO_FOLDER)
import pandas as pd
from pymoo.optimize import minimize
from threading import Thread
import os
import filecmp
import datetime
from pymoo.operators.crossover.sbx import SBX
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.unsga3 import UNSGA3
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.ctaea import CTAEA

from backend.get import get_algorithm, get_problem, get_performance_indicator, get_termination, get_reference_directions
from utils.defines import PROB_KEY, ALGO_KEY, PI_KEY, SEEDS_KEY, MOO_KEY, N_EVAL_KEY
from backend.run import MyCallback
from tests.tests_declaration import TEST_NAME_KEY, soo_algos, soo_probs, soo_mixed, moo_algos, moo_probs, moo_mixed

RESULTS_FILE = 'thesis/app_framework/results/results.txt'
RESULTS_FOLDER = 'thesis/app_framework/results'
EXPECTED_RESULTS_FOLDER = 'thesis/app_framework/expected_results'

def correctProbs(probs:dict):
    for key in probs.keys():    
        for i in range(1, 10):
            dascmop_key = f'dascmop' + str(i)
            wfg_key = f'wfg' + str(i)
            if key == dascmop_key:
                probs[dascmop_key] = get_problem(dascmop_key,difficulty_factors=1) if i in [7,8,9] else get_problem(dascmop_key,difficulty=1)
            elif key == wfg_key:
                probs[wfg_key] = get_problem(wfg_key,n_var=10,n_obj=3)
    
    return probs

def correctAlgos(algos: dict, n_obj, n_partitions=12):
    ref_dirs = get_reference_directions('das-dennis', n_dim=n_obj, n_partitions=n_partitions)
    for key in algos.keys():
        if key == 'nsga2':
            algos[key] = NSGA2(crossover=SBX())
        elif key == 'nsga3':
            algos[key] = NSGA3(ref_dirs,crossover=SBX())
        elif key == 'unsga3':
            algos[key] = UNSGA3(ref_dirs,crossover=SBX())
        elif key == 'moead':
            algos[key] = MOEAD(ref_dirs,crossover=SBX())
        elif key == 'ctaea':
            algos[key] = CTAEA(ref_dirs,crossover=SBX())
                    
    return algos

def try_get_function(get_function, id):
    try:
        object = get_function(id)
    except:
        object = 'failed to get object'
    return object
class FrameworkTest(Thread):
    def __init__(self, options: dict, n_seeds:int=1, n_evals:int=500):
        super().__init__()
        self.test_name = options.pop(TEST_NAME_KEY) + '.csv'
        self.is_finished = False
        
        if SEEDS_KEY not in options.keys():
            options[SEEDS_KEY] = n_seeds
        if 'n_evals' in options.keys():
            n_evals = options.pop('n_evals')
        
        self.termination = get_termination('n_eval', n_max_evals=n_evals)
        
        if not set([MOO_KEY, PI_KEY, ALGO_KEY, PROB_KEY]) <= set(options.keys()):
            raise Exception('Invalid options dictionary. Test options must contain at least: ' + str([MOO_KEY, PI_KEY, ALGO_KEY, PROB_KEY]))
        self.options = options
        self.moo = self.options.pop(MOO_KEY) 
        self.data = pd.DataFrame()
        
    def run(self):
        problems = {prob_id: try_get_function(get_problem,prob_id) for prob_id in self.options[PROB_KEY]}
        self.problems = correctProbs(problems)
        for prob_id, prob in self.problems.items():
            algos = {algo_id: try_get_function(get_algorithm,algo_id) for algo_id in self.options[ALGO_KEY]}
            self.algos = correctAlgos(algos, prob.n_obj)
            for algo_id, algo in self.algos.items():
                try:
                    pf = prob.pareto_front(ref_dirs=algo.ref_dirs) #@IgnoreException
                except:
                    pf = prob.pareto_front() if prob.pareto_front else None
                self.pi_objects = [get_performance_indicator(pi_id, pf=pf) for pi_id in self.options[PI_KEY]]
                for seed in range(self.options[SEEDS_KEY]):
                    res = minimize(algorithm=algo,
                                    problem=prob,
                                    termination=self.termination,
                                    seed=seed,
                                    verbose=False,
                                    save_history=False,
                                    progress_bar=True,
                                    callback=MyCallback(self.options[PI_KEY], self.pi_objects))
        
                    self.updateData(prob_id, algo_id, res, seed, res.algorithm.callback) if res is not None else None

        self.data.to_csv(RESULTS_FOLDER + '/' + self.test_name, index=False)
        self.is_finished = True
    
    def updateData(self, prob_id, algo_id, res, seed, callback: MyCallback):
        if res is None:
            return
        run_length = len(callback.data[N_EVAL_KEY])

        single_run_data = {SEEDS_KEY: [seed] * run_length,
                           PROB_KEY: [prob_id] * run_length,
                           ALGO_KEY: [algo_id] * run_length}
        
        single_run_data.update(callback.data)
        if self.data.empty:
            self.data = pd.DataFrame(single_run_data)
        else:
            self.data = pd.concat([self.data, pd.DataFrame(single_run_data)])

TESTS_TO_RUN = [soo_algos, soo_probs, soo_mixed, moo_algos, moo_probs, moo_mixed]

def main():

    # create a new folder RESULTS_FOLDER
    if os.path.exists(RESULTS_FOLDER):
        for file in os.listdir(RESULTS_FOLDER):
            if file.endswith(".csv"):
                os.remove(os.path.join(RESULTS_FOLDER, file))
    else:
        os.mkdir(RESULTS_FOLDER)
    
    # create the app to instantiate the MainWindows
    tests=[]    
    # run the tests
    for test_options in TESTS_TO_RUN: 
        test = FrameworkTest(test_options)
        tests.append(test)
        test.start()
    
    # Wait for all tests threads to finish
    for test in tests:
        test.join()

    # get the list of files to compare
    expected_files = [file for file in os.listdir(EXPECTED_RESULTS_FOLDER)]
    files = [file for file in os.listdir(RESULTS_FOLDER) if file.endswith(".csv")]
            
    # compare the CSV files
    for file in files:
        # append the results to the file inside RESULTS_FOLDER
        with open(RESULTS_FILE, 'a') as f:
            date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if file not in expected_files:
                string = date_time + ' No comparison for test ' + file + '\n'
            else:
                test_result = ' passed!' if filecmp.cmp(RESULTS_FOLDER + '/' + file, EXPECTED_RESULTS_FOLDER + '/' + file) else ' failed!'
                string = date_time + ' Test ' + file + test_result + '\n'
            print(string)
            f.write(string)

if __name__ == '__main__':
    main()