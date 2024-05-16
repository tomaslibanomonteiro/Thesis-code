
def returnObjectOrOptions(name, single_dict, multi_dict, *args, **kwargs):
    name = name.lower()

    merged_dict = {**single_dict, **multi_dict}
    
    if name == "all_options":
        return merged_dict
    elif name == "soo_options":
        return single_dict
    elif name == "moo_options":
        return multi_dict    
    elif name in merged_dict:
        # try to instantiate the object with kwargs, if it fails, try with args_dict
        args_dict = kwargs.pop('args_dict', None)
        try:
            kwargs.update(args_dict) if args_dict is not None else None
            obj = merged_dict[name](*args, **kwargs) #@IgnoreException
        except:
            obj = merged_dict[name](*args, **args_dict) if args_dict is not None else merged_dict[name](*args)
        return obj
    else:
        raise Exception("Object '%s' for not found in %s. If you want options, call with 'all_options', 'all_soo_options' or 'all_moo_options'" % (name, list(merged_dict.keys())))
    
# =========================================================================================================
# Algorithms
# =========================================================================================================

def get_algorithm(name, *args, **kwargs):
        
    from pymoo.algorithms.moo.ctaea import CTAEA
    from pymoo.algorithms.moo.moead import MOEAD
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.nsga3 import NSGA3
    # from pymoo.algorithms.moo.rnsga2 import RNSGA2 # needs a numpy array to set, cannot be done through the app
    # from pymoo.algorithms.moo.rnsga3 import RNSGA3 # needs a numpy array to set, cannot be done through the app
    from pymoo.algorithms.moo.unsga3 import UNSGA3
    from pymoo.algorithms.soo.nonconvex.cmaes import CMAES
    from pymoo.algorithms.soo.nonconvex.de import DE
    from pymoo.algorithms.soo.nonconvex.ga import GA
    from pymoo.algorithms.soo.nonconvex.nelder import NelderMead
    from pymoo.algorithms.soo.nonconvex.pattern import PatternSearch
    from pymoo.algorithms.soo.nonconvex.pso import PSO
    from pymoo.algorithms.soo.nonconvex.brkga import BRKGA

    ALGORITHMS_SINGLE = {
        "ga": GA,
        "de": DE,
        "nelder-mead": NelderMead,
        "pattern-search": PatternSearch,
        "cmaes": CMAES,
        "pso": PSO,
        "brkga": BRKGA,
    }
    
    ALGORITHMS_MULTI = {
        "nsga2": NSGA2,
        "nsga3": NSGA3,
        "unsga3": UNSGA3,
        "moead": MOEAD,
        "ctaea": CTAEA,
    }

    return returnObjectOrOptions(name, ALGORITHMS_SINGLE, ALGORITHMS_MULTI, *args, **kwargs)

# =========================================================================================================
# Sampling
# =========================================================================================================

def get_sampling(name, *args, **kwargs):
        
    from pymoo.operators.sampling.lhs import LHS
    from pymoo.operators.sampling.rnd import (BinaryRandomSampling,
                                              FloatRandomSampling,
                                              PermutationRandomSampling)
    
    SAMPLING = {
        "real_random": FloatRandomSampling,
        "real_lhs": LHS,
        "bin_random": BinaryRandomSampling,
        "perm_random": PermutationRandomSampling
    }

    return returnObjectOrOptions(name, SAMPLING, SAMPLING, *args, **kwargs)

# =========================================================================================================
# Selection
# =========================================================================================================

def get_selection(name, *args, **kwargs):
        
    from pymoo.operators.selection.rnd import RandomSelection
    from utils.useful_classes import (TournamentByCVAndFitness, RestrictedMatingCTAEA, BinaryTournament, 
                                        TournamentByCVThenRandom, TournamentByRankAndRefLineDist)
    SELECTION_SINGLE = {
        "random": RandomSelection,
        "tournament_by_cv_and_fitness": TournamentByCVAndFitness  # ga
    }
    
    SELECTION_MULTI = {
        "restricted_mating_ctaea": RestrictedMatingCTAEA,  # ctaea
        "binary_tournament": BinaryTournament,  # nsga2
        "tournament_by_cv_then_random": TournamentByCVThenRandom,  # nsga3
        "tournament_by_rank_and_ref_line_dist": TournamentByRankAndRefLineDist  # unsga3
    }

    return returnObjectOrOptions(name, SELECTION_SINGLE, SELECTION_MULTI, *args, **kwargs)


# =========================================================================================================
# Crossover
# =========================================================================================================

def get_crossover(name, *args, **kwargs):
        
    from pymoo.operators.crossover.dex import DEX
    from pymoo.operators.crossover.erx import EdgeRecombinationCrossover
    from pymoo.operators.crossover.expx import ExponentialCrossover
    from pymoo.operators.crossover.hux import HalfUniformCrossover
    from pymoo.operators.crossover.ox import OrderCrossover
    from pymoo.operators.crossover.pcx import PCX
    from pymoo.operators.crossover.pntx import PointCrossover
    from pymoo.operators.crossover.sbx import SBX
    from pymoo.operators.crossover.ux import UniformCrossover
    
    CROSSOVER = {
        "real_sbx": SBX,
        "real_de": DEX,
        "real_pcx": PCX,
        "(real|bin|int)_ux": UniformCrossover,
        "(bin|int)_hux": HalfUniformCrossover,
        "(real|bin|int)_exp": ExponentialCrossover,
        "(real|bin|int)_k_point": PointCrossover,
        "perm_ox": OrderCrossover,
        "perm_erx": EdgeRecombinationCrossover
    }

    return returnObjectOrOptions(name, CROSSOVER, CROSSOVER, *args, **kwargs)

# =========================================================================================================
# Mutation
# =========================================================================================================

def get_mutation(name, *args, **kwargs):
        
    from pymoo.operators.mutation.bitflip import BitflipMutation
    from pymoo.operators.mutation.inversion import InversionMutation
    from pymoo.operators.mutation.nom import NoMutation
    from pymoo.operators.mutation.pm import PM

    MUTATION = {
        "none": NoMutation,
        "real_pm": PM,
        "bitflip": BitflipMutation,
        "perm_inv": InversionMutation
    }

    return returnObjectOrOptions(name, MUTATION, MUTATION, *args, **kwargs)


# =========================================================================================================
# Termination
# =========================================================================================================

def get_termination(name, *args, **kwargs):
            
    from pymoo.termination.default import (DefaultMultiObjectiveTermination,
                                           DefaultSingleObjectiveTermination)
    from pymoo.termination.fmin import MinimumFunctionValueTermination
    from pymoo.termination.max_eval import MaximumFunctionCallTermination
    from pymoo.termination.max_gen import MaximumGenerationTermination
    from pymoo.termination.max_time import TimeBasedTermination
    from utils.useful_classes import MinFitnessTermination, StaledBestTermination
    from thesis.pso.pso_classes import PSOTermination
    
    TERMINATION_SINGLE = {
        "n_eval": MaximumFunctionCallTermination,
        "n_gen": MaximumGenerationTermination,
        "fmin": MinimumFunctionValueTermination,
        "time": TimeBasedTermination,
        "soo": DefaultSingleObjectiveTermination,
        "min_fitness": MinFitnessTermination,
        "staled_best": StaledBestTermination,
        "pso_termination": PSOTermination #!
    }

    TERMINATION_MULTI = {
        "n_eval": MaximumFunctionCallTermination,
        "n_gen": MaximumGenerationTermination,
        "fmin": MinimumFunctionValueTermination,
        "time": TimeBasedTermination,
        "moo": DefaultMultiObjectiveTermination,
    }
    
    return returnObjectOrOptions(name, TERMINATION_SINGLE, TERMINATION_MULTI, *args, **kwargs) 

# =========================================================================================================
# Problems
# =========================================================================================================

def get_problem(name, *args, **kwargs):    

    from pymoo.problems.dynamic.df import (DF1, DF2, DF3, DF4, DF5, DF6, DF7,
                                           DF8, DF9, DF10, DF11, DF12, DF13,
                                           DF14)
    #InvertedDTLZ1 not well implemented
    # ConvexDTLZ2 and ConvexDTLZ4 are just dtlz with different args
    from pymoo.problems.many import (C1DTLZ1, C1DTLZ3, C2DTLZ2, C3DTLZ1,
                                     C3DTLZ4, DC1DTLZ1, DC1DTLZ3, DC2DTLZ1,
                                     DC2DTLZ3, DC3DTLZ1, DC3DTLZ3, DTLZ1,
                                     DTLZ2, DTLZ3, DTLZ4, DTLZ5, DTLZ6, DTLZ7) #WFG not giving consistent pfs 
    # MODAct needs to install module
    from pymoo.problems.multi import (BNH, CTP1, CTP2, CTP3, CTP4, CTP5, CTP6,
                                      CTP7, CTP8, DASCMOP1, DASCMOP2, DASCMOP3,
                                      DASCMOP4, DASCMOP5, DASCMOP6, DASCMOP7,
                                      DASCMOP8, DASCMOP9, MW1, MW2, MW3, MW4,
                                      MW5, MW6, MW7, MW8, MW9, MW10, MW11,
                                      MW12, MW13, MW14, OSY, SRN, TNK, ZDT1,
                                      ZDT2, ZDT3, ZDT4, ZDT5, ZDT6, Carside,
                                      Kursawe, Truss2D, WeldedBeam) 
    from pymoo.problems.single import (G1, G2, G3, G4, G5, G6, G7, G8, G9, G10,
                                       G11, G12, G13, G14, G15, G16, G17, G18,
                                       G19, G20, G21, G22, G23, G24, Ackley,
                                       CantileveredBeam, Himmelblau, PressureVessel,
                                       Schwefel, Sphere, Zakharov) # Griewank, Rastrigin, Rosenbrock overwritten to set xl and xu
    from utils.useful_classes import RandomKnapsackMulti, RandomKnapsackSingle, ScaledDTLZ, Griewank, Rastrigin, Rosenbrock
    
    PROBLEM_SINGLE = {
        "ackley": Ackley,
        "g1": G1,
        "g2": G2,
        "g3": G3,
        "g4": G4,
        "g5": G5,
        "g6": G6,
        "g7": G7,
        "g8": G8,
        "g9": G9,
        "g10": G10,
        "g11": G11,
        "g12": G12,
        "g13": G13,
        "g14": G14,
        "g15": G15,
        "g16": G16,
        "g17": G17,
        "g18": G18,
        "g19": G19,
        "g20": G20,
        "g21": G21,
        "g22": G22,
        "g23": G23,
        "g24": G24,
        "cantilevered_beam": CantileveredBeam,
        "griewank": Griewank,
        "himmelblau": Himmelblau,
        "soo_rnd_knp": RandomKnapsackSingle,
        "pressure_vessel": PressureVessel,
        "rastrigin": Rastrigin,
        "rosenbrock": Rosenbrock,
        "schwefel": Schwefel,
        "sphere": Sphere,
        "zakharov": Zakharov,
    }

    PROBLEM_MULTI = {
        "bnh": BNH,
        "moo_rnd_knp": RandomKnapsackMulti,
        "carside": Carside,
        "ctp1": CTP1,
        "ctp2": CTP2,
        "ctp3": CTP3,
        "ctp4": CTP4,
        "ctp5": CTP5,
        "ctp6": CTP6,
        "ctp7": CTP7,
        "ctp8": CTP8,
        "dascmop1": DASCMOP1,
        "dascmop2": DASCMOP2,
        "dascmop3": DASCMOP3,
        "dascmop4": DASCMOP4,
        "dascmop5": DASCMOP5,
        "dascmop6": DASCMOP6,
        "dascmop7": DASCMOP7,
        "dascmop8": DASCMOP8,
        "dascmop9": DASCMOP9,
        "df1": DF1,
        "df2": DF2,
        "df3": DF3,
        "df4": DF4,
        "df5": DF5,
        "df6": DF6,
        "df7": DF7,
        "df8": DF8,
        "df9": DF9,
        "df10": DF10,
        "df11": DF11,
        "df12": DF12,
        "df13": DF13,
        "df14": DF14,
        "mw1": MW1,
        "mw2": MW2,
        "mw3": MW3,
        "mw4": MW4,
        "mw5": MW5,
        "mw6": MW6,
        "mw7": MW7,
        "mw8": MW8,
        "mw9": MW9,
        "mw10": MW10,
        "mw11": MW11,
        "mw12": MW12,
        "mw13": MW13,
        "mw14": MW14,
        "dtlz1": DTLZ1,
        "dtlz2": DTLZ2,
        "dtlz3": DTLZ3,
        "dtlz4": DTLZ4,
        "dtlz5": DTLZ5,
        "dtlz6": DTLZ6,
        "dtlz7": DTLZ7,
        "scaled_dtlz": ScaledDTLZ,
        "c1dtlz1": C1DTLZ1,
        "c1dtlz3": C1DTLZ3,
        "c2dtlz2": C2DTLZ2,
        "c3dtlz1": C3DTLZ1,
        "c3dtlz4": C3DTLZ4,
        "dc1dtlz1": DC1DTLZ1,
        "dc1dtlz3": DC1DTLZ3,
        "dc2dtlz1": DC2DTLZ1,
        "dc2dtlz3": DC2DTLZ3,
        "dc3dtlz1": DC3DTLZ1,
        "dc3dtlz3": DC3DTLZ3,
        "kursawe": Kursawe,
        "osy": OSY,
        "srn": SRN,
        "tnk": TNK,
        "truss2d": Truss2D,
        "welded_beam": WeldedBeam,
        "zdt1": ZDT1,
        "zdt2": ZDT2,
        "zdt3": ZDT3,
        "zdt4": ZDT4,
        "zdt5": ZDT5,
        "zdt6": ZDT6,
    }

    return returnObjectOrOptions(name, PROBLEM_SINGLE, PROBLEM_MULTI, *args, **kwargs)

# =========================================================================================================
# Reference Directions
# =========================================================================================================


def get_reference_directions(name, *args, **kwargs):
        
    from pymoo.util.ref_dirs.energy import RieszEnergyReferenceDirectionFactory
    from pymoo.util.ref_dirs.energy_layer import \
        LayerwiseRieszEnergyReferenceDirectionFactory
    from pymoo.util.ref_dirs.reduction import \
        ReductionBasedReferenceDirectionFactory
    from pymoo.util.reference_direction import UniformReferenceDirectionFactory
                
    REFERENCE_DIRECTIONS = {
        "das-dennis": UniformReferenceDirectionFactory,
        "energy": RieszEnergyReferenceDirectionFactory,
        "layer-energy": LayerwiseRieszEnergyReferenceDirectionFactory,
        "red": ReductionBasedReferenceDirectionFactory,
    }

    ref_dirs = returnObjectOrOptions(name, {}, REFERENCE_DIRECTIONS, *args, **kwargs)
    if isinstance(ref_dirs, dict):
        return ref_dirs
    else:
        return ref_dirs.do()

# =========================================================================================================
# Performance Indicator
# =========================================================================================================

def get_performance_indicator(name, *args, **kwargs):
        
    from pymoo.indicators.gd import GD
    from pymoo.indicators.gd_plus import GDPlus
    from pymoo.indicators.igd import IGD
    from pymoo.indicators.igd_plus import IGDPlus
    from pymoo.indicators.rmetric import RMetric
    from utils.useful_classes import BestFitness, minusHypervolume, AvgPopFitness, MinusGoalAchieved, EvalsOnGoal
    from thesis.pso.pso_classes import EvalsOnGoalPSO, MinusGoalAchievedPSO
                 
    PERFORMANCE_INDICATOR_SINGLE = {
        "best": BestFitness,
        "avg_fitness": AvgPopFitness,
        "-goal_achieved": MinusGoalAchieved,
        "evals_on_goal": EvalsOnGoal,
        "-goal_achieved_pso": MinusGoalAchievedPSO,
        "evals_on_goal_pso": EvalsOnGoalPSO
    }
        
    PERFORMANCE_INDICATOR_MULTI = {
        "gd": GD,
        "gd+": GDPlus,
        "igd": IGD,
        "igd+": IGDPlus,
        "-hv": minusHypervolume,
        "rmetric": RMetric
    }
    
    return returnObjectOrOptions(name, PERFORMANCE_INDICATOR_SINGLE, PERFORMANCE_INDICATOR_MULTI, *args, **kwargs)

# =========================================================================================================
# Decomposition
# =========================================================================================================

def get_decomposition(name, *args, **kwargs):
        
    from pymoo.decomposition.aasf import AASF
    from pymoo.decomposition.asf import ASF
    from pymoo.decomposition.pbi import PBI
    from pymoo.decomposition.perp_dist import PerpendicularDistance
    from pymoo.decomposition.tchebicheff import Tchebicheff
    from pymoo.decomposition.weighted_sum import WeightedSum

    DECOMPOSITION_MULTI = {
        "weighted-sum": WeightedSum,
        "tchebi": Tchebicheff,
        "pbi": PBI,
        "asf": ASF,
        "aasf": AASF,
        "perp_dist": PerpendicularDistance
    }

    return returnObjectOrOptions(name, {}, DECOMPOSITION_MULTI, *args, **kwargs)

# =========================================================================================================
# VISUALIZATION TECHNIQUES #!?
# =========================================================================================================

def get_visualization_options(name, *args, **kwargs):
        
    from pymoo.visualization.fitness_landscape import FitnessLandscape
    from pymoo.visualization.heatmap import Heatmap
    from pymoo.visualization.pcp import PCP
    from pymoo.visualization.petal import Petal
    from pymoo.visualization.radar import Radar
    from pymoo.visualization.radviz import Radviz
    from pymoo.visualization.scatter import Scatter
    from pymoo.visualization.star_coordinate import StarCoordinate

    VISUALIZATION = {
        "scatter": Scatter,
        "heatmap": Heatmap,
        "pcp": PCP,
        "petal": Petal,
        "radar": Radar,
        "radviz": Radviz,
        "star": StarCoordinate,
        "fitness-landscape": FitnessLandscape
    }

    return returnObjectOrOptions(name, VISUALIZATION, VISUALIZATION, *args, **kwargs)
