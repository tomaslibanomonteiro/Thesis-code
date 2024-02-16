"""
In this script, an example of how you can program your own Class and integrate it in the App. 

The code must be written according to the pymoo framework. For more information, see https://pymoo.org/algorithms/index.html

To integrate the created class in the App, added it in the respective get_class_options function of the backend/get.py file. 

Keep in mind that the App only allows the changing of values in arguments with type string, boolean, integer or float.

In case of an Algorithm, if one of the arguments is an operator, 
("mutation", "crossover", "selection", "decomposition", "sampling", "ref_dirs")
the App will retrieve the default class of that operator, provided that it is one of the operators in the get_operator_options. However, specific initializations are not possible, so if you want to use a specific initialization, you must create a new class;

So this initialization: 

    crossover=SBX(eta=15, prob=0.9)

Will be translated as this, by the App:

    crossover=SBX()

So instead, do this if you want to have that specific default in the App:

    class MySBX(SBX)
        ...
        super.__init__(eta=15, prob=0.9)
    ...
    crossover=MySBX()
    
Or just manually change the values in the crossover operator in the App.

In the example below, is just the DE algorithm coded in pymoo with a different default value for pop_size.
This algorithm is already added to the list of algorithms in the backend/run.py file, and can be used in the App as 'my_algorithm' in Single Objective Optimization.  
"""

import numpy as np

from pymoo.algorithms.base.genetic import GeneticAlgorithm
from pymoo.algorithms.soo.nonconvex.ga import FitnessSurvival
from pymoo.core.infill import InfillCriterion
from pymoo.core.population import Population
from pymoo.core.replacement import ImprovementReplacement
from pymoo.core.variable import Choice, get
from pymoo.core.variable import Real
from pymoo.operators.control import EvolutionaryParameterControl, NoParameterControl
from pymoo.operators.crossover.binx import mut_binomial
from pymoo.operators.crossover.expx import mut_exp
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.bounds_repair import repair_random_init
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.selection.rnd import fast_fill_random
from pymoo.termination.default import DefaultSingleObjectiveTermination
from pymoo.util.display.single import SingleObjectiveOutput
from pymoo.util.misc import where_is_what


# =========================================================================================================
# Crossover
# =========================================================================================================

def de_differential(X, F, jitter, alpha=0.001):
    n_parents, n_matings, n_var = X.shape
    assert n_parents % 2 == 1, "For the differential an odd number of values need to be provided"

    # the differentials from each pair
    delta = np.zeros((n_matings, n_var))

    # for each difference of the differences
    for i in range(1, n_parents, 2):
        # create the weight vectors with jitter to give some variation
        _F = F[:, None].repeat(n_var, axis=1)
        _F[jitter] *= (1 + alpha * (np.random.random((jitter.sum(), n_var)) - 0.5))

        # add the difference to the vector
        delta += _F * (X[i] - X[i + 1])

    # now add the differentials to the first parent
    Xp = X[0] + delta

    return Xp


# =========================================================================================================
# Variant
# =========================================================================================================

class Variant(InfillCriterion):

    def __init__(self,
                 selection="best",
                 n_diffs=1,
                 F=0.5,
                 crossover="bin",
                 CR=0.2,
                 jitter=False,
                 prob_mut=0.1,
                 control=EvolutionaryParameterControl,
                 **kwargs):

        super().__init__(**kwargs)
        self.selection = Choice(selection, options=["rand", "best"], all=["rand", "best", "target-to-best"])
        self.n_diffs = Choice(n_diffs, options=[1], all=[1, 2])
        self.F = Real(F, bounds=(0.4, 0.7), strict=(0.0, None))
        self.crossover = Choice(crossover, ["bin"], all=["bin", "exp", "hypercube", "line"])
        self.CR = Real(CR, bounds=(0.2, 0.8), strict=(0.0, 1.0))
        self.jitter = Choice(jitter, options=[False], all=[True, False])

        self.mutation = PM(at_least_once=True)
        self.mutation.eta = 20
        self.mutation.prob = prob_mut

        self.control = control(self)

    def do(self, problem, pop, n_offsprings, algorithm=None, **kwargs):
        control = self.control

        # let the parameter control now some information
        control.tell(pop=pop)

        # set the controlled parameter for the desired number of offsprings
        control.do(n_offsprings)

        # find the different groups of selection schemes and order them by category
        sel, n_diffs = get(self.selection, self.n_diffs, size=n_offsprings)
        H = where_is_what(zip(sel, n_diffs))

        # get the parameters used for reproduction during the crossover
        F, CR, jitter = get(self.F, self.CR, self.jitter, size=n_offsprings)

        # the `target` vectors which will be recombined
        X = pop.get("X")

        # the `donor` vector which will be obtained through the differential equation
        donor = np.full((n_offsprings, problem.n_var), np.nan)

        # for each type defined by the type and number of differentials
        for (sel_type, n_diffs), targets in H.items():

            # the number of offsprings created in this run
            n_matings, n_parents = len(targets), 1 + 2 * n_diffs

            # create the parents array
            P = np.full([n_matings, n_parents], -1)

            itself = np.array(targets)[:, None]

            best = lambda: np.random.choice(np.where(pop.get("rank") == 0)[0], replace=True, size=n_matings)

            if sel_type == "rand":
                fast_fill_random(P, len(pop), columns=range(n_parents), Xp=itself)
            elif sel_type == "best":
                P[:, 0] = best()
                fast_fill_random(P, len(pop), columns=range(1, n_parents), Xp=itself)
            elif sel_type == "target-to-best":
                P[:, 0] = targets
                P[:, 1] = best()
                fast_fill_random(P, len(pop), columns=range(2, n_parents), Xp=itself)
            else:
                raise Exception("Unknown selection method.")

            # get the values of the parents in the design space
            XX = np.swapaxes(X[P], 0, 1)

            # do the differential crossover to create the donor vector
            Xp = de_differential(XX, F[targets], jitter[targets])

            # make sure everything stays in bounds
            if problem.has_bounds():
                Xp = repair_random_init(Xp, XX[0], *problem.bounds())

            # set the donors (the one we have created in this step)
            donor[targets] = Xp

        # the `trial` created by by recombining target and donor
        trial = np.full((n_offsprings, problem.n_var), np.nan)

        crossover = get(self.crossover, size=n_offsprings)
        for name, K in where_is_what(crossover).items():

            _target = X[K]
            _donor = donor[K]
            _CR = CR[K]

            if name == "bin":
                M = mut_binomial(len(K), problem.n_var, _CR, at_least_once=True)
                _trial = np.copy(_target)
                _trial[M] = _donor[M]
            elif name == "exp":
                M = mut_exp(n_offsprings, problem.n_var, _CR, at_least_once=True)
                _trial = np.copy(_target)
                _trial[M] = _donor[M]
            elif name == "line":
                w = np.random.random((len(K), 1)) * _CR[:, None]
                _trial = _target + w * (_donor - _target)
            elif name == "hypercube":
                w = np.random.random((len(K), _target.shape[1])) * _CR[:, None]
                _trial = _target + w * (_donor - _target)
            else:
                raise Exception(f"Unknown crossover variant: {name}")

            trial[K] = _trial

        # create the population
        off = Population.new(X=trial)

        # do the mutation which helps to add some more diversity
        off = self.mutation(problem, off)

        # repair the individuals if necessary - disabled if repair is NoRepair
        off = self.repair(problem, off, **kwargs)

        # advance the parameter control by attaching them to the offsprings
        control.advance(off)

        return off


# =========================================================================================================
# Implementation
# =========================================================================================================


class MyAlgorithm(GeneticAlgorithm):

    def __init__(self,
                 pop_size=200,
                 n_offsprings=None,
                 sampling=FloatRandomSampling(),
                 variant="DE/best/1/bin",
                 output=SingleObjectiveOutput(),
                 **kwargs
                 ):

        if variant is None:
            if "control" not in kwargs:
                kwargs["control"] = NoParameterControl
            variant = Variant(**kwargs)

        elif isinstance(variant, str):
            try:
                _, selection, n_diffs, crossover = variant.split("/")
                if "control" not in kwargs:
                    kwargs["control"] = NoParameterControl
                variant = Variant(selection=selection, n_diffs=int(n_diffs), crossover=crossover, **kwargs)
            except:
                raise Exception("Please provide a valid variant: DE/<selection>/<n_diffs>/<crossover>")

        super().__init__(pop_size=pop_size,
                         n_offsprings=n_offsprings,
                         sampling=sampling,
                         mating=variant,
                         survival=None,
                         output=output,
                         eliminate_duplicates=False,
                         **kwargs)

        self.termination = DefaultSingleObjectiveTermination()

    def _initialize_advance(self, infills=None, **kwargs):
        FitnessSurvival().do(self.problem, self.pop, return_indices=True)

    def _infill(self):
        infills = self.mating.do(self.problem, self.pop, self.n_offsprings, algorithm=self)

        # tag each individual with an index - if a steady state version is executed
        index = np.arange(len(infills))

        # if number of offsprings is set lower than pop_size - randomly select
        if self.n_offsprings < self.pop_size:
            index = np.random.permutation(len(infills))[:self.n_offsprings]
            infills = infills[index]

        infills.set("index", index)

        return infills

    def _advance(self, infills=None, **kwargs):
        assert infills is not None, "This algorithms uses the AskAndTell interface thus infills must to be provided."

        # get the indices where each offspring is originating from
        I = infills.get("index")

        # replace the individuals with the corresponding parents from the mating
        self.pop[I] = ImprovementReplacement().do(self.problem, self.pop[I], infills)

        # update the information regarding the current population
        FitnessSurvival().do(self.problem, self.pop, return_indices=True)

    def _set_optimum(self, **kwargs):
        k = self.pop.get("rank") == 0
        self.opt = self.pop[k]
