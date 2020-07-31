import os
import sys

sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from source_MainWindow import MainWindow

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1180x800')

    try:
        print(f'Проект {projectfilename}')
        ini = os.path.normpath(projectfilename)
    except:
        ini = None

    main_win = MainWindow(root, projectfilename=ini)

    root.mainloop()
