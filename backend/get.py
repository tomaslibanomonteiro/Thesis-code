import re

# =========================================================================================================
# Generic
# =========================================================================================================

def get_from_list(l, name, args, kwargs):
    i = None

    for k, e in enumerate(l):
        if e[0] == name:
            i = k
            break

    if i is None:
        for k, e in enumerate(l):
            if re.match(e[0], name):
                i = k
                break

    if i is not None:

        if len(l[i]) == 2:
            name, clazz = l[i]
            return clazz(*args, **kwargs)

        elif len(l[i]) == 3:
            name, clazz, default_kwargs = l[i]

            # overwrite the default if provided
            for key, val in kwargs.items():
                default_kwargs[key] = val
            kwargs = default_kwargs

            return clazz(*args, **kwargs)

    else:
        raise Exception("Object '%s' for not found in %s" % (name, [e[0] for e in l]))

def returnOptions(objectives, single_list, multi_list):
    
    if objectives == 'all':
        return list( set(single_list + multi_list) )
    elif objectives == 'soo':
        return single_list
    elif objectives == 'moo':
        return multi_list
    else:
        raise Exception("'objectives' must be 'all', 'soo' or 'moo'")
        
# =========================================================================================================
# Algorithms
# =========================================================================================================

def get_algorithm_options(objectives = 'all'):
        
    from pymoo.algorithms.moo.ctaea import CTAEA
    from pymoo.algorithms.moo.moead import MOEAD
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.algorithms.moo.rnsga2 import RNSGA2
    from pymoo.algorithms.moo.rnsga3 import RNSGA3
    from pymoo.algorithms.moo.unsga3 import UNSGA3
    from pymoo.algorithms.soo.nonconvex.brkga import BRKGA
    from pymoo.algorithms.soo.nonconvex.cmaes import CMAES
    from pymoo.algorithms.soo.nonconvex.de import DE
    from pymoo.algorithms.soo.nonconvex.ga import GA
    from pymoo.algorithms.soo.nonconvex.nelder import NelderMead
    from pymoo.algorithms.soo.nonconvex.pattern import PatternSearch
    from pymoo.algorithms.soo.nonconvex.pso import PSO

    ALGORITHMS_SINGLE = [
        ("ga", GA),
        ("brkga", BRKGA),
        ("de", DE),
        ("nelder-mead", NelderMead),
        ("pattern-search", PatternSearch),
        ("cmaes", CMAES),
        ("pso", PSO),
    ]
    
    ALGORITHMS_MULTI = [
        ("nsga2", NSGA2),
        ("rnsga2", RNSGA2),
        ("nsga3", NSGA3),
        ("unsga3", UNSGA3),
        ("rnsga3", RNSGA3),
        ("moead", MOEAD),
        ("ctaea", CTAEA),
    ]

    return returnOptions(objectives, ALGORITHMS_SINGLE, ALGORITHMS_MULTI)


def get_algorithm(name, objectives = 'all', *args, d={}, **kwargs):
    return get_from_list(get_algorithm_options(objectives), name, args, {**d, **kwargs})


# =========================================================================================================
# Other Classes
# =========================================================================================================

def get_other_class_options(objectives = 'all'):
        
    from pymoo.algorithms.soo.nonconvex.cmaes import CMAESOutput
    from pymoo.algorithms.soo.nonconvex.ga import FitnessSurvival
    from pymoo.algorithms.soo.nonconvex.nelder import adaptive_params
    from pymoo.algorithms.soo.nonconvex.pso import PSOFuzzyOutput
    from pymoo.core.repair import NoRepair
    from pymoo.operators.sampling.lhs import criterion_maxmin
    from pymoo.util.display.multi import MultiObjectiveOutput
    from pymoo.util.display.single import SingleObjectiveOutput
    
    OTHER_CLASS_OPTIONS_SINGLE = [
        ("SingleObjectiveOutput", SingleObjectiveOutput), # output
        ("PSOFuzzyOutput", PSOFuzzyOutput),               # output  
        ("CMAESOutput", CMAESOutput),                     # output
        ("FitnessSurvival", FitnessSurvival),             # survival  
        ("adaptive_params", adaptive_params),             # func_params
        ("NoRepair", NoRepair),                           # repair
        ("criterion_maxmin", criterion_maxmin)            # criterion  
    ]

    OTHER_CLASS_OPTIONS_MULTI = [
        ("MultiObjectiveOutput", MultiObjectiveOutput)   # output   
    ]
    
    return returnOptions(objectives, OTHER_CLASS_OPTIONS_SINGLE, OTHER_CLASS_OPTIONS_MULTI)

def get_other_class(name, objectives = 'all', *args, d={}, **kwargs):
    return get_from_list(get_other_class_options(objectives), name, args, {**d, **kwargs})

# =========================================================================================================
# Sampling
# =========================================================================================================

def get_sampling_options(objectives = 'all'):
        
    from pymoo.operators.sampling.lhs import LHS
    # from pymoo.operators.integer_from_float_operator import IntegerFromFloatSampling
    from pymoo.operators.sampling.rnd import (BinaryRandomSampling,
                                              FloatRandomSampling,
                                              PermutationRandomSampling)
    
    SAMPLING = [
        ("real_random", FloatRandomSampling),
        ("real_lhs", LHS),
        ("bin_random", BinaryRandomSampling),
        #("int_random", IntegerFromFloatSampling, {'clazz': FloatRandomSampling}),
        #("int_lhs", IntegerFromFloatSampling, {'clazz': LatinHypercubeSampling}),
        ("perm_random", PermutationRandomSampling)
    ]

    return SAMPLING


def get_sampling(name, objectives = 'all', *args, d={}, **kwargs):
    return get_from_list(get_sampling_options(objectives), name, args, {**d, **kwargs})


# =========================================================================================================
# Selection
# =========================================================================================================

def get_selection_options(objectives = 'all'):
        
    from pymoo.operators.selection.rnd import RandomSelection
    from pymoo.operators.selection.tournament import TournamentSelection
    
    SELECTION = [
        ("random", RandomSelection),
        ("tournament", TournamentSelection),
    ]

    return SELECTION


def get_selection(name, objectives = 'all', *args, d={}, **kwargs):
    return get_from_list(get_selection_options(objectives), name, args, {**d, **kwargs})


# =========================================================================================================
# Crossover
# =========================================================================================================

def get_crossover_options(objectives = 'all'):
        
    from pymoo.operators.crossover.dex import DEX
    #from pymoo.operators.integer_from_float_operator import IntegerFromFloatCrossover
    from pymoo.operators.crossover.erx import EdgeRecombinationCrossover
    from pymoo.operators.crossover.expx import ExponentialCrossover
    from pymoo.operators.crossover.hux import HalfUniformCrossover
    from pymoo.operators.crossover.ox import OrderCrossover
    from pymoo.operators.crossover.pcx import PCX
    from pymoo.operators.crossover.pntx import PointCrossover
    from pymoo.operators.crossover.sbx import SBX, SimulatedBinaryCrossover
    from pymoo.operators.crossover.ux import UniformCrossover
    
    CROSSOVER = [
        ("real_sbx", SBX),
        #("int_sbx", IntegerFromFloatCrossover, dict(clazz=SimulatedBinaryCrossover, prob=0.9, eta=30)),
        ("real_de", DEX),
        ("real_pcx", PCX),
        ("(real|bin|int)_ux", UniformCrossover),
        ("(bin|int)_hux", HalfUniformCrossover),
        ("(real|bin|int)_exp", ExponentialCrossover),
        ("(real|bin|int)_k_point", PointCrossover),
        ("perm_ox", OrderCrossover),
        ("perm_erx", EdgeRecombinationCrossover)
    ]

    return CROSSOVER


def get_crossover(name, objectives = 'all', *args, d={}, **kwargs):
    return get_from_list(get_crossover_options(objectives), name, args, {**d, **kwargs})


# =========================================================================================================
# Mutation
# =========================================================================================================

def get_mutation_options(objectives = 'all'):
        
    from pymoo.operators.mutation.bitflip import BitflipMutation
    #from pymoo.operators.integer_from_float_operator import IntegerFromFloatMutation
    from pymoo.operators.mutation.inversion import InversionMutation
    from pymoo.operators.mutation.nom import NoMutation
    from pymoo.operators.mutation.pm import PM

    MUTATION = [
        ("none", NoMutation),
        ("real_pm", PM),
        #("int_pm", IntegerFromFloatMutation, dict(clazz=PolynomialMutation, eta=20)),
        ("bitflip", BitflipMutation),
        ("perm_inv", InversionMutation)
    ]

    return MUTATION


def get_mutation(name, objectives = 'all', *args, d={}, **kwargs):
    return get_from_list(get_mutation_options(objectives), name, args, {**d, **kwargs})


# =========================================================================================================
# Termination
# =========================================================================================================

def get_termination_options(objectives = 'all'):
        
    from pymoo.termination.default import (DefaultMultiObjectiveTermination,
                                           DefaultSingleObjectiveTermination)
    from pymoo.termination.fmin import MinimumFunctionValueTermination
    from pymoo.termination.max_eval import MaximumFunctionCallTermination
    from pymoo.termination.max_gen import MaximumGenerationTermination
    from pymoo.termination.max_time import TimeBasedTermination
        
    TERMINATION_SINGLE = [
        ("n_evals", MaximumFunctionCallTermination),
        ("n_gen", MaximumGenerationTermination),
        ("fmin", MinimumFunctionValueTermination),
        ("time", TimeBasedTermination),
        ("soo", DefaultSingleObjectiveTermination),
        ]

    TERMINATION_MULTI = [
        ("n_evals", MaximumFunctionCallTermination),
        ("n_gen", MaximumGenerationTermination),
        ("fmin", MinimumFunctionValueTermination),
        ("time", TimeBasedTermination),
        ("moo", DefaultMultiObjectiveTermination),
        ]
    
    return returnOptions(objectives, TERMINATION_SINGLE, TERMINATION_MULTI) 

def get_termination(name, objectives = 'all', *args, d={}, **kwargs):
    return get_from_list(get_termination_options(objectives), name, args, {**d, **kwargs})

# =========================================================================================================
# Problems
# =========================================================================================================

def get_problem_options(objectives = 'all'):    

    from pymoo.problems.dynamic.df import (DF1, DF2, DF3, DF4, DF5, DF6, DF7,
                                           DF8, DF9, DF10, DF11, DF12, DF13,
                                           DF14)
    from pymoo.problems.many import (C1DTLZ1, C1DTLZ3, C2DTLZ2, C3DTLZ1,
                                     C3DTLZ4, DC1DTLZ1, DC1DTLZ3, DC2DTLZ1,
                                     DC2DTLZ3, DC3DTLZ1, DC3DTLZ3, DTLZ1,
                                     DTLZ2, DTLZ3, DTLZ4, DTLZ5, DTLZ6, DTLZ7,
                                     WFG1, WFG2, WFG3, WFG4, WFG5, WFG6, WFG7,
                                     WFG8, WFG9, ConvexDTLZ2, ConvexDTLZ4,
                                     InvertedDTLZ1, ScaledDTLZ1)
    from pymoo.problems.multi import (BNH, CTP1, CTP2, CTP3, CTP4, CTP5, CTP6,
                                      CTP7, CTP8, DASCMOP1, DASCMOP2, DASCMOP3,
                                      DASCMOP4, DASCMOP5, DASCMOP6, DASCMOP7,
                                      DASCMOP8, DASCMOP9, MW1, MW2, MW3, MW4,
                                      MW5, MW6, MW7, MW8, MW9, MW10, MW11,
                                      MW12, MW13, MW14, OSY, SRN, TNK, ZDT1,
                                      ZDT2, ZDT3, ZDT4, ZDT5, ZDT6, Carside,
                                      Kursawe, MODAct, Truss2D, WeldedBeam)
    from pymoo.problems.single import (G1, G2, G3, G4, G5, G6, G7, G8, G9, G10,
                                       G11, G12, G13, G14, G15, G16, G17, G18,
                                       G19, G20, G21, G22, G23, G24, Ackley,
                                       CantileveredBeam, Griewank, Himmelblau,
                                       Knapsack, PressureVessel, Rastrigin,
                                       Rosenbrock, Schwefel, Sphere, Zakharov)
    PROBLEM_SINGLE = [
        ('ackley', Ackley),
        ('g1', G1),
        ('g2', G2),
        ('g3', G3),
        ('g4', G4),
        ('g5', G5),
        ('g6', G6),
        ('g7', G7),
        ('g8', G8),
        ('g9', G9),
        ('g10', G10),
        ('g11', G11),
        ('g12', G12),
        ('g13', G13),
        ('g14', G14),
        ('g15', G15),
        ('g16', G16),
        ('g17', G17),
        ('g18', G18),
        ('g19', G19),
        ('g20', G20),
        ('g21', G21),
        ('g22', G22),
        ('g23', G23),
        ('g24', G24),
        ('cantilevered_beam', CantileveredBeam),
        ('griewank', Griewank),
        ('himmelblau', Himmelblau),
        ('knp', Knapsack),
        ('pressure_vessel', PressureVessel),
        ('rastrigin', Rastrigin),
        ('rosenbrock', Rosenbrock),
        ('schwefel', Schwefel),
        ('sphere', Sphere),
        ('zakharov', Zakharov),
        ]

    PROBLEM_MULTI = [
        ('bnh', BNH),
        ('carside', Carside),
        ('ctp1', CTP1),
        ('ctp2', CTP2),
        ('ctp3', CTP3),
        ('ctp4', CTP4),
        ('ctp5', CTP5),
        ('ctp6', CTP6),
        ('ctp7', CTP7),
        ('ctp8', CTP8),
        ('dascmop1', DASCMOP1),
        ('dascmop2', DASCMOP2),
        ('dascmop3', DASCMOP3),
        ('dascmop4', DASCMOP4),
        ('dascmop5', DASCMOP5),
        ('dascmop6', DASCMOP6),
        ('dascmop7', DASCMOP7),
        ('dascmop8', DASCMOP8),
        ('dascmop9', DASCMOP9),
        ('df1', DF1),
        ('df2', DF2),
        ('df3', DF3),
        ('df4', DF4),
        ('df5', DF5),
        ('df6', DF6),
        ('df7', DF7),
        ('df8', DF8),
        ('df9', DF9),
        ('df10', DF10),
        ('df11', DF11),
        ('df12', DF12),
        ('df13', DF13),
        ('df14', DF14),
        ('modact', MODAct),
        ('mw1', MW1),
        ('mw2', MW2),
        ('mw3', MW3),
        ('mw4', MW4),
        ('mw5', MW5),
        ('mw6', MW6),
        ('mw7', MW7),
        ('mw8', MW8),
        ('mw9', MW9),
        ('mw10', MW10),
        ('mw11', MW11),
        ('mw12', MW12),
        ('mw13', MW13),
        ('mw14', MW14),
        ('dtlz1^-1', InvertedDTLZ1),
        ('dtlz1', DTLZ1),
        ('dtlz2', DTLZ2),
        ('dtlz3', DTLZ3),
        ('dtlz4', DTLZ4),
        ('dtlz5', DTLZ5),
        ('dtlz6', DTLZ6),
        ('dtlz7', DTLZ7),
        ('convex_dtlz2', ConvexDTLZ2),
        ('convex_dtlz4', ConvexDTLZ4),
        ('sdtlz1', ScaledDTLZ1),
        ('c1dtlz1', C1DTLZ1),
        ('c1dtlz3', C1DTLZ3),
        ('c2dtlz2', C2DTLZ2),
        ('c3dtlz1', C3DTLZ1),
        ('c3dtlz4', C3DTLZ4),
        ('dc1dtlz1', DC1DTLZ1),
        ('dc1dtlz3', DC1DTLZ3),
        ('dc2dtlz1', DC2DTLZ1),
        ('dc2dtlz3', DC2DTLZ3),
        ('dc3dtlz1', DC3DTLZ1),
        ('dc3dtlz3', DC3DTLZ3),
        ('kursawe', Kursawe),
        ('osy', OSY),
        ('srn', SRN),
        ('tnk', TNK),
        ('truss2d', Truss2D),
        ('welded_beam', WeldedBeam),
        ('zdt1', ZDT1),
        ('zdt2', ZDT2),
        ('zdt3', ZDT3),
        ('zdt4', ZDT4),
        ('zdt5', ZDT5),
        ('zdt6', ZDT6),
        ('wfg1', WFG1),
        ('wfg2', WFG2),
        ('wfg3', WFG3),
        ('wfg4', WFG4),
        ('wfg5', WFG5),
        ('wfg6', WFG6),
        ('wfg7', WFG7),
        ('wfg8', WFG8),
        ('wfg9', WFG9),
    ]

    return returnOptions(objectives, PROBLEM_SINGLE, PROBLEM_MULTI)

def get_problem(name, *args, **kwargs):
    name = name.lower()

    if name.startswith("bbob-"):
        from pymoo.vendor.vendor_coco import COCOProblem
        return COCOProblem(name.lower(), **kwargs)

    from pymoo.problems.dynamic.df import (DF1, DF2, DF3, DF4, DF5, DF6, DF7,
                                           DF8, DF9, DF10, DF11, DF12, DF13,
                                           DF14)
    from pymoo.problems.many import (C1DTLZ1, C1DTLZ3, C2DTLZ2, C3DTLZ1,
                                     C3DTLZ4, DC1DTLZ1, DC1DTLZ3, DC2DTLZ1,
                                     DC2DTLZ3, DC3DTLZ1, DC3DTLZ3, DTLZ1,
                                     DTLZ2, DTLZ3, DTLZ4, DTLZ5, DTLZ6, DTLZ7,
                                     WFG1, WFG2, WFG3, WFG4, WFG5, WFG6, WFG7,
                                     WFG8, WFG9, ConvexDTLZ2, ConvexDTLZ4,
                                     InvertedDTLZ1, ScaledDTLZ1)
    from pymoo.problems.multi import (BNH, CTP1, CTP2, CTP3, CTP4, CTP5, CTP6,
                                      CTP7, CTP8, DASCMOP1, DASCMOP2, DASCMOP3,
                                      DASCMOP4, DASCMOP5, DASCMOP6, DASCMOP7,
                                      DASCMOP8, DASCMOP9, MW1, MW2, MW3, MW4,
                                      MW5, MW6, MW7, MW8, MW9, MW10, MW11,
                                      MW12, MW13, MW14, OSY, SRN, TNK, ZDT1,
                                      ZDT2, ZDT3, ZDT4, ZDT5, ZDT6, Carside,
                                      Kursawe, MODAct, Truss2D, WeldedBeam)
    from pymoo.problems.single import (G1, G2, G3, G4, G5, G6, G7, G8, G9, G10,
                                       G11, G12, G13, G14, G15, G16, G17, G18,
                                       G19, G20, G21, G22, G23, G24, Ackley,
                                       CantileveredBeam, Griewank, Himmelblau,
                                       Knapsack, PressureVessel, Rastrigin,
                                       Rosenbrock, Schwefel, Sphere, Zakharov)

    PROBLEM = {
        'ackley': Ackley,
        'bnh': BNH,
        'carside': Carside,
        'ctp1': CTP1,
        'ctp2': CTP2,
        'ctp3': CTP3,
        'ctp4': CTP4,
        'ctp5': CTP5,
        'ctp6': CTP6,
        'ctp7': CTP7,
        'ctp8': CTP8,
        'dascmop1': DASCMOP1,
        'dascmop2': DASCMOP2,
        'dascmop3': DASCMOP3,
        'dascmop4': DASCMOP4,
        'dascmop5': DASCMOP5,
        'dascmop6': DASCMOP6,
        'dascmop7': DASCMOP7,
        'dascmop8': DASCMOP8,
        'dascmop9': DASCMOP9,
        'df1': DF1,
        'df2': DF2,
        'df3': DF3,
        'df4': DF4,
        'df5': DF5,
        'df6': DF6,
        'df7': DF7,
        'df8': DF8,
        'df9': DF9,
        'df10': DF10,
        'df11': DF11,
        'df12': DF12,
        'df13': DF13,
        'df14': DF14,
        'modact': MODAct,
        'mw1': MW1,
        'mw2': MW2,
        'mw3': MW3,
        'mw4': MW4,
        'mw5': MW5,
        'mw6': MW6,
        'mw7': MW7,
        'mw8': MW8,
        'mw9': MW9,
        'mw10': MW10,
        'mw11': MW11,
        'mw12': MW12,
        'mw13': MW13,
        'mw14': MW14,
        'dtlz1^-1': InvertedDTLZ1,
        'dtlz1': DTLZ1,
        'dtlz2': DTLZ2,
        'dtlz3': DTLZ3,
        'dtlz4': DTLZ4,
        'dtlz5': DTLZ5,
        'dtlz6': DTLZ6,
        'dtlz7': DTLZ7,
        'convex_dtlz2': ConvexDTLZ2,
        'convex_dtlz4': ConvexDTLZ4,
        'sdtlz1': ScaledDTLZ1,
        'c1dtlz1': C1DTLZ1,
        'c1dtlz3': C1DTLZ3,
        'c2dtlz2': C2DTLZ2,
        'c3dtlz1': C3DTLZ1,
        'c3dtlz4': C3DTLZ4,
        'dc1dtlz1': DC1DTLZ1,
        'dc1dtlz3': DC1DTLZ3,
        'dc2dtlz1': DC2DTLZ1,
        'dc2dtlz3': DC2DTLZ3,
        'dc3dtlz1': DC3DTLZ1,
        'dc3dtlz3': DC3DTLZ3,
        'cantilevered_beam': CantileveredBeam,
        'griewank': Griewank,
        'himmelblau': Himmelblau,
        'knp': Knapsack,
        'kursawe': Kursawe,
        'osy': OSY,
        'pressure_vessel': PressureVessel,
        'rastrigin': Rastrigin,
        'rosenbrock': Rosenbrock,
        'schwefel': Schwefel,
        'sphere': Sphere,
        'srn': SRN,
        'tnk': TNK,
        'truss2d': Truss2D,
        'welded_beam': WeldedBeam,
        'zakharov': Zakharov,
        'zdt1': ZDT1,
        'zdt2': ZDT2,
        'zdt3': ZDT3,
        'zdt4': ZDT4,
        'zdt5': ZDT5,
        'zdt6': ZDT6,
        'g1': G1,
        'g2': G2,
        'g3': G3,
        'g4': G4,
        'g5': G5,
        'g6': G6,
        'g7': G7,
        'g8': G8,
        'g9': G9,
        'g10': G10,
        'g11': G11,
        'g12': G12,
        'g13': G13,
        'g14': G14,
        'g15': G15,
        'g16': G16,
        'g17': G17,
        'g18': G18,
        'g19': G19,
        'g20': G20,
        'g21': G21,
        'g22': G22,
        'g23': G23,
        'g24': G24,
        'wfg1': WFG1,
        'wfg2': WFG2,
        'wfg3': WFG3,
        'wfg4': WFG4,
        'wfg5': WFG5,
        'wfg6': WFG6,
        'wfg7': WFG7,
        'wfg8': WFG8,
        'wfg9': WFG9
    }

    if name not in PROBLEM:
        raise Exception("Problem not found.")

    return PROBLEM[name](*args, **kwargs)

# =========================================================================================================
# Weights
# =========================================================================================================

from pymoo.util.ref_dirs.energy import RieszEnergyReferenceDirectionFactory
from pymoo.util.ref_dirs.energy_layer import \
    LayerwiseRieszEnergyReferenceDirectionFactory
from pymoo.util.ref_dirs.reduction import \
    ReductionBasedReferenceDirectionFactory
from pymoo.util.reference_direction import MultiLayerReferenceDirectionFactory

def get_reference_direction_options(objectives = 'all'):
        
    from pymoo.util.reference_direction import UniformReferenceDirectionFactory

    REFERENCE_DIRECTIONS = [
        ("(das-dennis|uniform)", UniformReferenceDirectionFactory),
        ("multi-layer", MultiLayerReferenceDirectionFactory),
        ("(energy|riesz)", RieszEnergyReferenceDirectionFactory),
        ("(layer-energy|layer-riesz)", LayerwiseRieszEnergyReferenceDirectionFactory),
        ("red", ReductionBasedReferenceDirectionFactory)
    ]

    return REFERENCE_DIRECTIONS


def get_reference_directions(name, *args, d={}, **kwargs):
    return get_from_list(get_reference_direction_options(), name, args, {**d, **kwargs}).do()


# =========================================================================================================
# Visualization
# =========================================================================================================

def get_visualization_options(objectives = 'all'):
        
    from pymoo.visualization.fitness_landscape import FitnessLandscape
    from pymoo.visualization.heatmap import Heatmap
    from pymoo.visualization.pcp import PCP
    from pymoo.visualization.petal import Petal
    from pymoo.visualization.radar import Radar
    from pymoo.visualization.radviz import Radviz
    from pymoo.visualization.scatter import Scatter
    from pymoo.visualization.star_coordinate import StarCoordinate

    VISUALIZATION = [
        ("scatter", Scatter),
        ("heatmap", Heatmap),
        ("pcp", PCP),
        ("petal", Petal),
        ("radar", Radar),
        ("radviz", Radviz),
        ("star", StarCoordinate),
        ("fitness-landscape", FitnessLandscape)
    ]

    return VISUALIZATION


def get_visualization(name, *args, d={}, **kwargs):
    return get_from_list(get_visualization_options(), name, args, {**d, **kwargs})


# =========================================================================================================
# Performance Indicator
# =========================================================================================================

def get_performance_indicator_options(objectives = 'all'):
        
    from pymoo.indicators.gd import GD
    from pymoo.indicators.gd_plus import GDPlus
    from pymoo.indicators.hv import Hypervolume
    from pymoo.indicators.igd import IGD
    from pymoo.indicators.igd_plus import IGDPlus
    from pymoo.indicators.rmetric import RMetric

    class BEST():
        def __init__(self, *args, **kwargs):
            pass
        def do(self, lst, *args, **kwargs):
            pass
                 
    PERFORMANCE_INDICATOR_SINGLE = [
        ("best", BEST)
    ]
        
    PERFORMANCE_INDICATOR_MULTI = [
        ("gd", GD),
        ("gd+", GDPlus),
        ("igd", IGD),
        ("igd+", IGDPlus),
        ("hv", Hypervolume),
        ("rmetric", RMetric)
    ]
    
    return returnOptions(objectives, PERFORMANCE_INDICATOR_SINGLE, PERFORMANCE_INDICATOR_MULTI)


def get_performance_indicator(name, *args, d={}, **kwargs):
    return get_from_list(get_performance_indicator_options(), name, args, {**d, **kwargs})


# =========================================================================================================
# DECOMPOSITION
# =========================================================================================================

def get_decomposition_options(objectives = 'all'):
        
    from pymoo.decomposition.aasf import AASF
    from pymoo.decomposition.asf import ASF
    from pymoo.decomposition.pbi import PBI
    from pymoo.decomposition.perp_dist import PerpendicularDistance
    from pymoo.decomposition.tchebicheff import Tchebicheff
    from pymoo.decomposition.weighted_sum import WeightedSum

    DECOMPOSITION = [
        ("weighted-sum", WeightedSum),
        ("tchebi", Tchebicheff),
        ("pbi", PBI),
        ("asf", ASF),
        ("aasf", AASF),
        ("perp_dist", PerpendicularDistance)
    ]

    return DECOMPOSITION


def get_decomposition(name, *args, d={}, **kwargs):
    return get_from_list(get_decomposition_options(), name, args, {**d, **kwargs})


# =========================================================================================================
# DECISION MAKING
# =========================================================================================================

def get_decision_making_options(objectives = 'all'):
        
    from pymoo.mcdm.high_tradeoff import HighTradeoffPoints
    from pymoo.mcdm.pseudo_weights import PseudoWeights

    DECISION_MAKING = [
        ("high-tradeoff", HighTradeoffPoints),
        ("pseudo-weights", PseudoWeights)
    ]

    return DECISION_MAKING


def get_decision_making(name, *args, d={}, **kwargs):
    return get_from_list(get_decision_making_options(), name, args, {**d, **kwargs})

