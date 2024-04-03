from backend.defaults import Defaults
import pickle


# Load the first dictionary from the first pickle file
with open('moo_parameters.pickle', 'rb') as file1:
    dict1 = pickle.load(file1)

dict2 = Defaults(moo=True).parameters

dict2['problem'] = dict1['problem']
dict2['algorithm'] = dict1['algorithm']

# Save the joined dictionary in another pickle file
with open('moo_parameters.pickle', 'wb') as output_file:
    pickle.dump(dict2, output_file)