import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os
import numpy as np
from numpy import exp, sin, cos, tan, log10
from numpy import log as ln

from utility import *
from Project_reader import DataParcer
from Save_for_remp import Save_remp
from Exceptions import *


class FrameGen(tk.Frame):
    def __init__(self, parent, path, name='Title', energy_type='Название типа энергии'):
        tk.Frame.__init__(self)
        self.parent = parent
        self.name = name
        self.energy_type = energy_type
        self.remp_source = None

        self.path = path
        self.pr_dir = path

        self.entry_func = []
        self.entry_time = []
        self.cell_numeric = tk.StringVar()
        self.func_entry_vel = []
        self.time_entry_vel = []
        self.func_list = []
        self.time_list = []

        self.entry_f_val = tk.StringVar()
        self.entry_time_fix_val = tk.StringVar()
        self.spectr = []

        # self.path = os.path.normpath(config_read()[0])
        # self.path = fd.askdirectory(title='Укажите путь к проекту REMP', initialdir=os.getcwd())

        # self.dir_name = config_read()[0].split('/')[-1]

        self.gursa_count = []

        self.existe_gursa_label = []
        self.gursa_dict = {}
        self.gursa_label_dict = {}

        self.x = []

        self.external_tf_num = []

        self.gursa_out_dict = {}

        self.spectr_dir = ''
        self.spectr_type = ''

        self.graph_frame_exist = 0

        print(repr(self))

    def __repr__(self):
        return f'{self.name}'

    def _notebooks(self):
        rows = 0
        while rows < 100:
            self.rowconfigure(rows, weight=1, minsize=10)
            self.columnconfigure(rows, weight=1, minsize=10)
            rows += 1

        self.button_change_method = tk.Button(self)
        self.button_change_method.grid(row=3, column=0, padx=5, pady=5, sticky='WN', columnspan=2)
        # test_button = tk.Button(self,text='test',command=self.integral)
        # test_button.grid(row=2,column=3)

        self.load_save_frame()
        self.entry_func_frame()

        self.button_calculate = tk.Button(self, width=15, text='Расчёт', state='disabled')
        self.button_calculate.grid(row=1, column=3, padx=3)

        self.a, self.A = self.time_grid()

        self.remp_source = self.remp_source_finder()
        self.specter_config = DataParcer(self.path).temp_spectres_reader()
        self.constants_frame()
        self.loat_from_remp()

    def remp_source_finder(self):
        if self.path is None:
            return

        remp_path = os.path.join(self.path, 'remp_sources')
        if not os.path.exists(remp_path):
            return

        out = DataParcer(remp_path).remp_source_decoder()

        return out

    def load_save_frame(self):
        self.load_safe_fr = tk.LabelFrame(self, text='Сохранение/Загрузка .dtf')
        self.load_safe_fr.grid(row=1, column=0, rowspan=2, columnspan=2, sticky='WN', padx=5)

        self.button_browse = tk.Button(self.load_safe_fr, width=12, text='Загрузить', state='active',
                                       command=lambda: self.ent_load(
                                           fd.askopenfilename(filetypes=[('Dtf files', '.dtf')],
                                                              initialdir=rf'{self.path}/time functions/user configuration')))
        self.button_browse.grid(row=0, column=0, padx=3, pady=3)
        self.button_browse_def = tk.Button(self.load_safe_fr, width=12, text='Загр. стандарт', state='active',
                                           command=lambda: self.ent_load(
                                               rf'{self.path}/time functions/user configuration/default.dtf'))
        self.button_browse_def.grid(row=0, column=1, padx=3, pady=3)
        self.button_save = tk.Button(self.load_safe_fr, width=12, text='Сохранить как', state='disabled',
                                     command=self.time_save)
        self.button_save.grid(row=1, column=0, padx=3, pady=3)
        self.button_save_def = tk.Button(self.load_safe_fr, width=12, text='Сохр. как станд.',
                                         command=self.time_save_def,
                                         state='disabled')
        self.button_save_def.grid(row=1, column=1, padx=3, pady=3)

    def entry_func_frame(self):

        if type(self.func_entry_vel) is not list:
            tmp_f = self.func_entry_vel.get().split()
            self.func_entry_vel = []
            for i, val in enumerate(tmp_f):
                self.func_entry_vel.append(tk.StringVar())
                self.func_entry_vel[i].set(val)

            tmp_t = self.time_entry_vel.get().split()
            self.time_entry_vel = []
            for i, val in enumerate(tmp_t):
                self.time_entry_vel.append(tk.StringVar())
                self.time_entry_vel[i].set(val)

        self.entry_func_fr = tk.LabelFrame(self, text='Блок ввода данных временной функции', width=30)
        self.entry_func_fr.grid(row=4, column=0, columnspan=3, padx=5)

        self.button_read_gen = tk.Button(self.entry_func_fr, width=12, text='Прочитать', state='disabled',
                                         command=self.local_get)
        self.button_read_gen.grid(row=0, column=2, padx=3, pady=3)
        self.button_generate = tk.Button(self.entry_func_fr, width=12, text='Сгенерировать', command=self.ent,
                                         state='active')
        self.button_generate.grid(row=1, column=2, padx=3, pady=3)

        label_name_energy = tk.Label(self.entry_func_fr, text=f'{self.energy_type}')
        label_name_energy.grid(row=2, column=0, columnspan=2)
        label_func = tk.Label(self.entry_func_fr, text='Значение функции', width=15)
        label_func.grid(row=3, column=1, padx=2, pady=2)
        label_time = tk.Label(self.entry_func_fr, text='Время', width=15)
        label_time.grid(row=3, column=0, padx=2, pady=2)

        self.add_button = tk.Button(self.entry_func_fr, width=6, text='Доб. яч.', state='disabled',
                                    command=lambda: self.add_entry())
        self.del_button = tk.Button(self.entry_func_fr, width=6, text='Уд. яч.', state='disabled',
                                    command=lambda: self.delete_entry())
        self.add_button.grid(row=0, column=0, sticky='e', padx=3)
        self.del_button.grid(row=0, column=1, sticky='w', padx=3)

        if len(self.time_entry_vel) != 0 or len(self.func_entry_vel) != 0:
            self.ent_load_back()

        self.button_change_method.configure(text='Строчный ввод', command=self.rows_metod, width=15)

    def constants_frame(self):
        self.constants_fr = tk.LabelFrame(self, text='Константы', width=20)
        self.constants_fr.grid(row=1, column=2, sticky='NWSE', padx=5)

        self.entry_f_val.set(1.)
        label_f = tk.Label(self.constants_fr, text='F , кал/см\u00b2')
        label_f.grid(row=0, column=0, padx=3, sticky='E')
        entry_f = tk.Entry(self.constants_fr, width=8, textvariable=self.entry_f_val)
        entry_f.grid(row=0, column=2, padx=3)

    def rows_metod(self):
        if type(self.func_entry_vel) is list:
            tmp_f = ''
            for val in self.func_entry_vel:
                tmp_f += val.get() + ' '
            self.func_entry_vel = tk.StringVar()
            self.func_entry_vel.set(tmp_f)

            tmp_t = ''
            for val in self.time_entry_vel:
                tmp_t += val.get() + ' '
            self.time_entry_vel = tk.StringVar()
            self.time_entry_vel.set(tmp_t)

        self.entry_func_fr.destroy()
        self.entry_func_fr = tk.LabelFrame(self, text='Блок ввода данных временной функции')
        self.entry_func_fr.grid(row=4, column=0, columnspan=3, padx=5, sticky='NWE')

        tk.Label(self.entry_func_fr, text='Время').grid(row=0, column=0, pady=3, padx=2)
        self.entry_time = tk.Entry(self.entry_func_fr, width=35, textvariable=self.time_entry_vel, justify='left')
        self.entry_time.grid(row=0, column=1, pady=3, padx=2, columnspan=7, sticky='WEN')

        tk.Label(self.entry_func_fr, text='Зн. функции').grid(row=1, column=0, pady=3, padx=2)
        self.entry_func = tk.Entry(self.entry_func_fr, width=35, textvariable=self.func_entry_vel, justify='left')
        self.entry_func.grid(row=1, column=1, pady=3, padx=2, columnspan=7, sticky='WEN')

        self.entryScroll = tk.Scrollbar(self.entry_func_fr, orient=tk.HORIZONTAL, command=self.__scrollHandler,
                                        bg='black',activebackground='green')
        self.entryScroll.grid(row=3, column=0, columnspan=8, sticky='WEN')

        self.entry_time["xscrollcommand"] = self.entryScroll.set
        self.entry_func["xscrollcommand"] = self.entryScroll.set

        self.button_read_gen = tk.Button(self.entry_func_fr, width=10, text='Прочитать', state='normal',
                                         command=self.local_get_row)
        self.button_read_gen.grid(row=7, column=1, padx=3, pady=3)

        tk.Label(self.entry_func_fr, text='Огр времени').grid(row=4, column=0)
        self.entry_time_label = tk.Label(self.entry_func_fr, text=f'{self.a}')
        self.entry_time_label.grid(row=4, column=1)
        tk.Label(self.entry_func_fr, text='Огр функции').grid(row=5, column=0)
        self.entry_func_label = tk.Label(self.entry_func_fr, text='[0 : 1]')
        self.entry_func_label.grid(row=5, column=1)

        self.obriv_tf_lavel = tk.Label(self.entry_func_fr, text='Обрыв tf')
        self.obriv_tf_lavel.grid(row=6, column=0)
        self.entry_time_fix_val.set(f'{self.A[-1]}')
        self.entry_time_fix = tk.Entry(self.entry_func_fr, textvariable=self.entry_time_fix_val, width=8)
        self.entry_time_fix.grid(row=6, column=1)

        self.button_save_def.configure(state='disabled')
        self.button_save.configure(state='disabled')
        self.button_change_method.configure(text='Дискретный метод', width=15,
                                            command=lambda: (self.entry_func_fr.destroy(), self.entry_func_frame()))

    def __scrollHandler(self, *L):
        op, howMany = L[0], L[1]
        if op == "scroll":
            units = L[2]
            self.entry_time.xview_scroll(howMany, units)
            self.entry_func.xview_scroll(howMany, units)
        elif op == "moveto":
            self.entry_time.xview_moveto(howMany)
            self.entry_func.xview_moveto(howMany)

    def ent(self):
        self.entry_func = []
        self.entry_time = []
        self.func_entry_vel.clear()
        self.time_entry_vel.clear()

        self.cell_numeric = simpledialog.askinteger('Введите число ячеек.', 'Число ячеек = ')

        self.func_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric))]
        self.time_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric))]
        for i in range(int(self.cell_numeric)):
            self.entry_time.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=4 + i, column=0, pady=3, padx=2)
            self.entry_func.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=4 + i, column=1, pady=3, padx=2)

        a, A = self.time_grid()

        self.entry_time_label = tk.Label(self.entry_func_fr, text=f'{a}')
        self.entry_time_label.grid(row=5 + int(self.cell_numeric) + 1, column=0)
        self.entry_func_label = tk.Label(self.entry_func_fr, text='[0 : 1]')
        self.entry_func_label.grid(row=5 + int(self.cell_numeric) + 1, column=1)

        self.obriv_tf_lavel = tk.Label(self.entry_func_fr, text='Обрыв tf')
        self.obriv_tf_lavel.grid(row=6 + len(self.func_entry_vel) + 1, column=0)
        self.entry_time_fix_val.set(f'{A[-1]}')
        self.entry_time_fix = tk.Entry(self.entry_func_fr, textvariable=self.entry_time_fix_val, width=6)
        self.entry_time_fix.grid(row=6 + len(self.func_entry_vel) + 1, column=1)

        self.button_browse.configure(state='disabled')
        self.button_browse_def.configure(state='disabled')
        self.button_read_gen.configure(state='normal')
        self.add_button.configure(state='normal')
        self.del_button.configure(state='normal')

    def loat_from_remp(self):

        if self.remp_source is not None:
            if self.name in self.remp_source.keys():
                l_dict = self.remp_source.get(self.name)
                time = l_dict.get('time')
                for i, val in enumerate(time):
                    self.time_entry_vel.append(tk.StringVar())
                    self.time_entry_vel[i].set(val)

                func = l_dict.get('value')
                for i, val in enumerate(func):
                    self.func_entry_vel.append(tk.StringVar())
                    self.func_entry_vel[i].set(val)

                self.ent_load_back()
                self.loat_from_remp_calc()
        else:
            return

    def loat_from_remp_calc(self):
        if self.name in self.specter_config.keys():
            self.get()
            self.stectr_choice(specter=self.specter_config.get(self.name)[0],
                               lag=self.specter_config.get(self.name)[1])

    def ent_load(self, path):
        if path == '':
            return
        try:
            with open(f'{path}', 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            if 'default.dtf' in path:
                mb.showerror('path error', 'default.dtf не обнаружен. Сначала сохраните значения как стандартные.')
                return
        lines = [line.strip() for line in lines]
        # print(lines)
        if type(self.entry_time) is list:
            self.entry_time.clear()
            self.entry_func.clear()
        else:
            self.entry_time = []
            self.entry_func = []

        self.func_entry_vel.clear()
        self.time_entry_vel.clear()

        for i, word in enumerate(lines[0].split()):
            self.func_entry_vel.append(tk.StringVar())
            self.func_entry_vel[i].set(word)
        for i, word in enumerate(lines[1].split()):
            self.time_entry_vel.append(tk.StringVar())
            self.time_entry_vel[i].set(word)

        self.entry_func_fr.destroy()
        self.entry_func_frame()

        # print('func = ', self.func_entry_vel)
        # print('time = ', self.time_entry_vel)

    def ent_load_back(self):
        if type(self.entry_time) is not list:
            self.entry_time = []
            self.entry_func = []

        # entr_utility_func = [tk.StringVar() for _ in range(len(self.func_entry_vel))]
        # entr_utility_time = [tk.StringVar() for _ in range(len(self.time_entry_vel))]
        #
        # if len(self.func_entry_vel) != 0:
        #     entr_utility_func = [entr_utility_func[i].set(val) for i, val in enumerate(self.func_entry_vel)]
        # if len(self.time_entry_vel) != 0:
        #     entr_utility_time = [entr_utility_time[i].set(val) for i, val in enumerate(self.time_entry_vel)]

        for i in range(len(self.func_entry_vel)):
            self.entry_time.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=4 + i, column=0, pady=3, padx=2)
            # entr_utility_time[i].set('{:.4g}'.format(float(self.time_entry_vel[i])))
            # self.time_entry_vel[i] = entr_utility_time[i].get()

            self.entry_func.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=4 + i, column=1, pady=3, padx=2)
            # entr_utility_func[i].set('{:.4g}'.format(float(self.func_entry_vel[i])))
            # self.func_entry_vel[i] = entr_utility_func[i].get()
            # print(f'{i} ', type(entr_utility_func[i]), entr_utility_func[i])

        a, A = self.time_grid()

        self.entry_time_label = tk.Label(self.entry_func_fr, width=9, text=f'{a}')
        self.entry_time_label.grid(row=5 + len(self.time_entry_vel) + 1, column=0)
        self.entry_func_label = tk.Label(self.entry_func_fr, width=9, text='[0 : 1]')
        self.entry_func_label.grid(row=5 + len(self.func_entry_vel) + 1, column=1)

        self.obriv_tf_lavel = tk.Label(self.entry_func_fr, text='Обрыв tf')
        self.obriv_tf_lavel.grid(row=6 + len(self.func_entry_vel) + 1, column=0)
        self.entry_time_fix_val.set(f'{A[-1]}')
        self.entry_time_fix = tk.Entry(self.entry_func_fr, textvariable=self.entry_time_fix_val, width=6)
        self.entry_time_fix.grid(row=6 + len(self.func_entry_vel) + 1, column=1)

        if len(self.func_entry_vel) != len(self.time_entry_vel):
            mb.showerror('Load error', 'Размерности не совпадают')
            self.onExit()

        self.button_read_gen.configure(state='normal')
        self.button_generate.configure(state='disabled')
        self.add_button.configure(state='normal')
        self.del_button.configure(state='normal')

    def add_entry(self):
        for i in self.entry_func:
            i.destroy()
        for i in self.entry_time:
            i.destroy()

        self.entry_time.clear()
        self.entry_func.clear()

        self.func_entry_vel.append(tk.StringVar())
        self.func_entry_vel[-1].set('')
        self.time_entry_vel.append(tk.StringVar())
        self.time_entry_vel[-1].set('')

        for i in range(len(self.time_entry_vel)):
            self.entry_func.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=4 + i, column=1, pady=3, padx=2)
            self.entry_time.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=4 + i, column=0, pady=3, padx=2)

        self.entry_time_label.grid_configure(row=len(self.func_entry_vel) + 2 + 4)
        self.entry_func_label.grid_configure(row=len(self.func_entry_vel) + 2 + 4)

        self.obriv_tf_lavel.grid_configure(row=len(self.func_entry_vel) + 2 + 5)
        self.entry_time_fix.grid_configure(row=len(self.func_entry_vel) + 2 + 5)

        self.button_calculate.configure(state='disabled')

    def delete_entry(self):
        for i in self.entry_func:
            i.destroy()
        for i in self.entry_time:
            i.destroy()

        self.entry_time.clear()
        self.entry_func.clear()

        self.func_entry_vel.pop(-1)
        self.time_entry_vel.pop(-1)

        for i in range(len(self.time_entry_vel)):
            self.entry_func.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=4 + i, column=1, pady=3, padx=2)
            self.entry_time.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=4 + i, column=0, pady=3, padx=2)

        self.entry_time_label.grid_configure(row=len(self.func_entry_vel) + 2 + 4)
        self.entry_func_label.grid_configure(row=len(self.func_entry_vel) + 2 + 4)

        self.obriv_tf_lavel.grid_configure(row=len(self.func_entry_vel) + 2 + 5)
        self.entry_time_fix.grid_configure(row=len(self.func_entry_vel) + 2 + 5)

        self.button_calculate.configure(state='disabled')

    def row_get(self):
        self.func_list.clear()
        self.time_list.clear()

        for i in self.time_entry_vel.get().split():
            try:
                self.time_list.append(float(i))
            except ValueError:
                print(f'{i} не может быть преобразовано в float')
                mb.showerror('Value error', f'{i} не может быть преобразовано в float')
                return 0

        func_string = self.func_entry_vel.get()
        if '(' in func_string:
            tmp = ''
            for i in range(len(self.time_list)):
                calc = func_string.replace('t', f'{self.time_list[i]}')
                self.func_list.append(eval(calc))
                tmp += '{:.5g} '.format(eval(calc))

            self.func_entry_vel.set(tmp)

        else:
            for i in self.func_entry_vel.get().split():
                try:
                    self.func_list.append(eval(i))
                except ValueError:
                    print(f'{i} не может быть преобразовано в float')
                    mb.showerror('Value error', f'{i} не может быть преобразовано в float')
                    return 0

        if len(self.func_list) != len(self.time_list):
            print('Размерности не совпадают!')
            mb.showerror('Index error', 'Размерности не совпадают!')
            return 0

        print('time = ', self.time_list)
        print('func = ', self.func_list)

        self.button_save.configure(state='disabled')
        self.button_save_def.configure(state='disabled')

    def get(self):

        # print('get', type(self.func_entry_vel[0]))
        self.func_list.clear()
        self.time_list.clear()

        for j in self.time_entry_vel:
            self.time_list.append(j.get())

        for x, j in enumerate(self.func_entry_vel):
            if 't' in j.get():  # если есть t в строке, то заменяем это t на значение entry time с тем же индексом
                string = j.get()
                fixed_string = string.replace('t', f'{self.time_list[x]}')
                self.func_list.append(fixed_string)
            else:
                self.func_list.append(j.get())

        exeption_list = ['exp', '(', ')', '*', '**', '/']

        for x, i in enumerate(self.func_list):
            if any([e in i for e in exeption_list]):
                self.func_list = self.eval_transformation(self.func_list, self.func_entry_vel)
                break
            else:
                try:
                    self.func_list[x] = float(self.func_entry_vel[x].get())
                except ValueError:
                    mb.showerror('Value error', f'{self.func_entry_vel[x].get()} не является числом')
                    return print(f'{self.func_entry_vel[x].get()} не является числом')

        for x, i in enumerate(self.time_list):
            if any([e in i for e in exeption_list]):
                self.time_list = self.eval_transformation(self.time_list, self.time_entry_vel)
                break
            else:
                try:
                    self.time_list[x] = float(self.time_entry_vel[x].get())
                except ValueError:
                    mb.showerror('Value error', f'{self.time_entry_vel[x].get()} не является числом')
                    return print(f'{self.time_entry_vel[x].get()} не является числом')
        print('time = ', self.time_list)
        print('func = ', self.func_list)

        self.value_check(func=self.func_list, time=self.time_list)

        self.button_save.configure(state='normal')
        self.button_save_def.configure(state='normal')

    def eval_transformation(self, arg, replace):
        for x, i in enumerate(replace):
            if 't' in i.get():
                string = i.get()
                fixed_string = string.replace('t', f'{self.time_list[x]}')
                arg[x] = eval(fixed_string)
                replace[x].set('{:.4g}'.format(eval(fixed_string)))
            else:
                arg[x] = eval(i.get())
                replace[x].set('{:.4g}'.format(eval(i.get())))
        return arg

    def time_save(self):

        save_dir = fd.asksaveasfilename(title='Назовите файл', filetypes=(("dtf files", "*.dtf"), ("All files", "*.*"))
                                        , defaultextension=("dtf files", "*.dtf"),
                                        initialdir=rf'{self.path}/time functions/user configuration')
        with open(save_dir, 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            save_dir_inf = save_dir.split('/')[-1]
            mb.showinfo('Save', f'Сохранено в time functions/user configuration/{save_dir_inf}')

    def time_save_def(self):
        with open(rf'{self.path}/time functions/user configuration/default.dtf', 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            mb.showinfo('Save default',
                        f'Сохранено стандартной в time functions/user configuration/default.dtf')

    def time_grid(self):
        a = DataParcer(os.path.join(f'{self.path}', check_folder(self.path).get('GRD'))).grid_parcer()
        return f'[{a[0]} : {a[-1]}]', a

    def spectr_choice_classifier(self, path):
        spectr_dir = os.path.normpath(path)

        with open(spectr_dir, 'r') as file:
            strings = []
            for string in range(5):
                strings.append(file.readline().strip())

        if any(['CONTINUOUS' in line for line in strings]):
            spectr_type = 'CONTINUOUS'
        elif any(['DISCRETE' in line for line in strings]):
            spectr_type = 'DISCRETE'
        else:
            print('Тип спектра не распознан')
            return
        return spectr_dir, spectr_type

    def spectr_choice_opener(self):

        try:
            if self.spectr_type == 'CONTINUOUS':
                with open(self.spectr_dir, 'r', encoding='utf-8') as file_handler:
                    i = 0
                    s = []
                    for line in file_handler:
                        i += 1
                        if i < 3: continue
                        if len(line.split()) < 2:
                            line = line + '0'
                            s.append(line.split())
                        else:
                            s.append(line.split())

                    out = np.array(s, dtype=float)
                    for i in range(len(out) - 1):
                        out[i, 0] = (out[i, 0] + out[i + 1, 0]) / 2
                        out[i, 1] = out[i + 1, 1]
                    out = np.delete(out, np.s_[-1:], 0)

                spectr = out

            elif self.spectr_type == 'DISCRETE':
                spectr = np.loadtxt(self.spectr_dir, skiprows=2)
            return spectr
        except Exception:
            main_spectr_ex_example()
            return 1

    def interpolate_user_time(self):

        entry_t, entry_f, time_cell = self.data_control()
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
            # (f'{time_cell[left_side]} - {time_cell[right_side]}')
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

        # print(len(func_out))
        # print('заданныйэ = ', time_cell.shape, time_cell[-1])
        # print('по факту = ', len(time_count), time_count[-1])

        return func_out, time_count

    def graph_painter(self, time_count, func_out, widget, dpi=85):
        try:
            self.figure.clf()
            self.chart_type.draw()
        except:
            pass

        self.figure = plt.Figure(figsize=(6, 4), dpi=dpi)
        self.ax = self.figure.add_subplot(111)
        self.ax.plot(time_count, func_out, label='Пользовательская функция')

        self.ax.set_xlabel('Time , s', fontsize=14)
        self.ax.set_ylabel('Function', fontsize=14)
        self.chart_type = FigureCanvasTkAgg(self.figure, widget)

        self.chart_type.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)
        self.ax.set_title(f'{self.name}')
        self.ax.legend()

    def data_control(self):
        self.grd_def = self.child_parcecer_grid()
        self.user_timeset = float(self.entry_time_fix_val.get())

        # print(f'функция {self.func_list}')
        # print(f'время {self.time_list}')
        entry_f = np.array(self.func_list)
        entry_t = np.array(self.time_list)

        # блок проверки на ограничение пользователем тайм функции
        if self.grd_def[-1] == self.user_timeset:
            time_cell = self.grd_def
            if entry_t[-1] != time_cell[-1]:
                entry_t = np.append(entry_t, time_cell[-1])
                entry_f = np.append(entry_f, 0)
            if entry_t[0] != 0 and entry_f[0] != 0:
                entry_t = np.insert(entry_t, 0, 0)
                entry_f = np.insert(entry_f, 0, 0)
        else:
            time_right_side = np.where(self.user_timeset == self.grd_def)[0]
            if len(time_right_side) == 0:
                time_right_side = \
                    np.where(abs(self.user_timeset - self.grd_def) <= (self.grd_def[1] - self.grd_def[0]) / 2)[0]
            # print(time_right_side)
            time_cell = self.grd_def[:time_right_side[0]]
            for i in range(len(entry_f)):
                if entry_t[i] > time_cell[-1]:
                    entry_t = np.delete(entry_t, np.s_[i:], 0)
                    entry_f = np.delete(entry_f, np.s_[i:], 0)
                    break
            if entry_t[-1] != time_cell[-1]:
                entry_t = np.append(entry_t, time_cell[-1])
                entry_f = np.append(entry_f, entry_f[-1])
            if entry_t[0] != 0 and entry_f[0] != 0:
                entry_t = np.insert(entry_t, 0, 0)
                entry_f = np.insert(entry_f, 0, 0)

        for i in range(len(entry_t) - 1):
            if entry_t[i] > entry_t[i + 1]:
                print(f'Value error время уменьшается на одном из отрезков {i}')

        return entry_t, entry_f, time_cell

    def value_check(self, func, time):
        for item in func:
            if not (0 <= item <= 1):
                mb.showerror('Value error', f'Значение функции {item} выходит за пределы')
        for item in time:
            if not (self.child_parcecer_grid()[0] <= item <= self.child_parcecer_grid()[-1]):
                mb.showerror('Value error', f'Значение временной функции {item} выходит за пределы')

    def child_parcecer_grid(self):
        return DataParcer(os.path.join(f'{self.path}', check_folder(self.path).get('GRD'))).grid_parcer()

    def onExit(self):
        self.quit()
