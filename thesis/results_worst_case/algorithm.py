
# original imports
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.termination.default import DefaultSingleObjectiveTermination

# new imports
from operators import PermutationRandomSampling, StartFromZeroRepair, OrderCrossover, InversionMutation

import numpy as np
from problem import RandomMultiMixedTSP
from pymoo.algorithms.moo.nsga2 import NSGA2, binary_tournament, TournamentSelection, RankAndCrowding
from pymoo.core.mixed import MixedVariableGA
from pymoo.optimize import minimize

algorithm = NSGA2(
    pop_size=3,
    sampling=PermutationRandomSampling(),
    selection=TournamentSelection(func_comp=binary_tournament),
    mutation=InversionMutation(),
    survival=RankAndCrowding(),
    crossover=OrderCrossover(),
    repair=StartFromZeroRepair(),
    eliminate_duplicates=True,
)
    
if __name__ == '__main__':
    from main import main
    main()