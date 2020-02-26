from tkinter import *
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
import numpy.random


class Calculations:
    def __init__(self):
        self.out = np.empty(1)
        self.b = 0
        self.k = 0

    def grid_parcer(self):
        #### .PL DECODER
        with open(r'C:\Users\Zalozhnyy_N\Dropbox\work_cloud\source_cont\entry_data\KUVSH.GRD', 'r') as file:
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
    time_cell = Calculations().grid_parcer()
    entry_f = np.array((1, 0.5, 0.3))
    entry_t = np.array((1e-10, 2e-9, 1e-7))
    # тесты интерполяции путём рандомизации времени
    # n = 10
    # entry_f = numpy.random.random_sample(n)
    # entry_t = np.sort(numpy.random.random_sample(n) * time_cell[-1])

    # print(entry_f)
    # print(entry_t)

    if entry_t[-1] != time_cell[-1]:
        entry_t = np.append(entry_t, time_cell[-1])
        entry_f = np.append(entry_f, 0)
    if entry_t[0] != 0 and entry_f[0] != 0:
        entry_t = np.insert(entry_t, 0, 0)
        entry_f = np.insert(entry_f, 0, 0)

    for i in range(len(entry_t) - 1):
        if entry_t[i] > entry_t[i + 1]:
            print(f'Value error время уменьшается на одном из отрезков {i}')

    old_tf = np.loadtxt(r'entry_data\time.tf', skiprows=3)

    print(f'entry_t = {entry_t}')
    print(f'entry_f = {entry_f}')

    time_count = []
    func_out = []
    for i in range(len(entry_t) - 1):
        k, b = Calculations().linear_dif(entry_f[i], entry_t[i], entry_f[i + 1], entry_t[i + 1])
        print(f'k = {k} , b = {b}')
        # print(np.extract((time_cell == entry_t[i]),time_cell))
        dt = time_cell[1] - time_cell[0]
        left_side = np.where(time_cell == entry_t[i])[0]
        right_side = np.where(time_cell == entry_t[i + 1])[0]

        if len(left_side) != 1:
            left_side = np.where(abs(time_cell - entry_t[i]) <= dt / 2)[0]
        if len(right_side) != 1:
            right_side = np.where(abs(time_cell - entry_t[i + 1]) <= dt / 2)[0]

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
    output_matrix = np.column_stack((time_count, func_out))
    print(func_out.shape)
    print('заданныйэ = ', time_cell.shape, time_cell[-1])
    print('по факту = ', time_count.shape, time_count[-1])
    print(old_tf.shape)

    np.savetxt('time functions/time_fixed.tf', output_matrix, fmt='%-8.4g',
               header=f'1 pechs\n{time_count[0]} {time_count[-1]} {1.0}\n{len(time_count)}\n', delimiter='\t',
               comments='')

    plt.plot(time_count, func_out * np.max(old_tf[:, 1]), label='Пользовательская функция')
    plt.plot(time_count, old_tf[:, 1], label='Стандартная функция')
    plt.legend()
    plt.show()
