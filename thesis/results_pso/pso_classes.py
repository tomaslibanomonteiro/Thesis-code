from utils.useful_classes import EvalsOnGoal, MinusGoalAchieved
from utils.defines import CONVERT_KEY

def getGoal(prob_id):
    if 'rosenbrock-2' in prob_id:
        goal = 0.5
    elif 'rastrigin-2' in prob_id:
        goal = 0.5
    elif 'griewank-2' in prob_id:
        goal = 0.01
        
    elif 'rosenbrock-30' in prob_id:
        goal = 100
    elif 'rastrigin-30' in prob_id:
        goal = 100
    elif 'griewank-30' in prob_id:
        goal = 0.1
    else:
        raise ValueError('Invalid prob_id')
    
    return goal

class EvalsOnGoalPSO(EvalsOnGoal):
    def __init__(self, prob_id='prob_id' + CONVERT_KEY):
        super().__init__(goal=getGoal(prob_id))

class MinusGoalAchievedPSO(MinusGoalAchieved):
    def __init__(self, prob_id='prob_id' + CONVERT_KEY):
        super().__init__(goal=getGoal(prob_id))

from pymoo.core.termination import Termination
from pymoo.termination.max_gen import MaximumGenerationTermination
from utils.useful_classes import StaledBestTermination, MinFitnessTermination 

class PSOTermination(Termination):
    def __init__(self, n_max_gen=10000, stale_limit=2000, prob_id='prob_id' + CONVERT_KEY):
        super().__init__()
        
        f_threshold = getGoal(prob_id)        
        self.f = MinFitnessTermination(f_threshold)
        self.max_gen = MaximumGenerationTermination(n_max_gen)
        self.stale = StaledBestTermination(stale_limit)
        
        self.criteria = [self.f, self.max_gen, self.stale]

    def _update(self, algorithm):
        p = [criterion.update(algorithm) for criterion in self.criteria]
        return max(p)
