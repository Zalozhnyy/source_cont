import os
import sys

sys.path.append(os.path.dirname(__file__))

import tkinter as tk

from source_MainWindow import MainWindow


def main():
    root = tk.Tk()
    root.geometry('1350x800')

    # permission_denied_test()

    try:
        print(f'Проект {projectfilename}')
        ini = os.path.normpath(projectfilename)
    except Exception:
        ini = None

    main_win = MainWindow(root, projectfilename=ini)
    root.mainloop()


if __name__ == '__main__':

    main()
