from utils.useful_classes import EvalsOnGoal, MinusGoalAchieved

class EvalsOnGoalPSO(EvalsOnGoal):
    def __init__(self, goal=1.1, **kwargs):
        
        prob_id = kwargs.get('prob_id', 'None')
        if 'rosenbrock' in prob_id:
            goal = 100
        elif 'rastringin' in prob_id:
            goal = 100
        elif 'griewank' in prob_id:
            goal = 0.1
            
        super().__init__(goal=goal)

class MinusGoalAchievedPSO(MinusGoalAchieved):
    def __init__(self, goal=1.1, **kwargs):
        
        prob_id = kwargs.get('prob_id', 'None')
        if 'rosenbrock' in prob_id:
            goal = 100
        elif 'rastringin' in prob_id:
            goal = 100
        elif 'griewank' in prob_id:
            goal = 0.1
            
        super().__init__(goal=goal)

from pymoo.core.termination import Termination
from pymoo.termination.max_gen import MaximumGenerationTermination
from utils.useful_classes import StaledBestTermination, MinFitnessTermination 

class PSOTermination(Termination):
    def __init__(self, n_max_gen=10000, f_threshold = 1.1, stale_limit=2000, **kwargs):
        super().__init__()
        
        prob_id = kwargs.get('prob_id', 'None')
        if 'rosenbrock' in prob_id:
            f_threshold = 100
        elif 'rastringin' in prob_id:
            f_threshold = 100
        elif 'griewank' in prob_id:
            f_threshold = 0.1
        
        self.f = MinFitnessTermination(f_threshold)
        self.max_gen = MaximumGenerationTermination(n_max_gen)
        self.stale = StaledBestTermination(stale_limit)
        
        self.criteria = [self.f, self.max_gen, self.stale]

    def _update(self, algorithm):
        p = [criterion.update(algorithm) for criterion in self.criteria]
        return max(p)
