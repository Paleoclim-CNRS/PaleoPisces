"""
Processes to set up PALEO PISCES
"""

import os
import subprocess
import shutil
import glob
import re
from importlib import import_module
# import xarray as xr
# import numpy as np

from pisces_modules.visuals import color, str_infos

from pisces_modules.utils import (path_checker,
                                  find_in_str,
                                  find_replace_in_file)

from pisces_modules.paths import (user,
                                        user_path,
                                        WORK_PATH,
                                        SOURCES_PATH,
                                        JB_PATH,
                                        IGCM_PATH)

if not os.path.isdir(os.path.join(WORK_PATH, 'user_input', user)):
    os.makedirs(os.path.join(WORK_PATH, 'user_input', user))
    shutil.copy2(os.path.join(SOURCES_PATH, 'USER_INPUT', 'sim_path.py'),
                        os.path.join(WORK_PATH, 'user_input', user))
    shutil.copy2(os.path.join(SOURCES_PATH, 'USER_INPUT', 'config_card.py'),
                        os.path.join(WORK_PATH, 'user_input', user))

sim_file = import_module(f'user_input.{user}.sim_path')
SIM_OUTPUT_PATH = getattr(sim_file, 'SIM_OUTPUT_PATH')
FILE_PREFIX = getattr(sim_file, 'FILE_PREFIX')
MASK_PATH = getattr(sim_file, 'MASK_PATH')
MASK_FILE = getattr(sim_file, 'MASK_FILE')
BATHY_PATH = getattr(sim_file, 'BATHY_PATH')
BATHY_FILE = getattr(sim_file, 'BATHY_FILE')
SUBBASIN_FILE = getattr(sim_file, 'SUBBASIN_FILE')
MASK_BATHY_FILE = getattr(sim_file, 'MASK_BATHY_FILE')

config_file = import_module(f'user_input.{user}.config_card')
JOB_NAME = getattr(config_file, 'JOB_NAME')
DATE_BEGIN = getattr(config_file, 'DATE_BEGIN')
DATE_END = getattr(config_file, 'DATE_END')
SPACE_NAME = getattr(config_file, 'SPACE_NAME')

# from pisces_modules.user_entry.sim_path import (SIM_OUTPUT_PATH,
#                                                 FILE_PREFIX,
#                                                 MASK_PATH,
#                                                 MASK_FILE,
#                                                 BATHY_PATH,
#                                                 BATHY_FILE,
#                                                 SUBBASIN_FILE,
#                                                 MASK_BATHY_FILE)

# from pisces_modules.user_entry.config_card import (JOB_NAME,
#                                                    DATE_BEGIN,
#                                                    DATE_END,
#                                                    SPACE_NAME)


class PaleoPiscesInstaller():
    """Install paleo pisces model"""

    def __init__(self, nemo):
        self.nemo = nemo
        self.icmc_username = 'icmc_users'
        self.icmc_password = 'icmc2022'

        print(str_infos['paleopisces_title'])

        prpt = (f' Enter path + folder name where PALEO PISCES will be installed:\n'
            f' (From {color["YELLOW"]}{user_path}{color["END"]})\n ')
        self.pisces_path, self.pisces_folder = path_checker(
            user_path,
            input(prpt),
            folder_exist=True
        )

        print(str_infos["install_pisces"])

        os.makedirs(self.pisces_path)


    def dl_modipsl(self):
        """Downloads modipsl"""
        print(f'\n Downloading {color["BLUE"]}modipsl{color["END"]}...',
            end=" ", flush=True)
        result = subprocess.run(
            ['svn', 'co',
             'http://forge.ipsl.jussieu.fr/igcmg/svn/modipsl/trunk', 'modipsl',
             '--username', self.icmc_username,
             '--password', self.icmc_password],
            cwd=self.pisces_path,
            capture_output=True,
            text=True,
            check=True
        )
        if not result.stderr:
            print(str_infos["done"])
        else:
            print(str_infos["error"])


    def load_nemo(self):
        """
        Load nemo, version is specified when instantiating PaleoPiscesInstaller class
        (see install_paleo_pisces.py).
        subprocess.Popen can be used instead of subprocess.run in order to print realtime output
        by using it in tandem with the Popen.poll method. Output to display can be filtered
        with if condition (check example code below `if 'username' in out_str...`).
        This is useful if the shell command require a username or a password to enter 
        (you wont be able to see the request with subprocess.run...).
        code:
            result = subprocess.Popen(
            ['./model', self.nemo],
            cwd=os.path.join(self.pisces_path, 'modipsl', 'util'),
            stdout=subprocess.PIPE
            )
            # Poll process.stdout to show stdout live
            while True:
                out_str = result.stdout.readline().strip().decode("utf-8")
                if result.poll() is not None:
                    break
                if 'username' in out_str or 'password' in out_str:
                    print(out_str)
            result.wait()
        """
        print(f'\n Loading {color["BLUE"]}{self.nemo}{color["END"]}...', end=" ", flush=True)

        result = subprocess.run(
            ['./model', self.nemo],
            cwd=os.path.join(self.pisces_path, 'modipsl', 'util'),
            input=f'{self.icmc_username}\n{self.icmc_password}\n',
            capture_output=True,
            text=True,
            check=True
        )

        if not result.stderr:
            print(str_infos["done"])
        else:
            print(str_infos["error"])


    def compile_xios(self):
        """Compile XIOS for NEMO
        result = subprocess.Popen(
            ['./make_xios', '--arch', 'X64_IRENE', '--full', '--prod', '--job', '8'],
            cwd=os.path.join(self.pisces_path, 'modipsl', 'modeles', 'XIOS'),
            stdout=subprocess.PIPE
        )
        # Poll process.stdout to show stdout live
        while True:
            out_str = result.stdout.readline().strip().decode("utf-8")
            if result.poll() is not None:
                break
            # if '?' in out_str:
            print(out_str)
        result.wait()
        """

        print(f'\n Compiling {color["BLUE"]}XIOS{color["END"]}...', 
            end=" ", flush=True)

        result = subprocess.run(
            ['./make_xios', '--arch', 'X64_IRENE', '--full', '--prod', '--job', '8'],
            cwd=os.path.join(self.pisces_path, 'modipsl', 'modeles', 'XIOS'),
            capture_output=True,
            text=True,
            check=True
        )

        if 'Build command finished' in result.stdout:
            str_elem = find_in_str("->TOTAL: ", "\n", result.stdout, reverse_find=True)
            print(color["GREEN"] + '[Build finished in ' + str_elem + ']' + color["END"])
        else:
            print(str_infos["error"])


    def cp_source_files(self):
        """Copy sources files into PISCES folder"""

        # cp arch-X64_IRENE.fcm file
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'ARCH', 'arch-X64_IRENE.fcm'),
            os.path.join(
                self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM', 'ARCH')
        )
        # cp cpp_ORCA2_OFF_PISCES.fcm file
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'ARCH', 'cpp_ORCA2_OFF_PISCES.fcm'),
            os.path.join(
                self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM', 'CONFIG', 'ORCA2_OFF_PISCES')
        )
        # Creates Creating MY_SRC folder
        os.mkdir(os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM',
            'CONFIG', 'ORCA2_OFF_PISCES', 'MY_SRC'))
        # Copying MY_SRC/*.F90 files into user model directory
        files2copy = glob.glob(os.path.join(JB_PATH, '*.F90'))
        for file_ in files2copy:
            shutil.copy2(file_,
                os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM',
                    'CONFIG', 'ORCA2_OFF_PISCES', 'MY_SRC'))

        shutil.copy2(os.path.join(SOURCES_PATH, 'XML', 'iodef.xml'),
            os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM',
                'CONFIG', 'ORCA2_OFF_PISCES', 'EXP00'))

        shutil.copy2(os.path.join(SOURCES_PATH, 'XML', 'field_def.xml'),
                     os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM',
                'CONFIG', 'ORCA2_OFF_PISCES', 'SHARED'))

        shutil.copy2(os.path.join(SOURCES_PATH, 'NAMELIST', 'namelist_pisces_ref'),
                     os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM',
                'CONFIG', 'ORCA2_OFF_PISCES', 'SHARED'))

        # # cp EXP00 files
        # files2copy = glob.glob(os.path.join(
        #     MARIE_PATH, 'BC_PISCES_OFFLINE', 'PALEOPISCES-TOOLS', 'ROUTINES', 'EXP00', '*'))
        # for file_ in files2copy:
        #     shutil.copy2(file_,
        #                  os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM',
        #                               'CONFIG', 'ORCA2_OFF_PISCES', 'EXP00'))

        # # cp SHARED files
        # files2copy = glob.glob(os.path.join(
        #     MARIE_PATH, 'BC_PISCES_OFFLINE', 'PALEOPISCES-TOOLS', 'ROUTINES', 'SHARED', '*'))
        # for file_ in files2copy:
        #     shutil.copy2(file_,
        #         os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM', 'CONFIG', 'SHARED'))

    def compile_nemo(self):
        """Compile NEMO"""

        print(f'\n Compiling {color["BLUE"]}NEMO{color["END"]}...', end=" ", flush=True)
        result = subprocess.run(
            ['./makenemo', '-n', 'ORCA2_OFF_PISCES', '-r', 'ORCA2_OFF_PISCES', '-m',
            'X64_IRENE', '-j', '8'],
            cwd=os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM', 'CONFIG'),
            capture_output=True,
            text=True,
            check=True
        )
        if 'Build command finished' in result.stdout:
            str_elem = find_in_str("->TOTAL: ", "\n", result.stdout, reverse_find=True)
            print(color["GREEN"] + '[Build finished in ' + str_elem + ']' + color["END"])
        else:
            print(str_infos["error"])


        # Copying generated executable
        print(f'\n Copying executable {color["BLUE"]}nemo.exe{color["END"]} as '
        f'{color["BLUE"]}orca2offpisces.exe{color["END"]} in '
        f'{color["YELLOW"]}{self.pisces_folder}/modipsl/bin/{color["END"]}...', end=" ", flush=True)
        shutil.copy2(
            os.path.join(
                self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM',
                'CONFIG', 'ORCA2_OFF_PISCES', 'BLD', 'bin', 'nemo.exe'),
            os.path.join(
                self.pisces_path, 'modipsl', 'bin', 'orca2offpisces.exe')
        )
        print(str_infos["done"])

        print(f'\n {color["BOLD"]}[{color["END"]}'
              f'{color["GREEN"]}PALEO PISCES successfully installed{color["END"]}'
              f'{color["BOLD"]}]{color["END"]}\n')


class PaleoPiscesConfigurator():
    """Set up boundary conditions"""

    def __init__(self):
        print(f'\n {str_infos["note"]} {color["YELLOW"]}install_paleo_pisces.py{color["END"]} '
            'must have been run first\n')

        prpt = (' Enter path + folder name where PALEO PISCES is installed:\n'
            f' (From {color["YELLOW"]}{user_path}{color["END"]})\n ')
        self.pisces_path, self.pisces_folder = path_checker(
            user_path,
            input(prpt),
            folder_exist=False
        )

        prpt2 = ('\n Enter path + folder name where Boundary condition folder will be set up:\n'
            f' (From {color["YELLOW"]}{user_path}{color["END"]})\n ')
        self.bc_path, self.bc_folder = path_checker(
            user_path,
            input(prpt2),
            folder_exist=True
        )

        print(str_infos["set_up_bc"])

        os.makedirs(os.path.join(self.bc_path, FILE_PREFIX), exist_ok=True)

    def mod_exp_files(self):
        """Modify general experience files"""

        shutil.copy2(
            os.path.join(
                SOURCES_PATH, 'NAMELIST', 'namelist_offline_clim_cfg_clim'),
            os.path.join(
                self.pisces_path, 'modipsl', 'config', 'NEMO_v6',
                'GENERAL', 'PARAM', 'NAMELIST', 'ORCA2', 'namelist_offline_clim_cfg'
            )
        )


    def cp_bc_files(self):
        """Copy BC files into $USER directory"""

        print(f'\n Making {color["BLUE"]}symlinks{color["END"]} of BC files into '
              f'{color["YELLOW"]}{os.path.join(self.bc_path, FILE_PREFIX)}{color["END"]}...',
              end=" ", flush=True)
        # SYMLINKS
        os.symlink(
            os.path.join(SOURCES_PATH, 'DATA', 'coordinates_paleorca2_yd.nc'),
                os.path.join(self.bc_path, FILE_PREFIX, 'coordinates_paleorca2_yd.nc')
        )
        os.symlink(
            os.path.join(MASK_PATH, MASK_FILE),
            os.path.join(self.bc_path, FILE_PREFIX, MASK_FILE)
        )
        os.symlink(
            os.path.join(BATHY_PATH, BATHY_FILE),
            os.path.join(self.bc_path, FILE_PREFIX, BATHY_FILE)
        )
        os.symlink(
            os.path.join(BATHY_PATH, SUBBASIN_FILE),
            os.path.join(self.bc_path, FILE_PREFIX, SUBBASIN_FILE)
        )
        shutil.copy2(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_grid_T.nc'),
            os.path.join(self.bc_path, FILE_PREFIX)
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_grid_U.nc'),
            os.path.join(self.bc_path, FILE_PREFIX,
                         FILE_PREFIX + '_grid_U.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_grid_V.nc'),
            os.path.join(self.bc_path, FILE_PREFIX,
                         FILE_PREFIX + '_grid_V.nc')
        )
        shutil.copy2(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_grid_W.nc'),
            os.path.join(self.bc_path, FILE_PREFIX)
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'OCE', 'Analyse',
                         'SE', FILE_PREFIX + '_diaptr.nc'),
            os.path.join(self.bc_path, FILE_PREFIX,
                         FILE_PREFIX + '_diaptr.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'MBG', 'Analyse',
                         'SE', FILE_PREFIX + '_diad_T.nc'),
            os.path.join(self.bc_path, FILE_PREFIX,
                         FILE_PREFIX + '_diad_T.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'MBG', 'Analyse',
                         'SE', FILE_PREFIX + '_ptrc_T.nc'),
            os.path.join(self.bc_path, FILE_PREFIX,
                         FILE_PREFIX + '_ptrc_T.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'ATM', 'Analyse',
                         'SE', FILE_PREFIX + '_histmth.nc'),
            os.path.join(self.bc_path, FILE_PREFIX,
                         FILE_PREFIX + '_histmth.nc')
        )
        os.symlink(
            os.path.join(SIM_OUTPUT_PATH, 'ICE', 'Analyse',
                         'SE', FILE_PREFIX + '_icemod.nc'),
            os.path.join(self.bc_path, FILE_PREFIX, FILE_PREFIX + '_icemod.nc')
        )
        print(str_infos["done"])


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


        # Because of versions of open mpi (2.0.4) needed for compilation of XIOS,
        # The xarray module can't be loaded with python 3.7.5. 
        #  So the 2 steps above:
        # - Put sic in icemod as siconc in grid_t
        # - Compute wocetr_eff and put it in grid_w
        # are not used.
        # Fix have been found by using older version of python (3.7.2)
        # But compilation of XIOS and NEMO take around 25min instead of 5min 

        # Use of UpadteVariable.ksh
        #-----------------------------

        print(f'\n Adding {color["BLUE"]}siconc{color["END"]} and {color["BLUE"]}wocetr_eff{color["END"]} '
              f'variables in {color["YELLOW"]}{FILE_PREFIX}_grid_T.nc{color["END"]} and {color["YELLOW"]}'
              f'{FILE_PREFIX}_grid_W.nc{color["END"]}...', end=" ", flush=True)

        shutil.copy2(
            os.path.join(SOURCES_PATH, 'SCRIPT', 'UpdateVariable_sic.ksh'),
            os.path.join(self.bc_path)
        )
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'SCRIPT', 'UpdateVariable_woce.ksh'),
            os.path.join(self.bc_path)
        )

        replacer = [os.path.join(self.bc_path, FILE_PREFIX), FILE_PREFIX + '_grid_T.nc', FILE_PREFIX + '_icemod.nc']
        pre_replacer = ['dir=', 'file_t=', 'file_icemod=']
        post_replacer = ['\n', '\n', '\n']
        find_replace_in_file(os.path.join(self.bc_path, 'UpdateVariable_sic.ksh'),
            pre_replacer, post_replacer, replacer)

        replacer = [os.path.join(self.bc_path, FILE_PREFIX), FILE_PREFIX + '_grid_W.nc', MASK_FILE]
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

        # get_outputs(os.path.join(self.bc_path, 'log_out_1'),os.path.join(self.bc_path, 'log_err_1'), result1)
        # get_outputs(os.path.join(self.bc_path, 'log_out_2'),os.path.join(self.bc_path, 'log_err_2'), result2)


        # Extract files _NO3, _02, from ptrc_T file...
        print(f'\n Extract variables ({color["BLUE"]}NO3{color["END"]}, '
              f'{color["BLUE"]}PO4{color["END"]}, {color["BLUE"]}DIC{color["END"]}...)'
              f' in files from {color["YELLOW"]}{FILE_PREFIX}_ptrc_T.nc{color["END"]}...',
              end=" ", flush=True)

        shutil.copy2(
            os.path.join(SOURCES_PATH, 'SCRIPT', 'ScaleNutrients.ksh'),
            os.path.join(self.bc_path)
        )

        replacer = [os.path.join(self.bc_path, FILE_PREFIX),
                    FILE_PREFIX]
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

        print(str_infos["done"])
        #-----------------------------


    def weight_tool(self):
        """Set up weight tool to compute weights"""

        # Compile weight tool
        print(f'\n Compiling {color["BLUE"]}weight tool{color["END"]}...', end=" ", flush=True)
        result = subprocess.run(
            ['./maketools', '-m', 'X64_IRENE', '-n', 'WEIGHTS'],
            cwd=os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM', 'TOOLS'),
            capture_output=True,
            text=True,
            check=True
        )
        if 'Build command finished' in result.stdout:
            str_elem = find_in_str("->TOTAL: ", "\n", result.stdout, reverse_find=True)
            print(color["GREEN"] + '[Build finished in ' + str_elem + ']' + color["END"])
        else:
            print(str_infos["error"])
        
        # Copy folder modipsl/modeles/NEMOGCM/TOOLS/WEIGHTS into BC folder
        shutil.copytree(
            os.path.join(self.pisces_path, 'modipsl', 'modeles', 'NEMOGCM', 'TOOLS', 'WEIGHTS'),
            os.path.join(self.bc_path, 'WEIGHTS')
        )

        # Create folder data in folder WEIGHTS
        os.mkdir(os.path.join(self.bc_path, 'WEIGHTS', 'data'))

        # Copy files in data folder
        shutil.copy2(
            os.path.join(IGCM_PATH, 'Dust_inca_LOI', 'DUST_INCA_LOI6012-histAER_1M_1850.nc'),
            os.path.join(self.bc_path, 'WEIGHTS', 'data')
        )
        shutil.copy2(
            os.path.join(
                IGCM_PATH, 'Ndep_input4MIPs',
                'Ndep_input4MIPs_surfaceFluxes_CMIP_NCAR-CCMI-2-0_gn_185001-185012-clim.nc'
                ),
            os.path.join(self.bc_path, 'WEIGHTS', 'data')
        )
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'DATA', 'coordinates_paleorca2_yd.nc'),
            os.path.join(self.bc_path, 'WEIGHTS', 'data')
        )

        # Copy namelist_r144x143_paleorca2_bilin and namelist_r144x96_paleorca2_bilin
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'NAMELIST', 'namelist_r144x143_paleorca2_bilin'),
            os.path.join(self.bc_path, 'WEIGHTS', 'data')
        )
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'NAMELIST', 'namelist_r144x96_paleorca2_bilin'),
            os.path.join(self.bc_path, 'WEIGHTS', 'data')
        )

        # Creates weight files
        print(f'\n Creating {color["BLUE"]}weight files{color["END"]}...', end=" ", flush=True)
        weight_scripgrid_143 = subprocess.run(['../scripgrid.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x143_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        weight_scrip_143 = subprocess.run(['../scrip.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x143_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        weight_scripshape_143 = subprocess.run(['../scripshape.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x143_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        weight_scripgrid_96 = subprocess.run(['../scripgrid.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x96_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        weight_scrip_96 = subprocess.run(['../scrip.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x96_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        weight_scripshape_96 = subprocess.run(['../scripshape.exe'],
            cwd=os.path.join(self.bc_path, 'WEIGHTS', 'data'),
            capture_output=True,
            input='namelist_r144x96_paleorca2_bilin\n',
            encoding='ascii',
            check=True
        )
        if (not weight_scripgrid_143.stderr and not weight_scrip_143.stderr 
            and not weight_scripshape_143.stderr and not weight_scripgrid_96.stderr
            and not weight_scrip_96.stderr and not weight_scripshape_96.stderr):
            print(str_infos["done"])
        else:
            print(str_infos["error"])


    def coastal_mask(self):
        """Compute coastline tool for mask"""

        # copy bathy file
        os.symlink(
            os.path.join(BATHY_PATH, BATHY_FILE),
            os.path.join(self.bc_path, BATHY_FILE)
        )

        # copy create_coastline.f90
        shutil.copy2(
            os.path.join(SOURCES_PATH, 'SRC', 'create_coastline.f90'),
            os.path.join(self.bc_path)
        )

        # Modify create_coastline.f90
        replacer = [BATHY_FILE, MASK_BATHY_FILE, MASK_BATHY_FILE]
        pre_replacer = ['status = nf90_open("', 'status = nf90_create("', 'status = nf90_open("']
        post_replacer = ['",nf90_nowrite,ncid1)', '",nf90_noclobber,ncid3)', '",nf90_write,ncid3)']
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
              f'{color["YELLOW"]}setup_boudary_conditions.py{color["END"]} '
              'must have been run first\n')

        prpt = (' Enter path + folder name where PALEO PISCES is installed:\n'
               f' (From {color["YELLOW"]}{user_path}{color["END"]})\n ')
        self.pisces_path, self.pisces_folder = path_checker(
            user_path,
            input(prpt),
            folder_exist=False
        )
        prpt2 = ('\n Enter path + folder name where Boundary condition folder is set up:\n'
            f' (From {color["YELLOW"]}{user_path}{color["END"]})\n ')
        self.bc_path, self.bc_folder = path_checker(
            user_path,
            input(prpt2),
            folder_exist=False
        )

        self.job_path, self.job_name = path_checker(
            os.path.join(self.pisces_path, "modipsl", "config", "NEMO_v6"),
            JOB_NAME,
            folder_exist=True
        )

        self.pnb = pnb

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

        # if os.path.isfile(os.path.join(
        #             self.pisces_path, 'modipsl', 'config', 'NEMO_v6', JOB_NAME, 'Job_' + JOB_NAME)):
        #     print(f'\n\n {str_infos["error"]} {color["BLUE"]}{JOB_NAME}{color["END"]} '
        #           f'already exists in {color["YELLOW"]}'
        #           f'{os.path.join(self.pisces_path, "modipsl", "config", "NEMO_v6")}{color["END"]}'
        #           f'\n Remove the existing directory or change '
        #           f'{color["BLUE"]}JOB_NAME{color["END"]} in '
        #           f'{color["YELLOW"]}'
        #           f'{os.path.join(WORK_PATH, "pisces_modules", "user_entry", "config_card.py")}'
        #           f'{color["END"]}')
        #     sys.exit(f'\n{color["RED"]}[PROGRAM EXITED]{color["END"]}\n')


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
            '${R_IN}/OCE/NEMO/${config_UserChoices_TagName}/${pisces_UserChoices_version}/par_fraction_gewex_orca_r2_clim90s00s.nc, par.orca.nc',
            '/ccc/work/cont003/gen2212/laugiema/BC_PISCES_OFFLINE/PALEOPISCES-TOOLS/FILES/novolcdust.nc, volcdust.nc',
            '/ccc/work/cont003/gen2212/laugiema/BC_PISCES_OFFLINE/PALEOPISCES-TOOLS/FILES/Paleosolubility1_T62-ORCA2_Mahowald.nc, solubility.orca.nc'
        ]

        str_tot  = '), \\\n            ('.join(lst)

        replacer = [os.path.join(self.bc_path, FILE_PREFIX), str_tot]
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
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6',
                         self.job_name, 'PARAM', 'NAMELIST')
        )

        shutil.copy2(
            os.path.join(SOURCES_PATH, 'NAMELIST', 'namelist_top_cfg'),
            os.path.join(self.pisces_path, 'modipsl', 'config', 'NEMO_v6',
                         self.job_name, 'PARAM', 'NAMELIST', 'ORCA2')
        )

        print(str_infos['done'])

        print(f'\n {color["BOLD"]}[{color["END"]}'
              f'{color["GREEN"]}Paleo pisces successfully initialized{color["END"]}'
              f'{color["BOLD"]}]{color["END"]}\n')
