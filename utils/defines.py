DESIGNER_MAIN = 'frontend/designer_templates/main_window.ui' 
DESIGNER_EDIT_WINDOW = 'frontend/designer_templates/edit_window.ui'
DESIGNER_ALGO_WINDOW = 'frontend/designer_templates/algo_window.ui'

# to be put in ui table
NO_DEFAULT = "No def"

# to be put in ui table as respective widget 
VALUE_TYPES = (int, float, str, bool, type(None), NO_DEFAULT)

# OPERATORS = ["mutation", "crossover", "selection", "decomposition", "sampling", "ref_dirs"] 
OPERATORS = ["mutation", "crossover", "decomposition", "sampling", "ref_dirs"] 

# classes that have arguments with the same name as the operatores names but are different
FAKE_OPERATORS = ['ReductionBasedReferenceDirectionFactory', 'RieszEnergyReferenceDirectionFactory']
