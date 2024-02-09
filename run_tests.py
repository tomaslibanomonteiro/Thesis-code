import os
import filecmp
import time

# import all tests and declare them in ALL_TESTS
from utils.defines import RESULTS_FOLDER, EXPECTED_RESULTS_FOLDER, RESULTS_FILE
from PyQt5.QtWidgets import QApplication

from tests.tests_declaration import Test, soo_algos, soo_probs, soo_mixed, moo_algos, moo_probs, moo_mixed

# TESTS_TO_RUN = [moo_probs, moo_algos, moo_mixed, soo_probs, soo_algos, soo_mixed]
TESTS_TO_RUN = [soo_probs, soo_algos, soo_mixed]

def main():

    # create a new folder RESULTS_FOLDER
    if os.path.exists(RESULTS_FOLDER):
        import shutil
        shutil.rmtree(RESULTS_FOLDER)    
    os.mkdir(RESULTS_FOLDER)
    
    # create the app to instantiate the MainWindows
    app = QApplication([])
    tests=[]    
    # run the tests
    for test_options in TESTS_TO_RUN: 
        test = Test(test_options)
        tests.append(test)
        test.run()
    
    # Wait for all tests to finish
    for test in tests:
        while not test.is_finished:
            app.processEvents()
            time.sleep(0.1)
            
    # get the list of files to compare
    expected_files = [file for file in os.listdir(EXPECTED_RESULTS_FOLDER)]
    files = [file for file in os.listdir(RESULTS_FOLDER)]
            
    # compare the CSV files
    for file in files:
        # append the results to the file inside RESULTS_FOLDER
        with open(RESULTS_FILE, 'a') as f:
            if file not in expected_files:
                f.write('No comparison for test ' + file + '\n')
            else:
                import datetime
                date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if filecmp.cmp(RESULTS_FOLDER + '/' + file, EXPECTED_RESULTS_FOLDER + '/' + file):
                    f.write(date_time + ' Test ' + file + ' passed!\n')
                else:
                    f.write(date_time + ' Test ' + file + ' failed!\n')

if __name__ == '__main__':
    main()