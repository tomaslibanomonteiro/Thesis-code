# Accepted values
PM_NAMES = ['hv', 'igd', 'gd', 'igd+', 'gd+']


def check_PM(pm_names, n_obj):
    # Check if PM selected are valid, at least one is chosen and are not repeated
    if n_obj == 1 and len(pm_names) != 0:
        raise Exception('Performance Measure cannot be selected for a single objective run (evaluation by best solution)')
    elif n_obj > 1:     
        if len(pm_names) == 0:
            raise Exception('No Performance Measure selected for the run')
        elif len(pm_names) != len(set(pm_names)):
            raise Exception('Repeated Performance Measure selected for the same run')
        # check if the PM selected are valid
        elif not set(pm_names).issubset(PM_NAMES):
            # raise exception with the name of the invalid PM
            raise Exception('Invalid Performance Measure selected for the run: {}'.format(set(pm_names).difference(PM_NAMES)))
            