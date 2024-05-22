
# original imports
# from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
# from pymoo.operators.mutation.inversion import InversionMutation
# from pymoo.operators.mutation.bitflip import BitflipMutation

# new imports
from thesis.results_worst_case.operators import PermutationRandomSampling, StartFromZeroRepair, OrderCrossover, InversionFlipMutation

from pymoo.algorithms.moo.nsga2 import NSGA2, binary_tournament, TournamentSelection, RankAndCrowding

class PermutationNSGA2(NSGA2):
    def __init__(self, pop_size=20):
        super().__init__(
            pop_size=pop_size,
            sampling=PermutationRandomSampling(),
            selection=TournamentSelection(func_comp=binary_tournament),
            mutation=InversionFlipMutation(),
            survival=RankAndCrowding(),
            crossover=OrderCrossover(),
            repair=StartFromZeroRepair(),
            eliminate_duplicates=True,
        )
        
if __name__ == '__main__':
    from main import main
    main()