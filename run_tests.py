import os
import filecmp

# import all tests and declare them in ALL_TESTS
from utils.defines import RESULTS_FOLDER, EXPECTED_RESULTS_FOLDER, RESULTS_FILE
from PyQt5.QtWidgets import QApplication

from tests.tests_declaration import soo_algos, soo_probs, soo_mixed, moo_algos, moo_probs, moo_mixed

TESTS_TO_RUN = [moo_probs]

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
            
    # compare the CSV files
    for file in files:
        # write the results in a file inside RESULTS_FOLDER
        with open(RESULTS_FILE, 'w') as f:
            if file not in expected_files:
                f.write('No comparison for test ' + file)
            else:
                import datetime
                date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if filecmp.cmp(RESULTS_FOLDER + '/' + file, EXPECTED_RESULTS_FOLDER + '/' + file):
                    f.write(date_time + ' Test ' + file + ' passed!')
                else:
                    f.write(date_time + ' Test ' + file + ' failed!')

if __name__ == '__main__':
    main()