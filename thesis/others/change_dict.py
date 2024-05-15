import pickle

# Load the pickle file
with open('moo_parameters.pickle', 'rb') as file:
    data = pickle.load(file)

from backend.defaults import Defaults

def_dict = Defaults(moo=True).parameters

# Modify the value in a specific key
data['problem'] = def_dict['problem']

# Save the modified data back to a pickle file
with open('moo_parameters_new.pickle', 'wb') as file:
    pickle.dump(data, file)