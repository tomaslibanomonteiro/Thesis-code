import csv

from pandas import read_csv
# import numpy as np
# import time

# from pymoo.algorithms.moo.nsga2 import NSGA2 
# from pymoo.algorithms.moo.nsga3 import NSGA3
# from pymoo.algorithms.moo.moead import MOEAD
# from pymoo.util.ref_dirs import get_reference_directions
# from pymoo.problems import get_problem
# from pymoo.optimize import minimize
# from pymoo.indicators.igd import IGD
# from pymoo.core.callback import Callback

def main():
    # Define the data to write to the output file
    data = [
        ['John', 'Doe', 28],
        ['Jane', 'Doe', 25],
        ['Bob', 'Smith', 32]
    ]
    
    print("hello")

    # Define the header for the output file
    header = ['First Name', 'Last Name', 'Age']

    # Open the output file in write mode, open with full path
    with open('test1234.csv', mode='w', newline='') as file:

        # Create a CSV writer object
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(header)

        # Write the data rows
        for row in data:
            writer.writerow(row)
        
if __name__ == '__main__':
    main()