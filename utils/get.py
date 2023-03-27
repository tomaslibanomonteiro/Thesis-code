import re

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

        elif len(l[i]) == 3:
            name, clazz, default_kwargs = l[i]

            # overwrite the default if provided
            for key, val in kwargs.items():
                default_kwargs[key] = val
            kwargs = default_kwargs

        return clazz(*args, **kwargs)
    else:
        raise Exception("Object '%s' for not found in %s" % (name, [e[0] for e in l]))

def get_algorithm_options():
    from pymoo.algorithms.moo.ctaea import CTAEA
    from pymoo.algorithms.moo.moead import MOEAD
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.algorithms.moo.rnsga2 import RNSGA2
    from pymoo.algorithms.moo.rnsga3 import RNSGA3
    from pymoo.algorithms.soo.nonconvex.de import DE
    from pymoo.algorithms.soo.nonconvex.ga import GA
    from pymoo.algorithms.moo.unsga3 import UNSGA3
    # from pymoo.algorithms.soo.nonconvex.nelder_mead import NelderMead
    from pymoo.algorithms.soo.nonconvex.cmaes import CMAES
    from pymoo.algorithms.soo.nonconvex.brkga import BRKGA
    # from pymoo.algorithms.soo.nonconvex.pattern_search import PatternSearch
    from pymoo.algorithms.soo.nonconvex.pso import PSO

    ALGORITHMS = [
        ("ga", GA),
        ("brkga", BRKGA),
        ("de", DE),
        # ("nelder-mead", NelderMead),
        # ("pattern-search", PatternSearch),
        ("cmaes", CMAES),
        ("pso", PSO),
        ("nsga2", NSGA2),
        ("rnsga2", RNSGA2),
        ("nsga3", NSGA3),
        ("unsga3", UNSGA3),
        ("rnsga3", RNSGA3),
        ("moead", MOEAD),
        ("ctaea", CTAEA),
    ]

    return ALGORITHMS

def get_algorithm(name, *args, d={}, **kwargs):
    return get_from_list(get_algorithm_options(), name, args, {**d, **kwargs})

def get_reference_direction_options():
    from pymoo.util.reference_direction import UniformReferenceDirectionFactory
    from pymoo.util.reference_direction import MultiLayerReferenceDirectionFactory
    from pymoo.util.ref_dirs.reduction import ReductionBasedReferenceDirectionFactory
    from pymoo.util.ref_dirs.energy import RieszEnergyReferenceDirectionFactory
    from pymoo.util.ref_dirs.energy_layer import LayerwiseRieszEnergyReferenceDirectionFactory

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
# Performance Indicator
# =========================================================================================================


def get_performance_indicator_options():
    from pymoo.indicators.gd import GD
    from pymoo.indicators.gd_plus import GDPlus
    from pymoo.indicators.igd import IGD
    from pymoo.indicators.igd_plus import IGDPlus
    from pymoo.indicators.hv import Hypervolume
    from pymoo.indicators.rmetric import RMetric

    PERFORMANCE_INDICATOR = [
        ("gd", GD),
        ("gd+", GDPlus),
        ("igd", IGD),
        ("igd+", IGDPlus),
        ("hv", Hypervolume),
        ("rmetric", RMetric)
    ]
    return PERFORMANCE_INDICATOR


def get_performance_indicator(name, *args, d={}, **kwargs):
    return get_from_list(get_performance_indicator_options(), name, args, {**d, **kwargs})