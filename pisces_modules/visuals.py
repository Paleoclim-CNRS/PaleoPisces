"""
Contains all visual elements to make prints clearer
"""

color = {
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'DARKCYAN': '\033[36m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'ORANGE': '\033[33m',
    'RED': '\033[91m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
    'END': '\033[0m'
}


# class Color:
#     """
#     Color class
#     """
#     PURPLE= '\033[95m'
#     CYAN= '\033[96m'
#     DARKCYAN= '\033[36m'
#     BLUE= '\033[94m'
#     GREEN= '\033[92m'
#     YELLOW= '\033[93m'
#     ORANGE= '\033[33m'
#     RED= '\033[91m'
#     BOLD= '\033[1m'
#     UNDERLINE= '\033[4m'
#     END= '\033[0m'


paleopisces_title = (
    f'''\n                                     {color["DARKCYAN"]}_
                                   /  /
                ____     ____     /  /  ___      ____
              /   _  \  |___  \  /  / /  _  \  /   _  \ 
             /  /_/  / /  /   / /  / /   ___/ /  /_/  /
            /  ____ /  \_____/ /_ /  \_____/  \______/
           /  /{color["END"]}                {color["PURPLE"]}_{color["END"]}
          {color["DARKCYAN"]}/_ /{color["END"]}               {color["PURPLE"]}/_ /
                   ____      _    _____   _____   ___      _____
                 /   _  \  /  / / ____/ /  ___/ /  _  \  / ____/
                /  /_/  / /  / (___  ) /  /__  /   ___/ (___  )
               /  ____ / /_ / /_____/ /_____/  \_____/ /_____/
              /  /
             /_ /{color["END"]}
''')

SPACE = ' '

install_pisces = ('\n\n' + 24 * SPACE +
                  f'{color["BOLD"]}{color["UNDERLINE"]}INSTALL PALEO PISCES MODEL{color["END"]}\n')

set_up_bc = ('\n\n' + 24 * SPACE +
             f'{color["BOLD"]}{color["UNDERLINE"]}SET UP BOUNDARY CONDITIONS{color["END"]}\n')

init_sim = ('\n\n' + 26 * SPACE +
             f'{color["BOLD"]}{color["UNDERLINE"]}INITIALIZE SIMULATION{color["END"]}\n')

# steps_str = [f'{color["BOLD"]}{color["UNDERLINE"]}SET UP PISCES MODEL{color["END"]}',
#              f'{color["BOLD"]}{color["UNDERLINE"]}MODIFY GENERAL EXPERIENCE FILE{color["END"]}',
#              (f'{color["BOLD"]}{color["UNDERLINE"]}'
#               f'CREATION OF INITIAL/BOUNDARY CONDITIONS{color["END"]}')]

# space = '                                            '

# steps_title = []

# for step in steps_str:
#     steps_title.append('\n\n' + space[int(np.round(len(step)/2))::] + step)

# str1 = '\n ---------------------------------------------------\n Steps:\n'
# len_stp = len(steps_str)
# str2 = ''
# for i, step in zip(np.arange(len_stp)+1, steps_str):
#     str2 += f' [{i}/{len_stp}] {step}\n'
# str3 = ' ---------------------------------------------------'
# steps_overview = str1 + str2 + str3

done = f'{color["GREEN"]}[DONE]{color["END"]}'
error = f'{color["RED"]}[ERROR]{color["END"]}'
warning = f'{color["ORANGE"]}[WARNING]{color["END"]}'
note = f'{color["PURPLE"]}[NOTE]{color["END"]}'
# skip_str = f'{color["BOLD"]}[SKIPPED]{color["END"]}'


str_infos = {
    'paleopisces_title': paleopisces_title,
    'install_pisces': install_pisces,
    'set_up_bc': set_up_bc,
    'init_sim': init_sim,
    'done': done,
    'error':error,
    'warning':warning,
    'note':note,
}
