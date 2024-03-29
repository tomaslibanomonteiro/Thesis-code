############################################################ 
########################### FOLDERS ########################
############################################################


# folders main window
DESIGNER_MAIN = 'frontend/designer_templates/main_window/main_window.ui' 
DESIGNER_FIXED_TABS = 'frontend/designer_templates/main_window/fixed_tabs.ui'
DESIGNER_RUN_TAB = 'frontend/designer_templates/main_window/run_tab.ui'
DESIGNER_HISTORY_FRAME = 'frontend/designer_templates/main_window/history_frame.ui'

# folders edit window
DESIGNER_EDIT_WINDOW = 'frontend/designer_templates/edit_window/edit_window.ui'
DESIGNER_EDIT_TAB = 'frontend/designer_templates/edit_window/edit_tab.ui'
DESIGNER_WIDGETS_FRAME = 'frontend/designer_templates/edit_window/widgets_frame.ui'

# folders tests
RESULTS_FOLDER = 'tests/results'
EXPECTED_RESULTS_FOLDER = 'tests/expected_results'      
RESULTS_FILE = 'tests/results/results.txt'

############################################################ 
########################### KEYS ###########################
############################################################

# RUN OPTIONS
PROB_KEY = 'problem'
ALGO_KEY = 'algorithm'
PI_KEY = 'pi'
TERM_KEY = 'term'
N_SEEDS_KEY = 'n_seeds'

RUN_OPTIONS_KEYS = [PROB_KEY, ALGO_KEY, PI_KEY, TERM_KEY, N_SEEDS_KEY]

# OPERATORS
MUT_KEY = 'mutation'
CROSS_KEY = 'crossover'
SEL_KEY = 'selection'
SAMP_KEY = 'sampling'
DECOMP_KEY = 'decomposition'
REF_DIR_KEY = 'ref_dirs'

OPERATORS = [MUT_KEY, CROSS_KEY, SEL_KEY, SAMP_KEY, DECOMP_KEY, REF_DIR_KEY]

# PLOTTING
VOTING_KEY = 'Voting'
PLOT_PROGRESS_KEY = 'Progress'
PLOT_PS_KEY = 'Pareto Sets'
PLOT_PC_KEY = 'Parallel Coordinates'
PLOT_FL_KEY = 'Fitness Landscape'

# OTHERS
CLASS_KEY = 'Class' # key from the class Default dictionary to get the class name 
N_EVAL_KEY = 'n_eval' # for the dataframes
N_GEN_KEY = 'n_gen' # for the dataframes
MOO_KEY = 'moo' # key to know if a loaded object is loaded into the right MOO/SOO
 

############################################################ 
########################### WINDOWS ########################
############################################################

### MAIN WINDOW
SOO_TAB = 0
MOO_TAB = 1

# RUN TAB
DEFAULT_ROW_NUMBERS = [7, 7, 4, 1] # default number of rows in the main window tables
HISTORY_LAYOUT_WIDGETS = 4 # history_layout number of widgets before adding history_frames 

# HISTORY TAB
MAX_HISTORY_FRAMES = 6 # maximum number of history_frames accepted before asking the user to delete

### EDIT WINDOW
NO_DEFAULT = "No def" # to be put in ui table
VARIANT = ' variant' # sufix for the variant of an object
VALUE_TYPES = (int, float, str, bool, type(None), NO_DEFAULT) # to be put in ui table as respective widget 
ID_COL = 1 # object id col number in the edit parameters tables

from backend.get import (get_algorithm, get_performance_indicator, get_problem, get_termination, get_crossover, 
                         get_decomposition, get_mutation, get_reference_directions, get_sampling, get_selection,
                         get_algorithm_options, get_crossover_options, get_decomposition_options, get_mutation_options,
                         get_performance_indicator_options, get_problem_options, get_reference_direction_options,
                         get_sampling_options, get_selection_options, get_termination_options)

# for the creation of the tabs in the edit window: (key: (tab name, label, get_object, get_options)) 
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

