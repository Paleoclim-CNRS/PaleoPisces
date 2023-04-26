"""
Processes to set up PALEO PISCES
"""

import os
import subprocess
import shutil
import re
from importlib import import_module
# import xarray as xr
# import numpy as np

from pisces_modules.visuals import color, str_infos

from pisces_modules.utils import (path_checker,
                                  find_replace_in_file)

from pisces_modules.paths import (user,
                                  user_path,
                                  WORK_PATH,
                                  SOURCES_PATH,
                                  IGCM_PATH)

if not os.path.isfile(os.path.join(WORK_PATH, 'user_input', user, 'param.py')):
    os.makedirs(os.path.join(WORK_PATH, 'user_input', user), exist_ok=True)
    shutil.copy2(os.path.join(SOURCES_PATH, 'USER_INPUT', 'param.py'),
                        os.path.join(WORK_PATH, 'user_input', user))
    print(f'\n {str_infos["note"]} Parametrization file {color["YELLOW"]}param.py{color["END"]} created into '
          f'{color["YELLOW"]}{os.path.join(WORK_PATH, "user_input", user)}{color["END"]} directory')

# var_lst = [SIM_OUTPUT_PATH, FILE_PREFIX, MASK_PATH, MASK_FILE, BATHY_PATH, BATHY_FILE, SUBBASIN_FILE, MASK_BATHY_FILE]
# for varname in var_lst:
#     exec(f"{varname} = getattr(sim_file, '{varname}')")

param_module    = import_module(f'user_input.{user}.param')
PISCES_FOLDER   = getattr(param_module, 'PALEOPISCES_FOLDER')
BC_FOLDER       = getattr(param_module, 'BC_FOLDER')
BC_EXP_FOLDER   = getattr(param_module, 'BC_EXP_FOLDER')
SIM_OUTPUT_PATH = getattr(param_module, 'SIM_OUTPUT_PATH')
FILE_PREFIX     = getattr(param_module, 'FILE_PREFIX')
COORD_PATH      = getattr(param_module, 'COORD_PATH')
COORD_FILE      = getattr(param_module, 'COORD_FILE')
MASK_PATH       = getattr(param_module, 'MASK_PATH')
MASK_FILE       = getattr(param_module, 'MASK_FILE')
BATHY_PATH      = getattr(param_module, 'BATHY_PATH')
BATHY_FILE      = getattr(param_module, 'BATHY_FILE')
SUBBASIN_FILE   = getattr(param_module, 'SUBBASIN_FILE')
MASK_BATHY_FILE = getattr(param_module, 'MASK_BATHY_FILE')
SOLUBILITY_FILE = getattr(param_module, 'SOLUBILITY_FILE')
PAR_FILE        = getattr(param_module, 'PAR_FILE')
JOB_NAME        = getattr(param_module, 'JOB_NAME')
DATE_BEGIN      = getattr(param_module, 'DATE_BEGIN')
DATE_END        = getattr(param_module, 'DATE_END')
SPACE_NAME      = getattr(param_module, 'SPACE_NAME')

param_file = os.path.join(WORK_PATH, "user_input", user, 'param.py')
param_var = {'pisces'   :'PALEOPISCES_FOLDER = ',
             'bc'       :'BC_FOLDER          = ',
             'bc_exp'   :'BC_EXP_FOLDER      = ',
             'msk_bathy':'MASK_BATHY_FILE = ',
             'job'      :'JOB_NAME   = '}


# Get realtime output of a command in console
#----------------------------------------------------------------
# result = subprocess.Popen(
#     ['./ScaleNutrients.ksh'],
#     cwd=self.bc_path,
#     stdout=subprocess.PIPE
# )
# # Poll process.stdout to show stdout live
# while True:
#     out_str = result.stdout.readline().strip().decode("utf-8")
#     if result.poll() is not None:
#         break
#     # if '?' in out_str:
#     print(out_str)
# result.wait()

# get_outputs(os.path.join(self.bc_path, 'log_out_1'),
#             os.path.join(self.bc_path, 'log_err_1'), result)
#----------------------------------------------------------------


class PaleoPiscesInstaller():
    """Install paleo pisces model"""

    def __init__(self):

        print(str_infos['paleopisces_title'])

        pisces_folder = PISCES_FOLDER

        # If PISCES_FOLDER variable is empty, ask for a new folder to copy pisces to
        if pisces_folder == '':
            prpt = (f' Enter path + folder name where PALEO PISCES will be installed:\n'
                    f' (From {color["YELLOW"]}{user_path}{color["END"]})\n ')
            pisces_folder = input(prpt)
            replacer = ["'" + pisces_folder + "'"]
            pre_replacer = [param_var['pisces']]
            post_replacer = ['\n']
            find_replace_in_file(param_file, pre_replacer, post_replacer, replacer)

        # Make sure folder for paleopisces model doesn't already exist
        self.pisces_path = path_checker(
            user_path,
            pisces_folder,
            existence=False,
            mod_param=[param_file, param_var['pisces']]
        )

        print(str_infos["install_pisces"])

    def cp_paleo_pisces(self):
        """Copy precompiled PaleoPisces model"""

        print(f'\n Copying {color["BLUE"]}PALEO PISCES{color["END"]} into '
              f'{color["YELLOW"]}{self.pisces_path}{color["END"]}...',
              end=" ", flush=True)

        shutil.copytree(
            os.path.join(SOURCES_PATH, 'MODEL', 'PALEOPISCES'),
            os.path.join(self.pisces_path),
            symlinks=True
        )

        print(str_infos["done"])

        print(f'\n {color["BOLD"]}[{color["END"]}'
              f'{color["GREEN"]}Paleo Pisces successfully copied{color["END"]}'
              f'{color["BOLD"]}]{color["END"]}\n')


class PaleoPiscesConfigurator():
    """Set up boundary conditions"""

    def __init__(self):
        print(f'\n {str_infos["note"]} {color["YELLOW"]}install_paleo_pisces.py{color["END"]} '
            'must have been run first')

        # Make sure folder for paleopisces model already exists
        self.pisces_path = path_checker(
            user_path,
            PISCES_FOLDER,
            existence=True,
            mod_param=[param_file, param_var['pisces']]
        )

        self.bc_path = os.path.join(user_path, BC_FOLDER)

        # Make sure folder for experience containing coupled sim files in boundary condition doesn't already exists
        self.bc_exp_path = path_checker(
            os.path.join(user_path, BC_FOLDER),
            BC_EXP_FOLDER,
            existence=False,
            mod_param=[param_file, param_var['bc_exp']]
        )
        os.makedirs(self.bc_exp_path)

        # Make sure MASK_BATHY_FILE doesn't already exists
        self.msk_bathy = path_checker(
            self.bc_path,
            MASK_BATHY_FILE,
            existence=False,
            isfile=True,
            mod_param=[param_file, param_var['msk_bathy']]
        ).split('/')[-1]

        self.dim_y = os.popen(
            f"ncdump -h {os.path.join(COORD_PATH, COORD_FILE)} | grep -i 'y = ' | cut -f 3 -d ' '"
            ).read()[:-1]

        print(str_infos["set_up_bc"])


    def cp_bc_files(self):
        """Copy BC files into $USER directory"""

        print(f'\n Making {color["BLUE"]}symlinks{color["END"]} of BC files into '
              f'{color["YELLOW"]}{self.bc_exp_path}{color["END"]}...',
              end=" ", flush=True)
        # SYMLINKS
        os.symlink(
            os.path.join(COORD_PATH, COORD_FILE),
            os.path.join(self.bc_exp_path, COORD_FILE)
        )
        shutil.copy2(
            os.path.join(MASK_PATH, MASK_FILE),
            os.path.join(self.bc_exp_path, MASK_FILE)
        )
        os.symlink(
            os.path.join(BATHY_PATH, BATHY_FILE),
            os.path.join(self.bc_exp_path, BATHY_FILE)
        )
        os.symlink(
            os.path.join(BATHY_PATH, SUBBASIN_FILE),
            os.path.join(self.bc_exp_path, SUBBASIN_FILE)
        )
        shutil.copy2(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_grid_T.nc'),
            self.bc_exp_path
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_grid_U.nc'),
            os.path.join(self.bc_exp_path,
                         FILE_PREFIX + '_grid_U.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_grid_V.nc'),
            os.path.join(self.bc_exp_path,
                         FILE_PREFIX + '_grid_V.nc')
        )
        shutil.copy2(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_grid_W.nc'),
            self.bc_exp_path
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_diaptr.nc'),
            os.path.join(self.bc_exp_path,
                         FILE_PREFIX + '_diaptr.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'MBG', 'Analyse',
                         'SE', FILE_PREFIX + '_diad_T.nc'),
            os.path.join(self.bc_exp_path,
                         FILE_PREFIX + '_diad_T.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'MBG', 'Analyse',
                         'SE', FILE_PREFIX + '_ptrc_T.nc'),
            os.path.join(self.bc_exp_path,
                         FILE_PREFIX + '_ptrc_T.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'ATM', 'Analyse',
                         'SE', FILE_PREFIX + '_histmth.nc'),
            os.path.join(self.bc_exp_path,
                         FILE_PREFIX + '_histmth.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'ICE', 'Analyse',
                         'SE', FILE_PREFIX + '_icemod.nc'),
            os.path.join(self.bc_exp_path, FILE_PREFIX + '_icemod.nc')
        )
        print(str_infos["done"])

        # Use of UpadteVariable.ksh
        #-----------------------------
        print(f'\n Adding {color["BLUE"]}siconc{color["END"]} and {color["BLUE"]}wocetr_eff{color["END"]} '
              f'variables in {color["YELLOW"]}{FILE_PREFIX}_grid_T.nc{color["END"]} and {color["YELLOW"]}'
              f'{FILE_PREFIX}_grid_W.nc{color["END"]}...', end=" ", flush=True)

        if not os.path.isfile(os.path.join(self.bc_path, 'UpdateVariable_sic.ksh')):
            shutil.copy2(
                os.path.join(SOURCES_PATH, 'SCRIPT', 'UpdateVariable_sic.ksh'),
                os.path.join(self.bc_path)
            )
        if not os.path.isfile(os.path.join(self.bc_path, 'UpdateVariable_woce.ksh')):
            shutil.copy2(
                os.path.join(SOURCES_PATH, 'SCRIPT', 'UpdateVariable_woce.ksh'),
                os.path.join(self.bc_path)
            )

        replacer = [self.bc_exp_path, FILE_PREFIX + '_grid_T.nc', FILE_PREFIX + '_icemod.nc']
        pre_replacer = ['dir=', 'file_t=', 'file_icemod=']
        post_replacer = ['\n', '\n', '\n']
        find_replace_in_file(os.path.join(self.bc_path, 'UpdateVariable_sic.ksh'),
            pre_replacer, post_replacer, replacer)

        replacer = [self.bc_exp_path, FILE_PREFIX + '_grid_W.nc', MASK_FILE]
        pre_replacer = ['dir=', 'file_w=', 'meshfile=']
        post_replacer = ['\n', '\n', '\n']
        find_replace_in_file(os.path.join(self.bc_path, 'UpdateVariable_woce.ksh'),
            pre_replacer, post_replacer, replacer)

        result1 = subprocess.run(
            ['./UpdateVariable_sic.ksh'],
            cwd=self.bc_path,
            capture_output=True,
            text=True,
            check=True
        )

        result2 = subprocess.run(
            ['./UpdateVariable_woce.ksh'],
            cwd=self.bc_path,
            capture_output=True,
            text=True,
            check=True
        )

        print(str_infos["done"])


        # Extract files _NO3, _02, from ptrc_T file...
        print(f'\n Extract variables ({color["BLUE"]}NO3{color["END"]}, '
              f'{color["BLUE"]}PO4{color["END"]}, {color["BLUE"]}DIC{color["END"]}...)'
              f' in files from {color["YELLOW"]}{FILE_PREFIX}_ptrc_T.nc{color["END"]}...',
              end=" ", flush=True)

        if not os.path.isfile(os.path.join(self.bc_path, 'ScaleNutrients.ksh')):
            shutil.copy2(
                os.path.join(SOURCES_PATH, 'SCRIPT', 'ScaleNutrients.ksh'),
                os.path.join(self.bc_path)
            )

        replacer = [self.bc_exp_path, FILE_PREFIX]
        pre_replacer = ['dir=', 'file_prefix=']
        post_replacer = ['\n', '\n']
        find_replace_in_file(os.path.join(self.bc_path, 'ScaleNutrients.ksh'),
                             pre_replacer, post_replacer, replacer)

        result = subprocess.run(
            ['./ScaleNutrients.ksh'],
            cwd=self.bc_path,
            capture_output=True,
            text=True,
            check=True
        )

        print(str_infos["done"])


    def weight_tool(self):
        """Set up weight tool to compute weights"""

        print(f'\n Preparing {color["BLUE"]}weight tool{color["END"]}...', end=" ", flush=True)
        # Copy folder modipsl/modeles/NEMOGCM/TOOLS/WEIGHTS into BC folder
        if not os.path.isdir(os.path.join(self.bc_path, 'WEIGHTS')):
            shutil.copytree(
                os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM', 'TOOLS', 'WEIGHTS'),
                os.path.join(self.bc_path, 'WEIGHTS')
            )

        # Create folder data in folder WEIGHTS
        if not os.path.isdir(os.path.join(self.bc_path, 'WEIGHTS', 'data')):
            os.mkdir(os.path.join(self.bc_path, 'WEIGHTS', 'data'))

        # Copy files in data folder
        if not os.path.isfile(os.path.join(self.bc_path, 'WEIGHTS', 'data', 'DUST_INCA_LOI6012-histAER_1M_1850.nc')):
            shutil.copy2(
                os.path.join(IGCM_PATH, 'Dust_inca_LOI', 'DUST_INCA_LOI6012-histAER_1M_1850.nc'),
                os.path.join(self.bc_path, 'WEIGHTS', 'data')
            )
        if not os.path.isfile(
            os.path.join(self.bc_path, 'WEIGHTS', 'data',
            'Ndep_input4MIPs_surfaceFluxes_CMIP_NCAR-CCMI-2-0_gn_185001-185012-clim.nc')
            ):
            shutil.copy2(
                os.path.join(
                    IGCM_PATH, 'Ndep_input4MIPs',
                    'Ndep_input4MIPs_surfaceFluxes_CMIP_NCAR-CCMI-2-0_gn_185001-185012-clim.nc'
                    ),
                os.path.join(self.bc_path, 'WEIGHTS', 'data')
            )
        if not os.path.isfile(os.path.join(self.bc_path, 'WEIGHTS', 'data', COORD_FILE)):
            shutil.copy2(
                os.path.join(COORD_PATH, COORD_FILE),
                os.path.join(self.bc_path, 'WEIGHTS', 'data')
            )

        # Copy namelist_r144x143_paleorca2_bilin and namelist_r144x96_paleorca2_bilin
        if not os.path.isfile(os.path.join(self.bc_path, 'WEIGHTS', 'data', 'namelist_r144x143_paleorca2_bilin')):
            shutil.copy2(
                os.path.join(SOURCES_PATH, 'NAMELIST', 'namelist_r144x143_paleorca2_bilin'),
                os.path.join(self.bc_path, 'WEIGHTS', 'data')
            )
        if not os.path.isfile(os.path.join(self.bc_path, 'WEIGHTS', 'data', 'namelist_r144x96_paleorca2_bilin')):
            shutil.copy2(
                os.path.join(SOURCES_PATH, 'NAMELIST', 'namelist_r144x96_paleorca2_bilin'),
                os.path.join(self.bc_path, 'WEIGHTS', 'data')
            )

        replacer = [COORD_FILE]
        pre_replacer = ["    nemo_file = '"]
        post_replacer = ["'\n"]
        find_replace_in_file(os.path.join(self.bc_path, 'WEIGHTS', 'data', 'namelist_r144x143_paleorca2_bilin'),
                             pre_replacer, post_replacer, replacer)
        find_replace_in_file(os.path.join(self.bc_path, 'WEIGHTS', 'data', 'namelist_r144x96_paleorca2_bilin'),
                             pre_replacer, post_replacer, replacer)

        # Creates weight files
        lst_err = []

        # Files produced: remap_data_grid.nc and remap_nemo_grid.nc
        weight_scripgrid_143 = subprocess.run(['../scripgrid.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x143_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        lst_err.append(weight_scripgrid_143.stderr)

        # Files produced: data_nemo_bilin.nc and nemo_data_bilin.nc
        weight_scrip_143 = subprocess.run(['../scrip.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x143_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        lst_err.append(weight_scrip_143.stderr)

        if not os.path.isfile(os.path.join(self.bc_path, 'WEIGHTS', 'data', 'weights_r144x143_paleorca2_bilinear.nc')):
            weight_scripshape_143 = subprocess.run(['../scripshape.exe'],
                cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
                capture_output=True,
                input='namelist_r144x143_paleorca2_bilin\n',
                encoding='ascii',
                check=True
            )
            lst_err.append(weight_scripshape_143.stderr)

        # Files produced: remap_data_grid.nc and remap_nemo_grid.nc
        weight_scripgrid_96 = subprocess.run(['../scripgrid.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x96_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        lst_err.append(weight_scripgrid_96.stderr)

        # Files produced: data_nemo_bilin.nc and nemo_data_bilin.nc
        weight_scrip_96 = subprocess.run(['../scrip.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x96_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        lst_err.append(weight_scrip_96.stderr)

        if not os.path.isfile(os.path.join(self.bc_path, 'WEIGHTS', 'data', 'weights_r144x96_paleorca2_bilinear.nc')):
            weight_scripshape_96 = subprocess.run(['../scripshape.exe'],
                cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
                capture_output=True,
                input='namelist_r144x96_paleorca2_bilin\n',
                encoding='ascii',
                check=True
            )
            lst_err.append(weight_scripshape_96.stderr)

        if not any(lst_err):
            print(str_infos["done"])
        else:
            print(str_infos["error"])


    def coastal_mask(self):
        """Compute coastline tool for mask"""

        # copy bathy file
        if not os.path.islink(os.path.join(self.bc_path, BATHY_FILE)):
            os.symlink(
                os.path.join(BATHY_PATH, BATHY_FILE),
                os.path.join(self.bc_path, BATHY_FILE)
            )

        # copy create_coastline.f90
        if not os.path.isfile(os.path.join(self.bc_path, 'create_coastline.f90')):
            shutil.copy2(
                os.path.join(SOURCES_PATH, 'SRC', 'create_coastline.f90'),
                os.path.join(self.bc_path)
            )

        # Modify create_coastline.f90
        replacer = [self.dim_y, BATHY_FILE, self.msk_bathy, self.dim_y, self.msk_bathy]
        pre_replacer = ['integer, parameter :: imax=182, jmax=', 'status = nf90_open("', 'status = nf90_create("', 'status = nf90_def_dim(ncid3,"y",', 'status = nf90_open("']
        post_replacer = ['\n', '",nf90_nowrite,ncid1)', '",nf90_noclobber,ncid3)', ',ydimid)', '",nf90_write,ncid3)']
        find_replace_in_file(os.path.join(self.bc_path, 'create_coastline.f90'),
            pre_replacer, post_replacer, replacer)

        # Compile Coast tool
        print(f'\n Compiling {color["BLUE"]}create_coastline.f90{color["END"]}...', 
            end=" ", flush=True)
        lib_inc = (os.getenv('NETCDFFORTRAN_LDFLAGS').split()
                   + os.getenv('NETCDFC_LDFLAGS').split()
                   + os.getenv('NETCDFFORTRAN_FFLAGS').split()
                   + os.getenv('NETCDFC_CFLAGS').split())
        result = subprocess.run(
            ['ifort',  '-o', 'createcoast'] + lib_inc + ['create_coastline.f90'],
            cwd=os.path.join(self.bc_path),
            capture_output=True,
            text=True,
            check=True
        )
        if not result.stderr:
            print(str_infos["done"])
        else:
            print(str_infos["error"])

        # Execute createcoast
        print(
            f'\n Execute {color["BLUE"]}createcoast{color["END"]}...',
            end=" ", flush=True
            )

        result = subprocess.run(
            ['./createcoast'],
            cwd=os.path.join(self.bc_path),
            capture_output=True,
            text=True,
            check=True
        )
        if 'Error occured' not in result.stdout:
            print(str_infos["done"])
        else:
            print(str_infos["error"])

        print(f'\n {color["BOLD"]}[{color["END"]}'
              f'{color["GREEN"]}Boundary conditions successfully set{color["END"]}'
              f'{color["BOLD"]}]{color["END"]}\n')


class PaleoPiscesInitializer():
    """Initialize simulation parameters and files"""

    def __init__(self, pnb):
        print(f'\n {str_infos["note"]} {color["YELLOW"]}install_paleo_pisces.py{color["END"]} and '
              f'{color["YELLOW"]}configure_paleo_pisces.py{color["END"]} '
              'must have been run first')

        # Make sure folder for paleopisces model already exists
        self.pisces_path = path_checker(
            user_path,
            PISCES_FOLDER,
            existence=True,
            mod_param=[param_file, param_var['pisces']]
        )

        # Make sure folder for boundary condition already exists
        self.bc_path = path_checker(
            user_path,
            BC_FOLDER,
            existence=True,
            mod_param=[param_file, param_var['bc']]
        )

        # Make sure folder for experience containing coupled sim files in boundary condition already exists
        self.bc_exp_path = path_checker(
            os.path.join(user_path, BC_FOLDER),
            BC_EXP_FOLDER,
            existence=True,
            mod_param=[param_file, param_var['bc_exp']]
        )

        # Make sure Job doesn't already exists
        self.job_name = path_checker(
            os.path.join(self.pisces_path, "modipsl", "config", "NEMO_v6"),
            JOB_NAME,
            existence=False,
            mod_param=[param_file, param_var['job']]
        ).split('/')[-1]

        self.pnb = pnb

        self.dim_y = os.popen(
            f"ncdump -h {os.path.join(COORD_PATH, COORD_FILE)} | grep -i 'y = ' | cut -f 3 -d ' '"
        ).read()[:-1]

        print(str_infos['init_sim'])


    def config_cards(self):
        """Prepare config.card"""

        print(f'\n Preparing {color["BLUE"]}config.card{color["END"]} in {color["YELLOW"]}'
              f'{os.path.join(self.pisces_path, "modipsl", "config", "NEMO_v6", self.job_name)}'
              f'{color["END"]}...', end=" ", flush=True)

        # copying config.card
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'EXP', 'config.card_clim'),
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6', 'config.card')
        )

        # Modifying config.card
        replacer = [self.job_name, DATE_BEGIN, DATE_END, SPACE_NAME]
        pre_replacer = ['JobName=', 'DateBegin=', 'DateEnd=', 'SpaceName=']
        post_replacer = ['\n', '\n', '\n', '\n']
        find_replace_in_file(
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6', 'config.card'),
            pre_replacer, post_replacer, replacer
        )
        print(str_infos['done'])

    def install_job(self):
        """Install job"""

        print(f'\n Installing job in {color["YELLOW"]}{self.pisces_path}'
              f'/modipsl/config/NEMO_v6/{self.job_name}{color["END"]}...\n')  # , end=" ", flush=True

        str_1 = 'Hit Enter or give'
        str_2 = 'possible numbers of cores are "1" to "112" for xlarge :'
        str_3 = ('=> Submit directory .+ will be created '
            'with cards from EXPERIMENTS/ORCA2_OFF_PISCES/clim')

        result = subprocess.Popen(
            [os.path.join(self.pisces_path, 'modipsl', 'libIGCM', 'ins_job')],
            cwd=os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6'),
            stdout=subprocess.PIPE,
            encoding='ascii'
        )

        wit  = False
        wit_2 = False
        out_str_sum = ''
        while True:
            out_str = result.stdout.readline().strip()
            if result.poll() is not None:
                if re.search(str_3, out_str_sum):
                    print(f' {color["GREEN"]}[Job successfully installed]{color["END"]}\n')
                break
            if str_1 in out_str or str_2 in out_str:
                print(' |--- ' + out_str)
                wit = True
            elif wit:
                print(' |------> ' + out_str + '\n')
                wit = False
            elif 'ERROR' in out_str or 'exists already' in out_str:
                print(out_str)
                wit_2 = True
            elif wit_2:
                print(out_str)
                if ('- JobName must start with a letter' in out_str or
                    '1 invalid JobName(s) found, check the log' in out_str or
                    'Remove the existing directory' in out_str):
                    wit_2 = False
            out_str_sum += out_str

            # print(out_str)
            # if result.poll() is not None:
            #     break

        result.wait()

        # Change PeriodNb in Job

        replacer = [self.pnb]
        pre_replacer = ['PeriodNb=']
        post_replacer = ['\n']

        find_replace_in_file(
            os.path.join(self.pisces_path, 'modipsl', 'config',
                         'NEMO_v6', self.job_name, 'Job_' + self.job_name),
            pre_replacer, post_replacer, replacer
        )

        # get_outputs(os.path.join(self.pisces_path, 'file_log_out'), os.path.join(self.pisces_path, 'file_log_err'), result.read())


    def pisces_card(self):
        """prepare pisces.card"""

        print(f'\n Preparing {color["BLUE"]}pisces.card{color["END"]} in {color["YELLOW"]}{os.path.join(self.pisces_path, "modipsl", "config", "NEMO_v6", JOB_NAME, "COMP")}{color["END"]}...', end=" ", flush=True)

        shutil.copy2(
                os.path.join(SOURCES_PATH, 'EXP', 'pisces.card'),
                os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6', self.job_name, 'COMP')
        )

        # RDYN = SIM_OUTPUT_PATH
        # ListNonDel = (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X_mesh_mask.nc, mask.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X_mesh_mask.nc, mesh_hgr.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X_mesh_mask.nc, mesh_zgr.nc), \

        #              (/ccc/work/cont003/gen2212/gramoula/BC_PISCES_OFFLINE/70Ma-4X.mask.from.tmask.nc, coastmsk.nc)


        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_grid_T.nc, dyna_grid_T.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_grid_U.nc, dyna_grid_U.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_grid_V.nc, dyna_grid_V.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_grid_W.nc, dyna_grid_W.nc), \

        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_DIC.nc, data_DIC_nomask.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_Si_2.307Scale.nc, data_SIL_nomask.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_Alk_2.361Scale.nc, data_ALK_nomask.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_O2_Unit.nc, data_OXY_nomask.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_PO4_1.836Scale.nc, data_PO4_nomask.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_DOC.nc, data_DOC_nomask.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_Fer.nc, data_FER_nomask.nc), \
        #              (${pisces_UserChoices_R_DYN}/CPL-70Ma-4X-part2_SE_4715_4764_1M_NO3_2.026Scale.nc, data_NO3_nomask.nc), \

        #              (/ccc/work/cont003/gen2212/laugiema/BC_PISCES_OFFLINE/PALEOPISCES-TOOLS/FILES/weights_r144x143_paleorca2_bilinear.nc, weights_lmd144142_bilin.nc), \
        #              (/ccc/work/cont003/gen2212/laugiema/BC_PISCES_OFFLINE/PALEOPISCES-TOOLS/FILES/weights_r144x96_paleorca2_bilinear.nc, weights_2d_bilin.nc), \

        #    |         (${R_IN}/OCE/NEMO /${config_UserChoices_TagName} /${pisces_UserChoices_version}/Dust_inca_LOI/DUST_INCA_LOI6012-histAER_1M_1850.nc, dust.orca.nc), \

        #    |         (${R_IN}/OCE/NEMO/${config_UserChoices_TagName} /${pisces_UserChoices_version}/Ndep_input4MIPs/Ndep_input4MIPs_surfaceFluxes_CMIP_NCAR-CCMI-2-0_gn_185001-185012-clim.nc, ndeposition.orca.nc), \
        #    |         (${R_IN}/OCE/NEMO/${config_UserChoices_TagName} /${pisces_UserChoices_version}/par_fraction_gewex_orca_r2_clim90s00s.nc, par.orca.nc), \

        #    |         (/ccc/work/cont003/gen2212/laugiema/BC_PISCES_OFFLINE/PALEOPISCES-TOOLS/FILES/novolcdust.nc, volcdust.nc), \
        #    |         (/ccc/work/cont003/gen2212/laugiema/BC_PISCES_OFFLINE/PALEOPISCES-TOOLS/FILES/Paleosolubility1_T62-ORCA2_Mahowald.nc, solubility.orca.nc), \


        path_pisces_card = '${pisces_UserChoices_R_DYN}'


        lst = [
            ', '.join([os.path.join(path_pisces_card, MASK_FILE), 'mask.nc']),
            ', '.join([os.path.join(path_pisces_card, MASK_FILE), 'mesh_hgr.nc']),
            ', '.join([os.path.join(path_pisces_card, MASK_FILE), 'mesh_zgr.nc']),
            ', '.join([os.path.join(self.bc_path, MASK_BATHY_FILE), 'coastmsk.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_grid_T.nc'), 'dyna_grid_T.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_grid_U.nc'), 'dyna_grid_U.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_grid_V.nc'), 'dyna_grid_V.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_grid_W.nc'), 'dyna_grid_W.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_DIC.nc'), 'data_DIC_nomask.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_Si.nc'), 'data_SIL_nomask.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_Alk.nc'), 'data_ALK_nomask.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_O2_Unit.nc'), 'data_OXY_nomask.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_PO4.nc'), 'data_PO4_nomask.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_DOC.nc'), 'data_DOC_nomask.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_Fer.nc'), 'data_FER_nomask.nc']),
            ', '.join([os.path.join(path_pisces_card, FILE_PREFIX + '_NO3.nc'), 'data_NO3_nomask.nc']),
            ', '.join([os.path.join(self.bc_path, 'WEIGHTS', 'data', 'weights_r144x143_paleorca2_bilinear.nc'), 'weights_lmd144142_bilin.nc']),
            ', '.join([os.path.join(self.bc_path, 'WEIGHTS', 'data', 'weights_r144x96_paleorca2_bilinear.nc'), 'weights_2d_bilin.nc']),
            '${R_IN}/OCE/NEMO /${config_UserChoices_TagName}/${pisces_UserChoices_version}/Dust_inca_LOI/DUST_INCA_LOI6012-histAER_1M_1850.nc, dust.orca.nc',
            '${R_IN}/OCE/NEMO/${config_UserChoices_TagName}/${pisces_UserChoices_version}/Ndep_input4MIPs/Ndep_input4MIPs_surfaceFluxes_CMIP_NCAR-CCMI-2-0_gn_185001-185012-clim.nc, ndeposition.orca.nc',
            # '${R_IN}/OCE/NEMO/${config_UserChoices_TagName}/${pisces_UserChoices_version}/par_fraction_gewex_orca_r2_clim90s00s.nc, par.orca.nc',
            ', '.join([os.path.join(SOURCES_PATH, 'DATA', PAR_FILE), 'par.orca.nc']),
            # '/ccc/work/cont003/gen2212/laugiema/BC_PISCES_OFFLINE/PALEOPISCES-TOOLS/FILES/novolcdust.nc, volcdust.nc',
            ', '.join([os.path.join(SOURCES_PATH, 'DATA', 'novolcdust.nc'), 'volcdust.nc']),
            # '/ccc/work/cont003/gen2212/laugiema/BC_PISCES_OFFLINE/PALEOPISCES-TOOLS/FILES/Paleosolubility1_T62-ORCA2_Mahowald.nc, solubility.orca.nc'
            ', '.join([os.path.join(SOURCES_PATH, 'DATA', SOLUBILITY_FILE), 'solubility.orca.nc'])
        ]

        str_tot  = '), \\\n            ('.join(lst)

        replacer = [self.bc_exp_path, str_tot]
        pre_replacer = ['R_DYN=', 'ListNonDel= (']
        post_replacer = ['\n', ')\n']
        find_replace_in_file(
            os.path.join(self.pisces_path, 'modipsl', 'config',
                         'NEMO_v6', self.job_name, 'COMP', 'pisces.card'),
            pre_replacer, post_replacer, replacer
        )

        print(str_infos['done'])
        # print(f' {color["GREEN"]}[{color["BLUE"]}pisces.card {color["GREEN"]}successfully edited in {color["YELLOW"]}{os.path.join(self.pisces_path, "modipsl", "config", "NEMO_v6", JOB_NAME, "COMP")}{color["GREEN"]}]{color["END"]}')


    def modif_param_files(self):
        """modif param files"""

        print(f'\n Preparing {color["BLUE"]}file_def_nemo-pisces_offline.xml{color["END"]}, '
              f'{color["BLUE"]}file_def_nemo-pisces.xml{color["END"]}, '
              f'{color["BLUE"]}field_def_nemo-pisces.xml{color["END"]} and '
              f'{color["BLUE"]}namelist_pisces_cfg{color["END"]} and '
              f'{color["BLUE"]}namelist_top_cfg{color["END"]}...', end=" ", flush=True)

        # !!!! THIS FILE WILL NEED MODIFICATION SO MIGHT BE BETTER TO COPY THIS FILE IN SOURCE PATH
        # DO MODIFICATIONS AND THEN COPY IT FROM SOURCES PATH shutil.copy2(os.path.join(SOURCES_PATH,...
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'XML', 'file_def_nemo-pisces_offline.xml'),
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6', self.job_name, 'PARAM', 'XML')
        )

        shutil.copy2(
            os.path.join(SOURCES_PATH, 'XML', 'file_def_nemo-pisces.xml'),
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6', self.job_name, 'PARAM', 'XML')
        )

        shutil.copy2(
            os.path.join(SOURCES_PATH, 'XML', 'field_def_nemo-pisces.xml'),
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6', self.job_name, 'PARAM', 'XML')
        )

        # !!!! SAME as FILE ABOVE file_def_nemo-pisces_offline.xml
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'NAMELIST', 'namelist_pisces_cfg'),
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6', self.job_name, 'PARAM', 'NAMELIST')
        )

        shutil.copy2(
            os.path.join(SOURCES_PATH, 'NAMELIST', 'namelist_top_cfg'),
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6', self.job_name, 'PARAM', 'NAMELIST', 'ORCA2')
        )

        replacer = [self.dim_y, self.dim_y]
        pre_replacer = ['   jpjdta      =     ', '   jpjglo      =     ']
        post_replacer = [
            '               !  2nd    "         "    ( >= jpj )',
            '               !  2nd    -                  -    --> j  =jpjdta'
            ]
        find_replace_in_file(
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6', self.job_name, 'PARAM', 'NAMELIST', 'ORCA2', 'namelist_offline_clim_cfg'),
            pre_replacer, post_replacer, replacer
        )

        print(str_infos['done'])

        print(f'\n {color["BOLD"]}[{color["END"]}'
              f'{color["GREEN"]}Paleo pisces successfully initialized{color["END"]}'
              f'{color["BOLD"]}]{color["END"]}\n')
