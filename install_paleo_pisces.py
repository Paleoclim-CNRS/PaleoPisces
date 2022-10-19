"""
Installs PALEO PISCES
"""

from pisces_modules.process import PaleoPiscesInstaller

NEMO = 'NEMO_v6.1'

installer = PaleoPiscesInstaller(NEMO)

installer.dl_modipsl()
installer.load_nemo()
installer.compile_xios()
installer.cp_source_files()
installer.compile_nemo()
