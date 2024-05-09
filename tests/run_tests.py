####################################################################################################
######################## MODIFY to full path to the project folder #################################
full_path = r"C:\Users\tomas\OneDrive - Universidade de Lisboa\Desktop\Tese\Thesis-code"
####################################################################################################
####################################################################################################

import os
import filecmp
import time
import datetime
from PyQt5.QtWidgets import QApplication
import sys
sys.path.insert(1, full_path)

from utils.defines import RESULTS_FOLDER, EXPECTED_RESULTS_FOLDER, RESULTS_FILE
from tests.tests_declaration import Test, soo_algos, soo_probs, soo_mixed, moo_algos, moo_probs, moo_mixed

TESTS_TO_RUN = [soo_algos, soo_probs, soo_mixed, moo_algos, moo_probs, moo_mixed]

def main():

    # create a new folder RESULTS_FOLDER
    if os.path.exists(RESULTS_FOLDER):
        for file in os.listdir(RESULTS_FOLDER):
            if file.endswith(".csv"):
                os.remove(os.path.join(RESULTS_FOLDER, file))
    else:
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
    files = [file for file in os.listdir(RESULTS_FOLDER) if file.endswith(".csv")]
            
    # compare the CSV files
    for file in files:
        # append the results to the file inside RESULTS_FOLDER
        with open(RESULTS_FILE, 'a') as f:
            date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if file not in expected_files:
                string = date_time + ' No comparison for test ' + file + '\n'
            else:
                test_result = ' passed!' if filecmp.cmp(RESULTS_FOLDER + '/' + file, EXPECTED_RESULTS_FOLDER + '/' + file) else ' failed!'
                string = date_time + ' Test ' + file + test_result + '\n'
            print(string)
            f.write(string)

if __name__ == '__main__':
    main()