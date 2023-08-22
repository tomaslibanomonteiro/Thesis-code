import os
import filecmp

# import all tests and declare them in ALL_TESTS
from tests.tests_declaration import test1, test2, test3, test_de
from utils.defines import RESULTS_FOLDER, EXPECTED_RESULTS_FOLDER
from PyQt5.QtWidgets import QApplication

ALL_TESTS = [test1, test2, test3, test_de]

TESTS_TO_RUN = [test_de]

# choose the type of tests to run from the list below
# ['soo' / 'moo', 'long' / 'short', 'algo' / 'prob' / 'pi' / 'term' / 'n_seeds']
RUN_TYPES = ['soo', 'moo', 'short', 'long', 'algo', 'prob', 'pi', 'term', 'n_seeds']


def main():

    # create a new folder RESULTS_FOLDER
    if os.path.exists(RESULTS_FOLDER):
        import shutil
        shutil.rmtree(RESULTS_FOLDER)    
    os.mkdir(RESULTS_FOLDER)
    
    tests = [test for test in TESTS_TO_RUN if test.isOfType(RUN_TYPES)]    
    
    # create a QApplication to instatiate the QWidgets
    app = QApplication([]) 
    
    # run the tests
    for test in tests: 
        print('Running test ' + test.test_name + '...')
        test.runTest()

    # wait for all threads to finish
    for my_thread in [test.my_thread for test in tests]:
        print('Waiting for thread ' + str(my_thread) + ' to finish...')
        my_thread.join() 
    
    # get the list of files to compare
    expected_files = [file for file in os.listdir(EXPECTED_RESULTS_FOLDER)]
    files = [file for file in os.listdir(RESULTS_FOLDER)]
    
    # check if all files have a comparison in the expected results folder
    cmp_files = []
    for file in files:
        if file in expected_files:
            cmp_files.append(file)
        else:
            print('No comparison for test ' + file)
        
    # compare the CSV files
    for file in cmp_files:
        if filecmp.cmp(RESULTS_FOLDER + '/' + file, EXPECTED_RESULTS_FOLDER + '/' + file):
            print('Test ' + file + ' passed!')
        else:
            print('Test ' + file + ' failed!')

if __name__ == '__main__':
    main()