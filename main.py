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
            cur_dir.append(line.strip())
    return cur_dir


def open_button():
    filename = fd.askdirectory(title='Укажите путь к проекту REMP')
    spectr = fd.askopenfilename(title='Выберите файл spectr', initialdir=rf'{filename}\pechs\spectrs',
                                filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
    handle = open(r"config.txt", "w", encoding='utf-8')
    handle.write(f'{filename}\n{spectr}')
    handle.close()

    with open(r"config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line.strip())
    if len(cur_dir) < 1:
        mb.showerror('Error', 'Путь не выбран')
    else:
        mb.showinfo('Info', 'Путь сохранён.')
    print(cur_dir)
    main()


def check_folder():
    prj_name = []
    for f in os.listdir(config_read()[0]):
        if f.endswith(".PRJ") or f.endswith(".prj"):
            prj_name.append(f)

    with open(os.path.join(config_read()[0], rf'{prj_name[0]}'), 'r') as file:
        lines = file.readlines()

    out = {}
    for i in range(len(lines)):
        if '<Grd name>' in lines[i]:
            out.setdefault('GRD', lines[i + 1].strip())
        if '<Tok name>' in lines[i]:
            out.setdefault('TOK', lines[i + 1].strip())
        if '<Layers name>' in lines[i]:
            out.setdefault('LAY', lines[i + 1].strip())
        if '<Particles-Layers name>' in lines[i]:
            out.setdefault('PL', lines[i + 1].strip())

    return out


class FrameGen(tk.Frame):
    def __init__(self, parent, name='Title', energy_type='Название типа энергии'):
        tk.Frame.__init__(self, parent)
        self.parent = root
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
        self.dir_name = config_read()[0].split('/')[-1]

    def __konstr(self):
        self.parent.title("Sources")
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Путь к PECHS", command=lambda: (tk.Frame.destroy(self), open_button()))
        filemenu.add_command(label="Reset", command=self.reset)
        filemenu.add_command(label="Exit", command=self.onExit)

        menubar.add_cascade(label="Файл", menu=filemenu)

    def notebooks(self):
        nb.add(self, text=f"{self.name}")
        # rows = 0
        # while rows < 50:
        #     self.rowconfigure(rows, weight=1,minsize=3)
        #     self.columnconfigure(rows, weight=1,minsize=3)
        #     rows += 1
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

        if 'Sigma' in self.name or 'Current' in self.name or 'Flu' in self.name:
            self.entry_f_val.set(1.)
            label_f = tk.Label(self, text='F')
            label_f.grid(row=2, column=30, padx=3, sticky='E')
            entry_f = tk.Entry(self, width=3, textvariable=self.entry_f_val)
            entry_f.grid(row=2, column=31, padx=3)

        if 'Initial_field' in self.name or 'External_field' in self.name:
            tk.Label(self, text='Ex').grid(row=2, column=30, sticky='E', padx=3)
            tk.Label(self, text='Ey').grid(row=3, column=30, sticky='E', padx=3)
            tk.Label(self, text='Ez').grid(row=4, column=30, sticky='E', padx=3)
            tk.Label(self, text='hx').grid(row=5, column=30, sticky='E', padx=3)
            tk.Label(self, text='hy').grid(row=6, column=30, sticky='E', padx=3)
            tk.Label(self, text='hz').grid(row=7, column=30, sticky='E', padx=3)

            self.some_x_val = [tk.StringVar() for _ in range(6)]
            for i in self.some_x_val:
                i.set('0')
            for i in range(6):
                some_x = tk.Entry(self, textvariable=self.some_x_val[i], width=4)
                some_x.grid(row=2 + i, column=31)

        if 'External_field' in self.name:
            for i in range(6):
                tk.Button(self, text='Browse tf', command=lambda: print(123),
                          width=10, ).grid(row=2 + i, column=32, padx=5)

    def gursa_nb(self):
        nb.add(self, text=f"{self.name}")
        add_button_gursa = tk.Button(self, text='add',
                                     command=lambda: Gursa().child_window()).grid(row=1, column=1)

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
        with open(rf'time functions/{self.dir_name}/user configuration/{path}.txt', 'r', encoding='utf-8') as file:
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
        with open(rf'functions/{self.dir_name}/user configuration/{self.name}.txt', 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            mb.showinfo('Save', f'Сохранено в time functions/{self.dir_name}/user configuration/{self.name}.txt')
            # self.labes_load_path = tk.Label(self, text=f'time functions/user configuration/{self.name}.txt')
            # self.labes_load_path.grid(row=3, column=3, columnspan=5)

    def time_save_def(self):
        with open(rf'time functions/{self.dir_name}/user configuration/default.txt', 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            mb.showinfo('Save default',
                        f'Сохранено стандартной в time functions/{self.dir_name}/user configuration/default.txt')
            # self.labes_load_path = tk.Label(self, text=f'time functions/user configuration/default.txt')
            # self.labes_load_path.grid(row=4, column=3, columnspan=5)

    def interpolate_user_time(self):
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

            return func_out, time_count

    def calculate(self):
        if ('Current' or 'Sigma' or 'Flu_e') in self.name:
            self.calculate_lay_pl()

    def calculate_lay_pl(self):

        func_out, time_count = self.interpolate_user_time()
        func_out = np.array(func_out)
        time_count = np.array(time_count)
        output_matrix = np.column_stack((time_count, func_out))

        # integrate
        if ('Current' or 'Sigma' or 'Flu_e') in self.name:
            if os.path.exists(config_read()[1]):
                spectr = np.loadtxt(config_read()[1], skiprows=3)
            else:
                mb.showerror('Spektr error', 'Spectr не существует')
                self.reset()

            E_cp = np.sum(spectr[:, 0] * spectr[:, 1]) / np.sum(spectr[:, 1])

            F = float(self.entry_f_val.get())
            intergal_tf = integrate.simps(y=output_matrix[:, 1], x=output_matrix[:, 0], dx=output_matrix[:, 0])

            koef = F / (0.23 * E_cp * intergal_tf * 1e3 * 1.6e-19)
            np.savetxt(f'time functions/{self.dir_name}/time_{self.name}.tf', output_matrix, fmt='%-8.4g',
                       header=f'1 pechs\n{time_count[0]} {time_count[-1]} {koef}\n{len(time_count)}', delimiter='\t',
                       comments='')
        else:
            np.savetxt(f'time functions/{self.dir_name}/time_{self.name}.tf', output_matrix, fmt='%-8.4g',
                       header=f'1 pechs\n{time_count[0]} {time_count[-1]} {1.0}\n{len(time_count)}', delimiter='\t',
                       comments='')
        # print(func_out.shape)
        # print('заданныйэ = ', time_cell.shape, time_cell[-1])
        # print('по факту = ', time_count.shape, time_count[-1])

        figure = plt.Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot(time_count, func_out, label='Пользовательская функция')

        if os.path.exists(os.path.join(self.path, 'time.tf')):
            old_tf_path = os.path.join(self.path, 'time.tf')
            old_tf = np.loadtxt(old_tf_path, skiprows=3)
            ax.plot(time_count, old_tf[:, 1] / np.max(old_tf[:, 1]), label='Стандартная функция')
        else:
            mb.showinfo('Time.tf', 'В проекте не найден time.tf, стандартная функция не отображена.')
        ax.set_xlabel('Time , s', fontsize=14)
        ax.set_ylabel('Function', fontsize=14)
        chart_type = FigureCanvasTkAgg(figure, self)

        chart_type.get_tk_widget().grid(row=4, column=8, rowspan=100, columnspan=50, padx=10)
        ax.set_title(f'{self.name}')
        ax.legend()

    def reset(self):

        nb.destroy()
        check_folder().clear()
        main()

    def onExit(self):
        self.quit()

    def time_grid(self):
        a = DataParcer(os.path.join(f'{self.path}', check_folder().get('GRD'))).grid_parcer()
        return f'[{a[0]} : {a[-1]}]'

    def child_parcecer_grid(self):
        return DataParcer(os.path.join(f'{self.path}', check_folder().get('GRD'))).grid_parcer()

    def value_check(self, func, time):
        for item in func:
            if not (0 <= item <= 1):
                mb.showerror('Value error', f'Значение функции {item} выходит за пределы')
        for item in time:
            if not (self.child_parcecer_grid()[0] <= item <= self.child_parcecer_grid()[-1]):
                mb.showerror('Value error', f'Значение временной функции {item} выходит за пределы')


class Gursa(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self, root)
        self.spectr_type = tk.IntVar()
        self.spectr_path = ''

    def child_window(self):
        self.title('PE source')
        self.geometry('800x600')

        rows = 0
        while rows < 30:
            self.rowconfigure(rows, weight=0, minsize=3)
            self.columnconfigure(rows, weight=0, minsize=3)
            rows += 1
        print(self.grid_size())

        x_y_z = ['X', 'Y', 'Z']
        label_names = ['Координаты источника (км)', 'Координаты объекта (км)', 'Число ячеек сетки']
        entry_koord_ist_val = [tk.StringVar() for _ in range(3)]
        entry_koord_obj_val = [tk.StringVar() for _ in range(3)]
        entry_koord_ist_val[0].set('0')
        entry_koord_ist_val[1].set('0')
        entry_koord_ist_val[2].set('40')
        entry_koord_obj_val[0].set('0')
        entry_koord_obj_val[1].set('0')
        entry_koord_obj_val[2].set('40')
        entry_grid_value = tk.StringVar()
        entry_grid_value.set('1000')
        tk.Entry(self, textvariable=entry_grid_value, width=9).grid(row=3, column=1)

        for i in range(3):
            entry_koord_ist = tk.Entry(self, textvariable=entry_koord_ist_val[i], width=9)
            entry_koord_ist.grid(row=1, column=1 + i, padx=1, pady=2)
            tk.Label(self, text=x_y_z[i]).grid(row=0, column=1 + i)
            tk.Label(self, text=label_names[i]).grid(row=1 + i, column=0, sticky='W')
        for i in range(3):
            entry_koord_ist = tk.Entry(self, textvariable=entry_koord_obj_val[i], width=9)
            entry_koord_ist.grid(row=2, column=1 + i, padx=1, pady=2)

        self.button_browse_spectr = tk.Button(self, text='Browse',
                                              command=self.take_spectr, state='normal')
        self.button_browse_spectr.grid(row=1, column=5, padx=5)
        self.button_rasch = tk.Button(self, text='Calc',
                                      command=lambda: print('calculated!'), state='disabled')
        self.button_rasch.grid(row=5, column=0)

        self.spectr_type.set(0)
        radio_cont = tk.Radiobutton(self, text='CONTINUOUS', variable=self.spectr_type, value=0)
        radio_cont.grid(row=1, column=6, sticky="W")
        radio_dis = tk.Radiobutton(self, text='DISCRETE', variable=self.spectr_type, value=1)
        radio_dis.grid(row=2, column=6, sticky="W")

        self.grab_set()
        self.focus_set()

    def take_spectr(self):
        path = fd.askopenfilename(title='Выберите файл spectr',
                                  filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
        with open(path, 'r') as file_handler:
            i = 0
            s = []

            if self.spectr_type.get() == 0:
                for line in file_handler:
                    i += 1
                    if 'SP_TYPE=DISCRETE' in line:
                        mb.showerror('Spectr error', 'Выбран спектр DISCRETE')
                        break
                    if i < 3: continue
                    if len(line.split()) < 2:
                        print(type(s))
                        line = line + '0'
                        s.append(line.split())
                    else:
                        s.append(line.split())

                out = np.array(s, dtype=float)
                for i in range(len(out) - 1):
                    out[i, 0] = (out[i, 0] + out[i + 1, 0]) / 2
                    out[i, 1] = out[i + 1, 1]
                out = np.delete(out, np.s_[-1:], 0)
            elif self.spectr_type.get() == 1:
                for line in file_handler:
                    if 'SP_TYPE=CONTINUOUS' in line:
                        mb.showerror('Spectr error', 'Выбран спектр CONTINUOUS')
                        break
                out = np.loadtxt(path, skiprows=2)
        return print(out)



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
        out_tok = np.zeros(3, dtype=int)
        for i in range(len(lines_tok)):
            if '<Начальное поле (0-нет,1-да)>' in lines_tok[i]:
                out_tok[0] = int(lines_tok[i + 1])
            if '<Внешнее поле (0-нет,1-да)>' in lines_tok[i]:
                out_tok[1] = int(lines_tok[i + 1])
            if '<Тип задачи (0-Коши 1-Гурса>' in lines_tok[i]:
                out_tok[2] = int(lines_tok[i + 1])
            # добавить тение строки гурса
        # print('.TOK  ', out_tok)
        return out_tok

    def pl_decoder(self):
        #### .PL DECODER
        with open(rf'{self.path}', 'r') as file:
            lines_pl = file.readlines()
        for line in range(len(lines_pl)):
            if '<Количество слоев>' in lines_pl[line]:
                pl_numeric = int(lines_pl[line + 1])
                out_pl = np.zeros((pl_numeric, pl_numeric), dtype=int)

            if '<Частица номер>' in lines_pl[line]:
                for i in range(pl_numeric):
                    for j in range(len(lines_pl[line + 2 + i].split())):
                        out_pl[i, j] = int(lines_pl[line + 2 + i].split()[j])

        # print('.PL\n', out_pl)
        return out_pl

    def grid_parcer(self):
        #### .PL DECODER
        with open(rf'{self.path}', 'r') as file:
            lines = file.readlines()
        out = np.array(lines[15].split(), dtype=float)
        return out


def checker():
    if os.path.exists(r"config.txt"):
        print('config exist')
    else:
        open_button()
    cur_dir = config_read()

    if len(cur_dir) < 2:
        print(f'len cur_dir < 2')
        mb.showerror('Path error', 'Укажите все необходимые директории')
        open_button()
        cur_dir = config_read()

    if not os.path.exists(rf"{cur_dir[0]}"):
        mb.showerror('Dir error', 'Директория не существует. Укажите путь к PECHS.')
        open_button()
        print('dir not exist ', f' {cur_dir[0]}')
        cur_dir = config_read()

    if not os.path.exists(r'time functions'):
        os.mkdir('time functions')
    if not os.path.exists(f'time functions/{FrameGen(root).dir_name}'):
        os.mkdir(f'time functions/{FrameGen(root).dir_name}')
    if not os.path.exists(f'time functions/{FrameGen(root).dir_name}/user configuration'):
        os.mkdir(os.path.join(f'time functions/{FrameGen(root).dir_name}/user configuration'))

    if len(DataParcer(os.path.normpath(os.path.join(cur_dir[0], check_folder().get('TOK')))).tok_decoder()) > 0:
        if not os.path.exists(f'time functions/{FrameGen(root).dir_name}/TOK'):
            os.mkdir(os.path.join(f'time functions/{FrameGen(root).dir_name}/TOK'))

    try:
        lay_dir = os.path.join(cur_dir[0], check_folder().get('LAY'))
        DataParcer(lay_dir).lay_decoder()
    except FileNotFoundError:
        mb.showerror('Path error', 'Директория указана неверно')
        cur_dir.clear()
        open_button()
        cur_dir = config_read()
    # check_folder()

    return cur_dir


def main():
    global nb

    cur_dir = checker()
    file_dict = check_folder()

    lay_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('LAY')))
    pl_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('PL')))
    tok_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('TOK')))
    grid_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('GRD')))

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
        mb.showinfo('ERROR', 'Частицы в нулевом слое!')

    if TOK[0] == 1:
        energy_type = 'Начальное поле'
        FrameGen(root, 'Initial_field', f'{energy_type}').notebooks()
    if TOK[1] == 1:
        energy_type = 'Внешнее поле'
        FrameGen(root, 'External_field', f'{energy_type}').notebooks()
    if TOK[2] == 1:
        energy_type = 'Gursa'
        FrameGen(root, 'Gursa', f'{energy_type}').gursa_nb()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1200x600')
    rows = 0
    while rows < 50:
        root.rowconfigure(rows, weight=1)
        root.columnconfigure(rows, weight=1)
        rows += 1
    print()
    main()

    root.mainloop()
