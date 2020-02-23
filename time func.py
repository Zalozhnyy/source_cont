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
    entry_f = np.array((1, 0.8, 0.6, 0.4, 0.2, 0))
    entry_t = np.array((1e-10, 1e-9, 2e-9, 5e-9, 1e-8, 1e-7))
    time_cell = Func().grid_parcer()

    if entry_t[-1] != time_cell[-1]:
        entry_t = np.append(entry_t, time_cell[-1])
        entry_f = np.append(entry_f, 0)
    if entry_t[0] != 0 and entry_f[0] != 0:
        entry_t = np.insert(entry_t, 0, 0)
        entry_f = np.insert(entry_f, 0, 0)

    for i in range(len(entry_t) - 1):
        if entry_t[i] < entry_t[i + 1]:
            print(f'Value error время уменьшается на одном из отрезков')

    old_tf = np.loadtxt(r'entry_data\time.tf', skiprows=3)

    print(f'entry_t before = {entry_t}')
    # for i in range(len(entry_t)):
    #     local_min = np.ones(len(time_cell))
    #     for j in range(len(time_cell)):
    #         # print(f'{time_cell[j]} {entry_t[i]} {time_cell[j + 1]}')
    #
    #         local_min[j] = abs(time_cell[j] - entry_t[i])
    #     print(local_min)
    #     print('index = ', np.argmin(local_min))
    #     print((np.min(local_min)))

    print(f'entry_t = {entry_t}')
    print(f'entry_f = {entry_f}')

    time_count = []
    func_out = []
    for i in range(len(entry_t) - 1):
        k, b = Func().linear_dif(entry_f[i], entry_t[i], entry_f[i + 1], entry_t[i + 1])
        # print(f'k = {k} , b = {b}')
        # print(np.extract((time_cell == entry_t[i]),time_cell))
        left_side = np.where(time_cell == entry_t[i])[0]
        right_side = np.where(time_cell == entry_t[i + 1])[0]
        # print(type(left_side), time_cell[left_side])
        # print(type(right_side), time_cell[right_side][0], time_cell[100])
        print(f'{time_cell[left_side]} - {time_cell[right_side]}')
        if i != len(entry_t) - 2:

            for j in time_cell[left_side[0]:right_side[0]]:
                if j == time_cell[right_side[0]]:
                    print(j)
                    print(f'curent f len = {len(func_out)}')
                    print('')
                func_out.append(solve(j, k, b))
                time_count.append(j)
        else:
            for j in time_cell[left_side[0]:right_side[0] + 1]:
                func_out.append(solve(j, k, b))
                time_count.append(j)

    func_out = np.array(func_out)
    time_count = np.array(time_count)

    print(func_out.shape)
    print('заданныйэ = ', time_cell.shape, time_cell[-1])
    print('по факту = ', time_count.shape, time_count[-1])
    print(old_tf.shape)

    np.savetxt('1.txt', (np.c_[time_count]))
    np.savetxt('2.txt', (np.c_[time_cell]))
    plt.plot(time_count, func_out * np.max(old_tf[:, 1]))
    plt.plot(time_count, old_tf[:, 1])

    plt.show()
