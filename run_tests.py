import os
import filecmp

# import all tests and declare them in ALL_TESTS
from utils.defines import RESULTS_FOLDER, EXPECTED_RESULTS_FOLDER
from PyQt5.QtWidgets import QApplication

from tests.tests_declaration import soo_algos, soo_probs, soo_mixed, moo_algos, moo_probs, moo_mixed

TESTS_TO_RUN = [soo_algos, soo_probs, soo_mixed, moo_algos, moo_probs, moo_mixed]

def main():

    # create a new folder RESULTS_FOLDER
    if os.path.exists(RESULTS_FOLDER):
        import shutil
        shutil.rmtree(RESULTS_FOLDER)    
    os.mkdir(RESULTS_FOLDER)
        
    # create a QApplication to instatiate the QWidgets
    app = QApplication([]) 
    
    # run the tests
    for test in TESTS_TO_RUN: 
        print('Running test ' + test.test_name + '...')
        test.runTest()

    # wait for all threads to finish
    for my_thread in [test.my_thread for test in TESTS_TO_RUN]:
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