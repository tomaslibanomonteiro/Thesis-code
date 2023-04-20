import inspect

def class_args_to_list(cls, idx, previous_cls):
    # get the names and default values of the class's arguments
    sig = inspect.signature(cls.__init__)
    arg_names = list(sig.parameters.keys())[1:]  # skip "self"
    arg_defaults = [p.default for p in sig.parameters.values() if p.default is not inspect.Parameter.empty][1:]  # skip "self"

    # create a list of alternating argument names and default values
    arg_pairs = []
    for i in range(len(arg_names)):
        arg_pairs.append(arg_names[i])
        if i < len(arg_defaults):
            arg_pairs.append(arg_defaults[i])
        else:
            arg_pairs.append(None)

    # add class name to second column
    arg_pairs.insert(1, cls.__name__)

    # add modified class name to first column
    modified_cls_name = f"{idx}_{cls.__name__}"
    if cls == previous_cls:
        modified_cls_name = ""
    arg_pairs.insert(0, modified_cls_name)

    # convert the list to a list of lists with the desired format
    data = [arg_pairs[i:i+2] for i in range(0, len(arg_pairs), 2)]

    return data, cls

class MyClass1:
    def __init__(self, arg1, arg2=10, arg3=None):
        pass

class MyClass2:
    def __init__(self, arg1, arg2, arg3="default"):
        pass

class MyClass3:
    def __init__(self):
        pass


# create the list of classes to process
classes = [MyClass1, MyClass2, MyClass3]

previous_cls = None
final_data = []
for i, cls in enumerate(classes):
    data, previous_cls = class_args_to_list(cls, i, previous_cls)
    final_data += data

# print the final data
for row in final_data:
    print(row)
