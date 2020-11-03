import os
import sys

sys.path.append(os.path.dirname(__file__))

import tkinter as tk

from loguru import logger

from source_MainWindow import MainWindow
from source_utility import permission_denied_test


@logger.catch()
def main():
    root = tk.Tk()
    root.geometry('1350x800')

    permission_denied_test()

    try:
        print(f'Проект {projectfilename}')
        ini = os.path.normpath(projectfilename)
    except:
        ini = None

    main_win = MainWindow(root, projectfilename=ini)

    root.mainloop()


if __name__ == '__main__':

    log_path = os.path.join(os.path.dirname(__file__), 'sources_debug.log')
    logger.add(log_path, format="{time} {level} {message}",
               level='ERROR', rotation='10MB', compression='zip')

    main()
