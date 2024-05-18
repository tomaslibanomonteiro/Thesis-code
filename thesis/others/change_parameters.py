import pickle
import os
import pickle
from backend.defaults import Defaults
from utils.defines import MOO_KEY, TERM_KEY, PI_KEY, ALGO_KEY, REF_DIR_KEY, PROB_KEY
# Function to update the pickle file
def update_pickle_file(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    
    # Ask user if they want to update the file
    user_input = input(f"Do you want to update the file '{file_path}'? (y/n): ")
    
    if user_input.lower() == 'y':
        def_parameters = Defaults(moo=data['moo']).parameters
        data['parameters'][TERM_KEY] = def_parameters[TERM_KEY]
        data['parameters'][PI_KEY] = def_parameters[PI_KEY]
    
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)

def main():
    # Traverse through all files in the directory (including subfolders)
    for root, dirs, files in os.walk('C:/Users/tomas/OneDrive - Universidade de Lisboa/Desktop/Tese/Thesis-code/thesis'):
        for file in files:
            if file.endswith('.pickle') and 'Run' in file:
                file_path = os.path.join(root, file)
                update_pickle_file(file_path)
                
if __name__ == '__main__':
    main()