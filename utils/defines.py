# frontend 

# main window
DESIGNER_MAIN = 'frontend/designer_templates/main_window/main_window.ui' 
DESIGNER_MAIN_TABS = 'frontend/designer_templates/main_window/main_tabs.ui'
DESIGNER_RUN_TAB = 'frontend/designer_templates/main_window/run_tab.ui'
DESIGNER_RESULT_FRAME = 'frontend/designer_templates/main_window/result_frame.ui'

# edit window
DESIGNER_EDIT_WINDOW = 'frontend/designer_templates/edit_window/edit_window.ui'
DESIGNER_EDIT_TAB = 'frontend/designer_templates/edit_window/edit_tab.ui'

# tests folders
RESULTS_FOLDER = 'tests/results'
EXPECTED_RESULTS_FOLDER = 'tests/expected_results'      
RESULTS_FILE = 'tests/results/results.txt'

# to be put in ui table
NO_DEFAULT = "No def"

# to be put in ui table as respective widget 
VALUE_TYPES = (int, float, str, bool, type(None), NO_DEFAULT)

# arg values from an algorithm that have a separate table because they are objects
OPERATORS = ["mutation", "crossover", "selection", "decomposition", "sampling", "ref_dirs"] 

# classes that have arguments with the same name as the operatores names but are different
FAKE_OPERATORS = ['ReductionBasedReferenceDirectionFactory', 'RieszEnergyReferenceDirectionFactory']

# keys needed in a dictionary given to start the app
RUN_OPTIONS_KEYS = ['prob', 'algo', 'pi', 'term', 'n_seeds']

# default number of rows in the main window tables
DEFAULT_ROW_NUMBERS = [7, 7, 4, 1]

# object id col number in the edit parameters tables
ID_COL = 1 

# result_layout number of widgets before adding result_frames 
RESULT_LAYOUT_WIDGETS = 3

# maximum number of result_frames accepted before asking the user to delete
MAX_RESULT_FRAMES = 1