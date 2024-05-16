import pickle

# Load the pickle file
with open('soo_parameters.pickle', 'rb') as file:
    data = pickle.load(file)

from backend.defaults import Defaults

def_dict = Defaults(moo=False).parameters

# Save the modified data back to a pickle file
with open('soo_parameters_new.pickle', 'wb') as file:
    pickle.dump(data, file)