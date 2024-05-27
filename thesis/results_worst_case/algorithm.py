# original imports
# from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
# from pymoo.operators.mutation.inversion import InversionMutation
# from pymoo.operators.mutation.bitflip import BitflipMutation

# new imports
from thesis.results_worst_case.operators import MixedPermRandomSampling, MixedStartFromZeroRepair, MixedOrderCrossover, InversionFlipMutation
from thesis.results_worst_case.aco_operators import RankAndCrowdingACO

from pymoo.algorithms.moo.nsga2 import NSGA2, RankAndCrowding
from utils.useful_classes import BinaryTournament

class PermutationNSGA2(NSGA2):
    def __init__(self,
                 pop_size=20,
                 sampling=MixedPermRandomSampling(),
                 survival=RankAndCrowding(),
                 selection=BinaryTournament(),
                 mutation=InversionFlipMutation(),
                 crossover=MixedOrderCrossover(),
                 repair=MixedStartFromZeroRepair(),
                 eliminate_duplicates=True,
                 **kwargs):
        super().__init__(
            pop_size=pop_size,
            sampling=sampling,
            survival=survival,
            selection=selection,
            mutation=mutation,
            crossover=crossover,
            repair=repair,
            eliminate_duplicates=eliminate_duplicates,
            **kwargs
        )   
        
class ACO_NSGA2(NSGA2):
    def __init__(self,          
                 pop_size=20,
                 sampling=MixedPermRandomSampling(),
                 survival=RankAndCrowdingACO(),
                 selection=BinaryTournament(),
                 mutation=InversionFlipMutation(),
                 crossover=MixedOrderCrossover(),
                 repair=MixedStartFromZeroRepair(),
                 eliminate_duplicates=True,
                 **kwargs):
        super().__init__(
            pop_size=pop_size,
            sampling=sampling,
            survival=survival,
            selection=selection,
            mutation=mutation,
            crossover=crossover,
            repair=repair,
            eliminate_duplicates=eliminate_duplicates,
            **kwargs
        )
        
if __name__ == '__main__':
    from main import main
    main()


