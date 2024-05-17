from utils.useful_classes import EvalsOnGoal, MinusGoalAchieved

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
    def __init__(self, **kwargs):
        prob_id = kwargs.get('prob_id', 'None')
        super().__init__(goal=getGoal(prob_id))

class MinusGoalAchievedPSO(MinusGoalAchieved):
    def __init__(self, **kwargs):
        prob_id = kwargs.get('prob_id', 'None')            
        super().__init__(goal=getGoal(prob_id))

from pymoo.core.termination import Termination
from pymoo.termination.max_gen import MaximumGenerationTermination
from utils.useful_classes import StaledBestTermination, MinFitnessTermination 

class PSOTermination(Termination):
    def __init__(self, n_max_gen=10000, stale_limit=2000, **kwargs):
        super().__init__()
        
        prob_id = kwargs.get('prob_id', 'None')
        f_threshold = getGoal(prob_id)
                
        self.f = MinFitnessTermination(f_threshold)
        self.max_gen = MaximumGenerationTermination(n_max_gen)
        self.stale = StaledBestTermination(stale_limit)
        
        self.criteria = [self.f, self.max_gen, self.stale]

    def _update(self, algorithm):
        p = [criterion.update(algorithm) for criterion in self.criteria]
        return max(p)
