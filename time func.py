from tkinter import *
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt


class Func:
    def __init__(self):
        self.out = np.empty(1)
        self.b = 0
        self.k = 0

    def grid_parcer(self):
        #### .PL DECODER
        with open(r'C:\Users\Никита\Dropbox\work_cloud\source_cont\entry_data\KUVSH.GRD', 'r') as file:
            lines = file.readlines()
        self.out = np.array(lines[15].split(), dtype=float)
        return self.out

    def linear_dif(self, y1, x1, y2, x2):
        self.k = (y2 - y1) / (x2 - x1)
        self.b = y1 - (y2 - y1) * x1 / (x2 - x1)
        return self.k, self.b


def solve(x, k, b):
    f = k * x + b
    return f


if __name__ == '__main__':
    entry_f = np.array((0, 1, 0.8, 0.5, 0))
    entry_t = np.array((0, 1e-8, 0.5e-8, 0.2e-7, 1e-7))
    time_cell = Func().grid_parcer()
    dt = time_cell[-1] / len(time_cell)
    time = 0
    time_count = []
    func_out = np.zeros(1)
    for i in range(len(entry_t) - 1):
        k, b = Func().linear_dif(entry_f[i], entry_t[i], entry_f[i + 1], entry_t[i + 1])
        print(f'k = {k} , b = {b}')

        while time <= entry_t[i + 1]:
            func_out = np.append(func_out, solve(time, k, b))
            time += dt
            time_count.append(time)
    func_out = np.delete(func_out, 0)
    func_out = np.delete(func_out, -1)
    time_count = np.array(time_count)
    time_count = np.delete(time_count, -1)
    time_count[-1] = entry_t[-1]
    print(func_out.shape)
    print('заданныйэ = ', time_cell.shape, time_cell[-1])
    print('по факту = ', time_count.shape, time_count[-1])
    plt.plot(time_count, func_out)
    plt.show()
