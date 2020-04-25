import os
import sys

sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from MainWindow import MainWindow

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1200x600')

    main_win = MainWindow(root)

    root.mainloop()
