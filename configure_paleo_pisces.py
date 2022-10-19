"""
Set up boundary conditions in $USER directory
"""

from pisces_modules.process import PaleoPiscesConfigurator

configurator = PaleoPiscesConfigurator()

configurator.mod_exp_files()
configurator.cp_bc_files()
configurator.weight_tool()
configurator.coastal_mask()
