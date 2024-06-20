import pickle

# Load the pickle file
with open('moo_parameters.pickle', 'rb') as file:
    param = pickle.load(file)

from backend.defaults import Defaults

def_param = Defaults(moo=False).parameters
param['plot_types'] = def_param['plot_types']
param['survival'] = def_param['survival']

# Save the modified data back to a pickle file
with open('moo_parameters.pickle', 'wb') as file:
    pickle.dump(param, file)

