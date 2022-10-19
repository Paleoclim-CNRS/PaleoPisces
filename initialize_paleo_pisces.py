"""
Initializes Pisces simulation
"""

from pisces_modules.process import PaleoPiscesInitializer

PERIOD_NB = '330'

initializer = PaleoPiscesInitializer(PERIOD_NB)

initializer.config_cards()
initializer.install_job()
initializer.pisces_card()
initializer.modif_param_files()
