# frontend 

# main window
DESIGNER_MAIN = 'frontend/designer_templates/main_window/main_window.ui' 
DESIGNER_MAIN_TABS = 'frontend/designer_templates/main_window/main_tabs.ui'
DESIGNER_RUN_TAB = 'frontend/designer_templates/main_window/run_tab.ui'
DESIGNER_RESULT_FRAME = 'frontend/designer_templates/main_window/result_frame.ui'

# edit window
DESIGNER_EDIT_WINDOW = 'frontend/designer_templates/edit_window/edit_window.ui'
DESIGNER_EDIT_TAB = 'frontend/designer_templates/edit_window/edit_tab.ui'
DESIGNER_WIDGETS_FRAME = 'frontend/designer_templates/edit_window/widgets_frame.ui'

# tests folders
RESULTS_FOLDER = 'tests/results'
EXPECTED_RESULTS_FOLDER = 'tests/expected_results'      
RESULTS_FILE = 'tests/results/results.txt'

# to be put in ui table
NO_DEFAULT = "No def"

# sufix for the variant of an object
VARIANT = '_variant'

# to be put in ui table as respective widget 
VALUE_TYPES = (int, float, str, bool, type(None), NO_DEFAULT)

# default number of rows in the main window tables
DEFAULT_ROW_NUMBERS = [7, 7, 4, 1]

# object id col number in the edit parameters tables
ID_COL = 1 

# result_layout number of widgets before adding result_frames 
RESULT_LAYOUT_WIDGETS = 3

# maximum number of result_frames accepted before asking the user to delete
MAX_RESULT_FRAMES = 6

# default number of moo and soo pages in main window
SOO_PAGE = 0
MOO_PAGE = 1

# arg values from an algorithm that have a separate table because they are objects
MUT_KEY = 'mutation'
CROSS_KEY = 'crossover'
SEL_KEY = 'selection'
SAMP_KEY = 'sampling'
DECOMP_KEY = 'decomposition'
REF_DIR_KEY = 'ref_dirs'

OPERATORS = [MUT_KEY, CROSS_KEY, SEL_KEY, SAMP_KEY, DECOMP_KEY, REF_DIR_KEY]

PROB_KEY = 'problem'
ALGO_KEY = 'algorithm'
PI_KEY = 'pi'
TERM_KEY = 'term'
N_SEEDS_KEY = 'n_seeds'
 
# keys needed in a dictionary given to start the app ORDERED THE SAME AS THE APP!!
RUN_OPTIONS_KEYS = [PROB_KEY, ALGO_KEY, PI_KEY, TERM_KEY, N_SEEDS_KEY]

from backend.get import (get_algorithm, get_performance_indicator, get_problem, get_termination, get_crossover, 
                         get_decomposition, get_mutation, get_reference_directions, get_sampling, get_selection,
                         get_algorithm_options, get_crossover_options, get_decomposition_options, get_mutation_options,
                         get_performance_indicator_options, get_problem_options, get_reference_direction_options,
                         get_sampling_options, get_selection_options, get_termination_options)

# Edit Window Dictionary
OPERATORS_ARGS_DICT = {  MUT_KEY: ('(op) Mutations', 'Edit Mutations', get_mutation, get_mutation_options),
                    CROSS_KEY: ('(op) Crossovers', 'Edit Crossovers', get_crossover, get_crossover_options),
                    SEL_KEY: ('(op) Selections', 'Edit Selections', get_selection, get_selection_options),
                    SAMP_KEY: ('(op) Samplings', 'Edit Samplings', get_sampling, get_sampling_options),
                    DECOMP_KEY: ('(op) Decomposition', 'Edit Decompositions', get_decomposition, get_decomposition_options),
                    REF_DIR_KEY: ('(op) Ref. Dir.', 'Edit Ref_dirs', get_reference_directions, get_reference_direction_options)}

RUN_OPTIONS_ARGS_DICT = {PROB_KEY: ('Problems', 'Edit Problems', get_problem, get_problem_options), 
                    ALGO_KEY: ('Algorithms', 'Edit Algorithms', get_algorithm, get_algorithm_options), 
                    PI_KEY: ('Perf. Ind.', 'Edit Performance Indicators', get_performance_indicator, get_performance_indicator_options),
                    TERM_KEY: ('Terminations', 'Edit Termination Criteria', get_termination, get_termination_options)}

KEY_ARGS_DICT = {**OPERATORS_ARGS_DICT, **RUN_OPTIONS_ARGS_DICT}
