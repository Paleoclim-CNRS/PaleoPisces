"""
All the necessary paths
"""

import os

# Predefined variables
user = os.getenv('USER')

# PATHS
user_path = f'/ccc/work/cont003/gen2212/{user}'
WORK_PATH = '/ccc/work/cont003/gen2212/gen2212/PaleoPisces'
SOURCES_PATH = os.path.join(WORK_PATH, 'src')
MARIE_PATH = '/ccc/work/cont003/gen2212/laugiema'
JB_PATH = ('/ccc/work/cont003/gen2212/p25ladan/PALEO-PISCES-revMarie/'
           'modipsl/modeles/NEMOGCM/CONFIG/ORCA2_OFF_PISCES/MY_SRC')
IGCM_PATH = '/ccc/work/cont003/igcmg/igcmg/IGCM/OCE/NEMO/ORCA2_OFF_PISCES/v3.6_stable'
