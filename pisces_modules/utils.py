"""
Contains utility functions
"""

import os
import sys
import time

from pisces_modules.visuals import color, str_infos

# Call PathChecker class
#------------------------
# from tools.utils import PathChecker,
# self.pisces = PathChecker(user_path, self.pisces_folder, folder_exist=True)
# self.pisces_path = self.pisces.full_path
# self.folder = self.pisces.folder

class PathChecker():
    """
    Prompts WARNING if (path + folder) already exists or not depending on folder_exist flag
        If exist = True: warning will be displayed if folder exists
        If exist = False: warning will be displayed if folder doesn't exist
    If warnnig is displayed, user will be prompted to enter another folder name or quit
    """
    def __init__(self, path, folder, folder_exist=True):
        self.path = path
        self.folder = folder
        self.exist = folder_exist

    def condition_eval(self):
        """Condition evaluation changes depending on folder_exist boolean value"""
        if self.exist:
            def condition(path):
                return os.path.isdir(path)
            str_elem = 'already exists'
        else:
            def condition(path):
                return not os.path.isdir(path)
            str_elem = 'does not exist'
        return condition, str_elem

    @property
    def folder(self):
        """get folder"""
        return self._folder

    @folder.setter
    def folder(self, value):
        self._full_path = None
        self._folder = value

    @property
    def full_path(self):
        """get full_path"""
        if self._full_path is None:
            time.sleep(5)
            condition, str_elem = self.condition_eval()
            while True:
                if self.folder.casefold() == 'q':
                    sys.exit(f'\n{color["RED"]}[PROGRAM EXITED]{color["END"]}\n')
                elif condition(os.path.join(self.path, self.folder)):
                    prpt = (f'Folder {color["YELLOW"]}{self.folder}{color["END"]} '
                            f'{str_elem} in {color["YELLOW"]}{self.path}{color["END"]},\n\n'
                            'Enter new name or (q)uit')
                    self.folder = input(prpt)
                elif not condition(os.path.join(self.path, self.folder)):
                    break
            self._full_path = os.path.join(self.path, self.folder)
        return self._full_path


def path_checker(path, elem, existence=True, isfile=False, mod_param=None):
    """
    Prompts WARNING if path/folder or path/file already exists or not depending on 
    - existence flag
        If existence = True: warning will be displayed if folder doesn't exist
        If existence = False: warning will be displayed if folder already exists
    - isfile flag
        If isfile = True: function will check for path/file
        If isfile = False: function will check for path/folder
    If warnnig is displayed, user will be prompted to enter another folder/file name or quit
    If mod_param is defined, variable (mod_param[1]) in param file (mod_param[0]) will be
    modified with the right folder name choosen by user in case warnning is displayed
        mod_param should be defined in list of 2 elements:
        - Path to the param file to correct if warning is encountered
        - Variable to modify (under format 'var = ')
    """
    if elem == '':
        elem = 'PALEO_PISCES'
    full_path = os.path.join(path, elem)
    if not existence:
        def condition(path):
            if not isfile:
                return os.path.isdir(path)
            if isfile:
                return os.path.isfile(path)
        str_2 = 'already exists'
    else:
        def condition(path):
            if not isfile:
                return not os.path.isdir(path)
            if isfile:
                return not os.path.isfile(path)
        str_2 = 'does not exist'

    if isfile:
        str_1 = 'File'
    elif not isfile:
        str_1 = 'Folder'

    wit = False
    while True:
        if elem.casefold() == 'q':
            sys.exit(f'\n{color["RED"]}[PROGRAM EXITED]{color["END"]}\n')
        elif condition(full_path):
            prpt = (f'\n {str_infos["warning"]} {str_1} '
                f'{color["YELLOW"]}{elem}{color["END"]} '
                f'{str_2} in {color["YELLOW"]}{path}{color["END"]}\n\n'
                ' Enter another name or (q)uit\n ')
            elem = input(prpt)
            full_path = os.path.join(path, elem)
            wit = True # witnesses foldername entered by user had to be modified
        elif not condition(full_path):
            if wit and mod_param is not None:
                replacer = ["'" + elem + "'"]
                pre_replacer = [mod_param[1]]
                post_replacer = ['\n']
                find_replace_in_file(mod_param[0], pre_replacer, post_replacer, replacer)
            break
    return full_path


def find_in_str(str_start, str_end, str_obj, reverse_find = False):
    """
    Allow to extract an element from str object
    example:
        >>> var    = 'Hello wonderful world'
        >>> result = find_in_str('Hello ', ' world', var)
        >>> print(result)
            wonderful
    """
    if reverse_find:
        ind_s = str_obj.rfind(str_start) + len(str_start)
    else:
        ind_s = str_obj.find(str_start) + len(str_start)
    ind_e = str_obj.find(str_end, ind_s)
    return str_obj[ind_s:ind_e]


def find_replace_in_file(file_in, pre_replacer, post_replacer, replacer):
    """
    Allows to replace one or several parts in a txt file
    file_in: file with elements to replace
    pre_replacer: list of str objects
    post_replacer: list of str objects
    replacer: list of str objects

    Example:
        file_state = Hello world
                     Weather is bad today
                     I'm sad

        python
        >>> file_in         = file_state
        >>> pre_replacer   = ['Weather is ', 'I'm ']
        >>> str_znd     = [' today', '\n']
        >>> replacer = ['amazing', 'happy']
        >>> find_and_replace(file_in, pre_replacer, post_replacer, replacer)

        file_state = Hello world
                     Weather is amazing today
                     I'm happy
    """
    with open(file_in, 'r+', encoding="utf-8") as file_object:
        str_obj = file_object.read()
        ind_c = 0
        for (pre_repl, post_repl, repl) in zip(pre_replacer, post_replacer, replacer):
            ind_s = str_obj[ind_c:].find(pre_repl) + len(pre_repl) + ind_c
            ind_e = str_obj[ind_s:].find(post_repl) + ind_s
            str_obj = str_obj[:ind_s] + repl + str_obj[ind_e:]
            ind_c = ind_s + len(repl)
        file_object.seek(0)  # Set cursor at beginning of file
        file_object.write(str_obj)
        file_object.truncate()
        file_object.close()


def find_replace_in_str(str_obj, pre_replacer, post_replacer, replacer):
    """
    Allows to replace one or several parts in a string variable
    str_obj: string variable with elements to replace
    pre_replacer: list of str objects
    post_replacer: list of str objects
    replacer: list of str objects
    """
    ind_c = 0
    for (pre_repl, post_repl, repl) in zip(pre_replacer, post_replacer, replacer):
        ind_s = str_obj[ind_c:].find(pre_repl) + len(pre_repl) + ind_c
        ind_e = str_obj[ind_s:].find(post_repl) + ind_s
        str_obj = str_obj[:ind_s] + repl + str_obj[ind_e:]
        ind_c = ind_s + len(repl)
    return str_obj


def get_outputs(file_log_out, file_log_err, subprocess_result):
    """
    Allow to save outputs from a subprocess command into log files
        file_log_out: name of file that will contain outputs (include source path before filename)
        file_log_err: name of file that will contain errors (include source path before filename)
        subprocess_result: variable name containing the subprocess
    """
    with open(file_log_out, "w", encoding="utf-8") as log_out:
        log_out.write(subprocess_result.stdout)
        log_out.close()
    with open(file_log_err, "w", encoding="utf-8") as log_err:
        log_err.write(subprocess_result.stderr)
        log_err.close()


        # Because of versions of open mpi (2.0.4) needed for compilation of XIOS,
        # The xarray module can't be loaded with python 3.7.5.
        #  So the 2 steps below:
        # - Put sic in icemod as siconc in grid_t
        # - Compute wocetr_eff and put it in grid_w
        # are not used.
        # Fix have been found by using older version of python (3.7.2)
        # But compilation of XIOS and NEMO take around 25min instead of 5min

        # Put sic in icemod as siconc in grid_t
        #-----------------------------
        # file_t = os.path.join(self.bc_path, FILE_PREFIX, FILE_PREFIX + '_grid_T.nc')
        # file_icemod = os.path.join(self.bc_path, FILE_PREFIX, FILE_PREFIX + '_icemod.nc')
        # ds_grid_t = xr.open_dataset(file_t)
        # ds_icemod = xr.open_dataset(file_icemod)
        # ds_grid_t['siconc'] = ds_icemod['sic']
        # os.remove(file_t)
        # ds_grid_t.to_netcdf(file_t)
        #-----------------------------

        # Compute wocetr_eff and put it in grid_w
        #-----------------------------
        # file_mesh = os.path.join(self.bc_path, FILE_PREFIX, MASK_FILE)
        # ds_mesh = xr.open_dataset(file_mesh)
        # file_w = os.path.join(self.bc_path, FILE_PREFIX, FILE_PREFIX + '_grid_W.nc')
        # ds_grid_w = xr.open_dataset(file_w)
        # ds_grid_w["wocetr_eff"] = ds_mesh["e1t"] * ds_mesh["e2t"] * np.nanmean(ds_grid_w["wo"],0)
        # os.remove(file_w)
        # ds_grid_w.to_netcdf(file_w)
        #-----------------------------
