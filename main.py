import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import integrate


def config_read():
    with open(r"config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line)
    return cur_dir


def open_button():
    filename = fd.askdirectory()
    handle = open(r"config.txt", "w", encoding='utf-8')
    handle.write(filename)
    handle.close()

    with open(r"config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line)
    if len(cur_dir) < 1:
        mb.showerror('Error', 'Путь не выбран')
    else:
        mb.showinfo('Info', 'Путь сохранён.')
    print(cur_dir[0])


class FrameGen(tk.Frame):
    def __init__(self, parent, name='Title', energy_type='Название типа энергии'):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.name = name
        self.energy_type = energy_type
        self.__konstr()

        self.cell_numeric = tk.StringVar()
        self.func_entry_vel = []
        self.time_entry_vel = []
        self.func_list = []
        self.time_list = []
        self.entry_f_val = tk.StringVar()

        self.path = os.path.normpath(config_read()[0])

    def __konstr(self):
        self.parent.title("PECH UTILITY")
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Путь к PECHS", command=open_button)
        filemenu.add_command(label="Reset", command=self.reset)
        filemenu.add_command(label="Exit", command=self.onExit)

        menubar.add_cascade(label="Файл", menu=filemenu)

    def notebooks(self):
        nb.add(self, text=f"{self.name}")
        label_name_energy = tk.Label(self, text=f'{self.energy_type}')
        label_name_energy.grid(row=5, column=0, columnspan=2)
        label_func = tk.Label(self, text='value', width=8)
        label_func.grid(row=6, column=0, padx=2, pady=2)
        label_time = tk.Label(self, text='time', width=8)
        label_time.grid(row=6, column=1, padx=2, pady=2)

        self.button_browse = tk.Button(self, width=10, text='Load', state='active',
                                       command=lambda: self.ent_load(self.name))
        self.button_browse.grid(row=1, column=2, padx=3)
        self.button_browse_def = tk.Button(self, width=10, text='Load default', state='active',
                                           command=lambda: self.ent_load('default'))
        self.button_browse_def.grid(row=1, column=3, padx=3)
        self.button_save = tk.Button(self, width=10, text='Save', state='disabled', command=self.time_save)
        self.button_save.grid(row=2, column=2, padx=3)
        self.button_save_def = tk.Button(self, width=10, text='Save as default', command=self.time_save_def,
                                         state='disabled')
        self.button_save_def.grid(row=2, column=3, padx=3)
        self.entry_generate_value = tk.Entry(self, width=5, textvariable=self.cell_numeric, state='normal')
        self.entry_generate_value.grid(row=5, column=3)
        self.button_generate = tk.Button(self, width=10, text='Generate', command=self.ent, state='active')
        self.button_generate.grid(row=5, column=2, padx=3)
        self.button_read_gen = tk.Button(self, width=10, text='Read', command=self.get, state='disabled')
        self.button_read_gen.grid(row=6, column=2)
        self.button_calculate = tk.Button(self, width=10, text='Calculate', command=self.calculate, state='disabled')
        self.button_calculate.grid(row=1, column=30, padx=3)
        self.add_button = tk.Button(self, width=6, text='Add one', state='disabled',
                                    command=lambda: self.add_entry())
        self.add_button.grid(row=1, column=0)

        if 'Sigma' or 'Current' or 'Flu_e' in self.name:
            self.entry_f_val.set(1.)
            self.label_f = tk.Label(self, text='F')
            self.label_f.grid(row=2, column=30, padx=3, sticky='E')
            self.entry_f = tk.Entry(self, width=3, textvariable=self.entry_f_val)
            self.entry_f.grid(row=2, column=31, padx=3)

    def ent(self):
        self.func_entry_vel.clear()
        self.time_entry_vel.clear()
        self.func_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric.get()))]
        self.time_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric.get()))]
        for i in range(int(self.cell_numeric.get())):
            entry_func = tk.Entry(self, width=9, textvariable=self.func_entry_vel[i])
            entry_func.grid(row=7 + i, column=0, pady=3)
            entry_time = tk.Entry(self, width=9, textvariable=self.time_entry_vel[i])
            entry_time.grid(row=7 + i, column=1, pady=3)

        self.entry_time = tk.Label(self, text=f'{self.time_grid()}')
        self.entry_time.grid(row=7 + int(self.cell_numeric.get()) + 1, column=1)
        self.entry_func = tk.Label(self, text='[0 : 1]')
        self.entry_func.grid(row=7 + int(self.cell_numeric.get()) + 1, column=0)

        self.button_browse.configure(state='disabled')
        self.button_browse_def.configure(state='disabled')
        self.button_read_gen.configure(state='normal')
        self.add_button.configure(state='normal')

    def ent_load(self, path):
        with open(rf'time functions/user configuration/{path}.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        print(lines)

        for word in lines[0].split():
            self.func_entry_vel.append(float(word))
        for word in lines[1].split():
            self.time_entry_vel.append(float(word))
        print('func = ', self.func_entry_vel)
        print('time = ', self.time_entry_vel)

        entr_utility_func = [tk.StringVar() for _ in range(len(self.func_entry_vel))]
        entr_utility_time = [tk.StringVar() for _ in range(len(self.func_entry_vel))]
        for i in range(len(self.func_entry_vel)):
            entry_func = tk.Entry(self, width=9, justify='center', textvariable=entr_utility_func[i])
            entry_func.grid(row=7 + i, column=0)
            entr_utility_func[i].set('{:.4g}'.format(self.func_entry_vel[i]))
            self.func_entry_vel[i] = entr_utility_func[i]
            # print(f'{i} ', type(entr_utility_func[i]), entr_utility_func[i])

        for i in range(len(self.time_entry_vel)):
            entry_time = tk.Entry(self, width=9, justify='center', textvariable=entr_utility_time[i])
            entry_time.grid(row=7 + i, column=1)
            entr_utility_time[i].set('{:.4g}'.format(self.time_entry_vel[i]))
            self.time_entry_vel[i] = entr_utility_time[i]

        self.entry_time = tk.Label(self, width=9, text=f'{self.time_grid()}')
        self.entry_time.grid(row=7 + len(self.time_entry_vel) + 1, column=1)
        self.entry_func = tk.Label(self, width=9, text='[0 : 1]')
        self.entry_func.grid(row=7 + len(self.func_entry_vel) + 1, column=0)

        if len(self.func_entry_vel) != len(self.time_entry_vel):
            mb.showerror('Load error', 'Размерности не совпадают')
            self.onExit()

        # self.labes_load_path = tk.Label(self, text=f'time functions/user configuration/{self.name}.txt')
        # self.labes_load_path.grid(row=1, column=4, columnspan=5)
        self.button_read_gen.configure(state='normal')
        self.button_generate.configure(state='disabled')
        self.button_browse_def.configure(state='disabled')
        self.button_browse.configure(state='disabled')
        self.add_button.configure(state='normal')

    def add_entry(self):

        self.func_entry_vel.append(tk.StringVar())
        self.time_entry_vel.append(tk.StringVar())

        entry_func = tk.Entry(self, width=9, justify='center', textvariable=self.func_entry_vel[-1])
        entry_func.grid(row=len(self.func_entry_vel) + 1 + 7, column=0)

        entry_time = tk.Entry(self, width=9, justify='center', textvariable=self.time_entry_vel[-1])
        entry_time.grid(row=len(self.func_entry_vel) + 1 + 7, column=1)

        self.entry_time.grid_configure(row=len(self.func_entry_vel) + 2 + 7)
        self.entry_func.grid_configure(row=len(self.func_entry_vel) + 2 + 7)

    # def del_entry(self):
    #
    #     self.func_entry_vel.pop()
    #     self.time_entry_vel.pop()

    def get(self):

        print('get', type(self.func_entry_vel[0]))
        self.func_list.clear()
        self.time_list.clear()

        for i in self.func_entry_vel:
            self.func_list.append(float(i.get()))
        for i in self.time_entry_vel:
            self.time_list.append(float(i.get()))

        self.value_check(func=self.func_list, time=self.time_list)
        self.button_generate.configure(state='disabled')
        self.entry_generate_value.configure(state='disabled')
        self.button_save.configure(state='active')
        self.button_save_def.configure(state='active')
        self.button_browse.configure(state='disabled')
        self.button_calculate.configure(state='normal')

        print('time = ', self.time_list)
        print('func = ', self.func_list)

    def time_save(self):
        with open(rf'time functions/user configuration/{self.name}.txt', 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            mb.showinfo('Save', f'Сохранено в time functions/user configuration/{self.name}.txt')
            # self.labes_load_path = tk.Label(self, text=f'time functions/user configuration/{self.name}.txt')
            # self.labes_load_path.grid(row=3, column=3, columnspan=5)

    def time_save_def(self):
        with open(rf'time functions/user configuration/default.txt', 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            mb.showinfo('Save default', f'Сохранено стандартной в time functions/user configuration/default.txt')
            # self.labes_load_path = tk.Label(self, text=f'time functions/user configuration/default.txt')
            # self.labes_load_path.grid(row=4, column=3, columnspan=5)

    def calculate(self):

        time_cell = self.child_parcecer_grid()
        print(f'функция {self.func_list}')
        print(f'время {self.time_list}')
        entry_f = np.array(self.func_list)
        entry_t = np.array(self.time_list)

        if entry_t[-1] != time_cell[-1]:
            entry_t = np.append(entry_t, time_cell[-1])
            entry_f = np.append(entry_f, 0)
        if entry_t[0] != 0 and entry_f[0] != 0:
            entry_t = np.insert(entry_t, 0, 0)
            entry_f = np.insert(entry_f, 0, 0)

        for i in range(len(entry_t) - 1):
            if entry_t[i] > entry_t[i + 1]:
                print(f'Value error время уменьшается на одном из отрезков {i}')
        old_tf_path = os.path.join(self.path, 'time.tf')
        # old_tf = np.loadtxt(r'entry_data\time.tf', skiprows=3)
        old_tf = np.loadtxt(old_tf_path, skiprows=3)
        time_count = []
        func_out = []
        for i in range(len(entry_t) - 1):
            k, b = Calculations().linear_dif(entry_f[i], entry_t[i], entry_f[i + 1], entry_t[i + 1])
            # print(f'k = {k} , b = {b}')
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
                    func_out.append(Calculations().solve(j, k, b))
                    time_count.append(j)
            else:
                for j in time_cell[left_side[0]:right_side[0] + 1]:
                    func_out.append(Calculations().solve(j, k, b))
                    time_count.append(j)

        func_out = np.array(func_out)
        time_count = np.array(time_count)
        output_matrix = np.column_stack((time_count, func_out))

        # integrate
        if ('Current' or 'Sigma' or 'Flu_e') in self.name:
            spectr = np.loadtxt(os.path.join(config_read()[0], 'pechs\spectrs\G'), skiprows=3, dtype=float)
            spectr_avg = np.average(spectr[:, 0])
            F = float(self.entry_f_val.get())
            intergal_tf = integrate.simps(y=output_matrix[:, 1], x=output_matrix[:, 0], dx=output_matrix[:, 0])

            koef = F / (0.23 * spectr_avg * intergal_tf * 1e3 * 1.6e-19)
            np.savetxt(f'time functions/time_{self.name}.tf', output_matrix, fmt='%-8.4g',
                       header=f'1 pechs\n{time_count[0]} {time_count[-1]} {koef}\n{len(time_count)}', delimiter='\t',
                       comments='')
        else:
            np.savetxt(f'time functions/time_{self.name}.tf', output_matrix, fmt='%-8.4g',
                       header=f'1 pechs\n{time_count[0]} {time_count[-1]} {1.0}\n{len(time_count)}', delimiter='\t',
                       comments='')
        print(func_out.shape)
        print('заданныйэ = ', time_cell.shape, time_cell[-1])
        print('по факту = ', time_count.shape, time_count[-1])
        print(old_tf.shape)

        figure = plt.Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot(time_count, func_out, label='Пользовательская функция')
        ax.plot(time_count, old_tf[:, 1] / np.max(old_tf[:, 1]), label='Стандартная функция')
        ax.set_xlabel('Time , s', fontsize=14)
        ax.set_ylabel('Function', fontsize=14)
        chart_type = FigureCanvasTkAgg(figure, self)

        chart_type.get_tk_widget().grid(row=4, column=8, rowspan=100, columnspan=50, padx=10)
        ax.set_title(f'{self.name}')
        ax.legend()

    def reset(self):
        nb.destroy()
        main()

    def onExit(self):
        self.quit()

    def time_grid(self):
        a = DataParcer(os.path.join(f'{self.path}', 'KUVSH.GRD')).grid_parcer()
        return f'[{a[0]} : {a[-1]}]'

    def child_parcecer_grid(self):
        return DataParcer(os.path.join(f'{self.path}', 'KUVSH.GRD')).grid_parcer()

    def value_check(self, func, time):
        for item in func:
            if not (0 <= item <= 1):
                mb.showerror('Value error', f'Значение функции {item} выходит за пределы')
        for item in time:
            if not (self.child_parcecer_grid()[0] <= item <= self.child_parcecer_grid()[-1]):
                mb.showerror('Value error', f'Значение временной функции {item} выходит за пределы')


class Calculations:

    def linear_dif(self, y1, x1, y2, x2):
        self.k = (y2 - y1) / (x2 - x1)
        self.b = y1 - (y2 - y1) * x1 / (x2 - x1)
        return self.k, self.b

    def solve(self, x, k, b):
        self.f = k * x + b
        return self.f


class DataParcer:
    def __init__(self, path):
        self.path = path

    def lay_decoder(self):
        #### .LAY DECODER
        with open(rf'{self.path}', 'r') as file:
            lines = file.readlines()
        lay_numeric = int(lines[2])
        out_lay = np.zeros((lay_numeric, 3), dtype=int)
        j = 0
        for i in range(len(lines)):
            if '<Номер, название слоя>' in lines[i]:  # 0 - номер слоя  1 - стороннй ток  2 - стро. ист.
                out_lay[j, 0] = int(lines[i + 1].split()[0])
                out_lay[j, 1] = int(lines[i + 3].split()[2])
                out_lay[j, 2] = int(lines[i + 3].split()[3])
                j += 1
        # print('.LAY  ', out_lay)
        return out_lay

    def tok_decoder(self):
        #### .TOK DECODER
        with open(rf'{self.path}', 'r') as file:
            lines_tok = file.readlines()
        out_tok = np.zeros(2, dtype=int)
        for i in range(len(lines_tok)):
            if '<Начальное поле (0-нет,1-да)>' in lines_tok[i]:
                out_tok[0] = int(lines_tok[i + 1])
            if '<Внешнее поле (0-нет,1-да)>' in lines_tok[i]:
                out_tok[1] = int(lines_tok[i + 1])
        # print('.TOK  ', out_tok)
        return out_tok

    def pl_decoder(self):
        #### .PL DECODER
        with open(rf'{self.path}', 'r') as file:
            lines_pl = file.readlines()
        for i in range(len(lines_pl)):
            if '<Количество слоев>' in lines_pl[i]:
                pl_numeric = int(lines_pl[i + 1])
                out_pl = np.zeros((pl_numeric, pl_numeric), dtype=int)

            if '<Частица номер>' in lines_pl[i]:
                for k in range(pl_numeric):
                    out_pl[k, 0] = int(lines_pl[i + 2 + k].split()[0])
                    out_pl[k, 1] = int(lines_pl[i + 2 + k].split()[1])
                    out_pl[k, 2] = int(lines_pl[i + 2 + k].split()[2])
                    out_pl[k, 3] = int(lines_pl[i + 2 + k].split()[3])
                    out_pl[k, 4] = int(lines_pl[i + 2 + k].split()[4])
                    out_pl[k, 5] = int(lines_pl[i + 2 + k].split()[5])
        # print('.PL\n', out_pl)
        return out_pl

    def grid_parcer(self):
        #### .PL DECODER
        with open(rf'{self.path}', 'r') as file:
            lines = file.readlines()
        out = np.array(lines[15].split(), dtype=float)
        return out


def main():
    global nb

    if os.path.exists(r"config.txt"):
        print('config exist')
    else:
        open_button()
    cur_dir = config_read()

    if len(cur_dir) == 0:
        open_button()
        cur_dir = config_read()

    if not os.path.exists(rf"{cur_dir[0]}"):
        mb.showerror('Dir error', 'Директория не существует. Укажите путь к PECHS.')
        open_button()
        print('config exist ', f' {cur_dir[0]}')
        cur_dir = config_read()

    if not os.path.exists(r'time functions'):
        os.mkdir('time functions')
    if not os.path.exists('time functions/user configuration'):
        os.mkdir(os.path.join('time functions/user configuration'))

    try:
        lay_dir = os.path.join(cur_dir[0], 'KUVSH.LAY')
        DataParcer(lay_dir).lay_decoder()
    except FileNotFoundError:
        mb.showerror('Path error', 'Директория указана неверно')
        cur_dir.clear()
        open_button()
        cur_dir = config_read()

    lay_dir = os.path.join(cur_dir[0], 'KUVSH.LAY')
    pl_dir = os.path.join(cur_dir[0], 'KUVSH.PL')
    tok_dir = os.path.join(cur_dir[0], 'KUVSH.TOK')
    grid_dir = os.path.join(cur_dir[0], 'KUVSH.GRD')

    # print(DataParcer(grid_dir).grid_parcer().shape)
    # print(FrameGen(root).time_grid())
    nb = ttk.Notebook(root)
    nb.grid(row=0, column=0, rowspan=100, columnspan=100, sticky='NWSE')
    LAY = DataParcer(lay_dir).lay_decoder()
    PL = DataParcer(pl_dir).pl_decoder()
    TOK = DataParcer(tok_dir).tok_decoder()
    for i in range(LAY.shape[0]):
        if LAY[i, 1] == 1:
            energy_type = 'Current'
            FrameGen(root, f'{energy_type}, layer {i}', 'Current').notebooks()
        if LAY[i, 2] == 1:
            energy_type = 'Sigma'
            FrameGen(root, f'{energy_type}, layer {i}', 'Sigma').notebooks()

    for i in range(PL.shape[0]):
        for j in range(1, PL.shape[1]):
            if PL[i, j] == 1:
                FrameGen(root, f'Flu_e{j}{i}', f'Источник электронов из {j}го в {i}й').notebooks()
    if PL[:, 0].any() == 1:
        mb.showerror('ERROR', 'Частицы в нулевом слое!')

    if TOK[0] == 1:
        energy_type = 'Начальное поле'
        FrameGen(root, 'Int', f'{energy_type}').notebooks()
    if TOK[1] == 1:
        energy_type = 'Внешнее поле'
        FrameGen(root, 'Int', f'{energy_type}').notebooks()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1200x600')
    rows = 0
    while rows < 100:
        root.rowconfigure(rows, weight=10)
        root.columnconfigure(rows, weight=10)
        rows += 1

    main()

    root.mainloop()
