# original imports
# from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
# from pymoo.operators.mutation.inversion import InversionMutation
# from pymoo.operators.mutation.bitflip import BitflipMutation

# new imports
from thesis.results_worst_case.operators import PermutationRandomSampling, StartFromZeroRepair, OrderCrossover, InversionFlipMutation
from thesis.results_worst_case.aco_operators import RankAndCrowdingACO

from pymoo.algorithms.moo.nsga2 import NSGA2, binary_tournament, TournamentSelection, RankAndCrowding
from utils.useful_classes import BinaryTournament

class PermutationNSGA2(NSGA2):
    def __init__(self,
                 pop_size=20,
                 sampling=PermutationRandomSampling(),
                 survival=RankAndCrowding(),
                 selection=BinaryTournament(),
                 mutation=InversionFlipMutation(),
                 crossover=OrderCrossover(),
                 repair=StartFromZeroRepair(),
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
        

# no crossover
class ACO_NSGA2(NSGA2):
    def __init__(self, pop_size=20):
        super().__init__(
            pop_size=pop_size,
            sampling=PermutationRandomSampling(),
            survival=RankAndCrowdingACO(),
            selection=BinaryTournament(),
            mutation=InversionFlipMutation(),
            crossover=OrderCrossover(),
            repair=StartFromZeroRepair(),
            eliminate_duplicates=True,
        )

        
if __name__ == '__main__':
    from main import main
    main()


