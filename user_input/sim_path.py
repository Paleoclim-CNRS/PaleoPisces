"""
Paths to boundary condition files

SIMULATION_TYPE - 'clim' (climatology) or 'ia' (inter annual)
SIM_OUTPUT_PATH - Where model output files are located
FILE_PREFIX     - [FILE_PREFIX]_grid_[X].nc with [X] = T, U, V or W
MASK_PATH       - Where mesh mask file is located
MASK_FILE       - Name of mesh mask file
BATHY_PATH      - Where bathy and subbasin files are located
BATHY_FILE      - Name of bathy file
SUBBASIN_FILE   - Name of subbasin file
MASK_BATHY_FILE - Define name of Mask file generated from bathy file using coast tools
"""

SIM_OUTPUT_PATH = '/ccc/store/cont003/gen2212/p519don/IGCM_OUT/IPSLCM5A2/PROD/paleo/C30MaTotV1-3X'
FILE_PREFIX     = 'C30MaTotV1-3X_SE_4805_4854_1M'
MASK_PATH       = '/ccc/work/cont003/gen2212/p519don'
MASK_FILE       = 'C30MaTMP_mesh_mask.nc'
BATHY_PATH      = '/ccc/work/cont003/gen2212/p519don/BC_PALEOIPSL/NEMO/30MaTot'
BATHY_FILE      = 'bathyORCA2.RupelianTotalV1.nc'
SUBBASIN_FILE   = 'subbasins_rupelianTot.nc'

MASK_BATHY_FILE = 'mask_from_Bathymetry_TEST.nc'
