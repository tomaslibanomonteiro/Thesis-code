import pickle

# Load the first dictionary from the first pickle file
with open('moo_parameters.pickle', 'rb') as file1:
    dict1 = pickle.load(file1)

# Load the second dictionary from the second pickle file
with open('moo_parameters_def.pickle', 'rb') as file2:
    dict2 = pickle.load(file2)

dict2['problem'] = dict1['problem']
dict2['algorithm'] = dict1['algorithm']

# Save the joined dictionary in another pickle file
with open('moo_parameters_2.pickle', 'wb') as output_file:
    pickle.dump(dict2, output_file)