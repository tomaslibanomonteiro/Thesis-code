from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pickle

from utils.defines import MOO_KEY

DEBUG_PRINT = False

def debug_print(*args):
    if DEBUG_PRINT:
        print(*args)
        
def setCombobox(combobox, items=None, center_items=False, index_changed_function=None):
    from PyQt5.QtCore import Qt
    
    if items is not None:
        combobox.addItems(items)
    if center_items:
        combobox.lineEdit().setAlignment(Qt.AlignCenter)
        combobox.lineEdit().setReadOnly(True)
    if index_changed_function is not None:
        combobox.currentIndexChanged.connect(index_changed_function)
class MyMessageBox(QMessageBox):
    """A class to show a message box with the given text and title."""
    def __init__(self, text, title="Warning", warning_icon=True):
        super().__init__()

        self.setIcon(QMessageBox.Warning) if warning_icon else None
        self.setText(text)
        self.setWindowTitle(title)
        self.setStandardButtons(QMessageBox.Ok)
        self.exec_()

def myFileManager(window_title, file_to_save_name=False, data_to_save=False, default_suffix=".pickle", name_filter="Pickle Files (*.pickle)", keys_to_check=None, moo = None, save_csv_index=False):
    """Open a file dialog to save or load a file. If file_to_save_name is given, save the file. If not, load the file and return the data.
    If keys_to_check is given, check if the loaded dictionary has the correct keys. If moo is given, check if the loaded moo is the same as the given moo."""
    
    if (keys_to_check is not None) ^ (moo is not None):
        ValueError("keys_to_check and moo args must be used together in myFileManager function")
    if name_filter not in [".pickle", ".csv"]:
        ValueError("name_filter can only be .pickle or .csv")
    
    loaded_data = None
    file_path = None
    
    # Open file dialog to select the save location
    file_dialog = QFileDialog()
    file_dialog.setDefaultSuffix(default_suffix)
    file_dialog.setNameFilter(name_filter)
    file_dialog.setWindowTitle(window_title)
    
    # protect the file dialog from crashing
    try:
        # If file_to_save_name is given, save the file
        if file_to_save_name: 
            file_dialog.selectFile(file_to_save_name)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            if file_dialog.exec_() == QFileDialog.Accepted:
                file_path = file_dialog.selectedFiles()[0]
                # Save options_dict as a pickle file
                with open(file_path, 'wb') as file:
                    if default_suffix == ".pickle":
                        pickle.dump(data_to_save, file) #@IgnoreException
                    elif default_suffix == ".csv":
                        data_to_save.to_csv(file_path, index=save_csv_index)
        # else, load the file and return the data
        else:
            file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
            if file_dialog.exec_() == QFileDialog.Accepted:
                file_path = file_dialog.selectedFiles()[0]
                # Load the pickle file
                with open(file_path, 'rb') as file:
                    loaded_data = pickle.load(file) #@IgnoreException
                    if keys_to_check is not None:
                        if not isinstance(loaded_data, dict):
                            loaded_data = None
                            raise Exception("The loaded file is not a dictionary")
                        if set(loaded_data.keys()) != set(keys_to_check + [MOO_KEY]):
                            loaded_data = None
                            raise Exception(f"The keys of the loaded parameters dictionary are not correct. They should be {keys_to_check}") #@IgnoreException
                        if loaded_data.pop(MOO_KEY) != moo:
                            loaded_data = None
                            raise Exception("The loaded file does not match current MOO/SOO mode") #@IgnoreException
    except Exception as e:
        MyMessageBox("Error saving/loading the file: \n" + str(e))
    
    filename = file_path.split("/")[-1].split(".")[0] if file_path else None
    return loaded_data, filename

def setBold(item):
    font = item.font()
    font.setBold(True)
    item.setFont(font)

def showAndRaise(window):    
    window.show()
    window.raise_()
    window.activateWindow()

def getAvailableName(name, names):
    """Return a name that is not in the list of names. When the name is already in the list, add a number to the name
    until it is not in the list (e.g. name (1), name (2), ...)"""
    
    if name not in names:
        return name
    else:
        i = 1
        while name + f" ({i})" in names:
            i += 1
        return name + f" ({i})"