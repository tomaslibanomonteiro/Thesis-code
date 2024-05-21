


from pymoo.optimize import minimize
from pymoo.termination.default import DefaultMultiObjectiveTermination

from problem import RandomMultiMixedTSP
from algorithm import algorithm
from plot import plotTSP

def main():

    termination = DefaultMultiObjectiveTermination()
    problem = RandomMultiMixedTSP()

    res = minimize(
        problem,
        algorithm,
        termination,
        seed=1,
    )
    
    print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))
    plotTSP(problem, res.X, res.F)
    
if __name__ == '__main__':
    main()