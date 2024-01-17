# import the pickle file

import pickle

# open the pickle file and load the data
with open('parameters.pickle', 'rb') as f:
    data = pickle.load(f)
    while(1):
        continue