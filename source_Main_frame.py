import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)
import matplotlib.ticker
from matplotlib.figure import Figure
import numpy as np
from numpy import exp, sin, cos, tan, log10, arcsin, arccos, arctan, arcsinh, arccosh, arctanh, sinh, cosh, tanh
from numpy import log as ln
from loguru import logger

from source_utility import *
from source_Spectre_one_interface import ScrolledWidget




@logger.catch()
class FrameGen(ttk.LabelFrame):
    def __init__(self, parent, path, data_obj, size_objects: tuple, grd_array):
        super().__init__(parent)

        self.parent = parent
        self.remp_source = None
        self.db = data_obj

        self.configure(text=self.db.obj_name)

        self.path = path
        self.pr_dir = path
        self.__nb_widget = size_objects[0]
        self.__root_widget = size_objects[1]

        # parent.geometry('1180x800')
        # parent.resizable(width=False, height=False)

        self.entry_func = []
        self.entry_time = []
        self.func_entry_vel = []
        self.time_entry_vel = []
        self.func_list = []
        self.time_list = []
        self.func_bind_id = []
        self.time_bind_id = []

        self.backup_tf = None
        self.backup_fu = None

        self.cell_numeric = tk.StringVar()
        self.entry_f_val = tk.StringVar()
        self.entry_time_fix_val = tk.StringVar()

        self.cell_numeric = 2

        self._grd_data = grd_array
        self._grd_corners = f'[{self._grd_data[0]} - {self._grd_data[-1]}]'

        self._error_label = None
        self.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='WN')

    def _notebooks(self):

        self.button_change_method = tk.Button(self)
        self.button_change_method.grid(row=3, column=0, padx=5, pady=5, sticky='WN', columnspan=2)

        self.graph_frame()
        self.constants_frame()
        if self.db.get_share_data('count') < 102:
            self.entry_func_frame()
        else:
            for i in range(self.db.get_share_data('count')):
                tmp_f = tk.StringVar()
                tmp_f.set(str(self.db.get_share_data('func')[i]))
                self.func_entry_vel.append(tmp_f)

                tmp_t = tk.StringVar()
                tmp_t.set(str(self.db.get_share_data('time')[i]))
                self.time_entry_vel.append(tmp_t)

            self.rows_metod()

        self.update()
        # w = self.__root_widget.winfo_width()
        # h = self.__root_widget.winfo_height()
        # if w > 500:
        #     self.__root_widget.geometry(f'{w}x{h}')

    def _initial_start_values(self):

        tf = 0

    def entry_func_frame(self):

        if type(self.func_entry_vel) is not list:
            if 'T' in self.func_entry_vel.get():
                tmp_f = self.func_list
            else:
                tmp_f = self.func_entry_vel.get().split()
            tmp_t = self.time_entry_vel.get().split()
            if len(tmp_f) != len(tmp_t):
                print('Размерности не совпадают')
                print(f'f = {tmp_f}')
                print(f't = {tmp_t}')
                return
            self.entry_func_fr.destroy()
            self.d_fr.destroy()

            self.func_entry_vel = []
            for i, val in enumerate(tmp_f):
                self.func_entry_vel.append(tk.StringVar())
                self.func_entry_vel[i].set(val)

            self.time_entry_vel = []
            for i, val in enumerate(tmp_t):
                self.time_entry_vel.append(tk.StringVar())
                self.time_entry_vel[i].set(val)

            from_row = True
        else:
            from_row = False


        self.cf = ScrolledWidget(self, (420, 600))
        self.cf.grid(row=4, column=0, padx=25)

        self._error_label = tk.Label(self.cf.frame)
        self._error_label.grid(row=0, column=0, padx=5, pady=5, sticky='WN', columnspan=3)

        self.entry_func_fr = tk.LabelFrame(self.cf.frame, text='Временная функция')
        self.entry_func_fr.grid(row=4, column=0, columnspan=3, padx=5, rowspan=20)

        label_func = tk.Label(self.entry_func_fr, text='Значение функции', width=15)
        label_func.grid(row=3, column=1, padx=2, pady=2)
        label_time = tk.Label(self.entry_func_fr, text='Время', width=15)
        label_time.grid(row=3, column=0, padx=2, pady=2)

        initiate = True if self.db.get_share_data('time_full') is None or len(
            self.db.get_share_data('time_full')) == 0 else False

        self.ent(from_row, initiate)

        self.button_change_method.configure(text='Строчный ввод', command=self.rows_metod, width=15)

        self.update()
        w = self.__nb_widget.winfo_width()
        h = self.__nb_widget.winfo_height()
        if w > 500:
            self.__root_widget.geometry(f'{w}x{h}')

    def description_fr(self):
        self.d_fr = ttk.LabelFrame(self, text='Подсказка')
        self.d_fr.grid(row=0, column=3, columnspan=4, rowspan=5, padx=5, sticky='NE')

        t = 'Значения заполняются через пробел\n' \
            'Для создания диапазона значений в строке "Время"\n' \
            'введите range[начало;конец;количество шагов]\n' \
            'Для применения формул в строке "Функция" введите\n' \
            'exp(T), ln(T) и т.д Так же доступны все мат. операции\n' \
            'возведение в степень: a**n\n\n' \
            'Для сортировки времени переведите курсор в окно ввода\n' \
            'временной функции и нажмите Enter'
        discription = tk.Label(self.d_fr, text=t)
        discription.grid(row=0, column=5, columnspan=3, rowspan=5)

    def constants_frame(self):
        self.constants_fr = tk.Frame(self)
        self.constants_fr.grid(row=0, column=0, sticky='NW', padx=5, columnspan=3)

        self.entry_f_val.set(f"{self.db.get_share_data('amplitude')}")

        self.amplitude_label = tk.Label(self.constants_fr, text='Суммарный выход\nиз источника')
        # label_f = tk.Label(self.constants_fr, text='Суммарный выход частиц\nиз источника')
        self.amplitude_label.grid(row=0, column=0, padx=3, sticky='E', pady=3)

        self.entry_f = tk.Entry(self.constants_fr, width=16, textvariable=self.entry_f_val)
        self.entry_f.grid(row=0, column=2, padx=3)
        self.entry_f.focus_force()

        combobox_values = ['шт', 'шт/с']
        decode = [True, False]

        self._integrate_decode_dict = dict(zip(combobox_values, decode))

        self._integrate_combobox = ttk.Combobox(self.constants_fr, value=[val for val in combobox_values],
                                                width=15, state='readonly')

        self._integrate_combobox.bind("<<ComboboxSelected>>", self.__change_db_integrate_flag_state)

        self._integrate_combobox.grid(row=0, column=3, columnspan=2, sticky='W')

        try:
            if self.db.get_share_data('integrate'):
                self._integrate_combobox.set(combobox_values[0])
            else:
                self._integrate_combobox.set(combobox_values[1])
        except KeyError:
            self._integrate_combobox.set(combobox_values[0])

        self.__change_db_integrate_flag_state(None)

        self.entry_f.bind("<FocusOut>", self.__get_amplitude_callback)

    def graph_frame(self):
        self.graph_fr = tk.LabelFrame(self, text='График', width=30)
        self.graph_fr.grid(row=0, column=5, padx=10, pady=10, rowspan=15, columnspan=30, sticky='NWSE')

        self.figure = Figure(figsize=(5, 5), dpi=100)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_fr)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

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

        try:
            self.cf.destroy()
        except Exception:
            pass
        try:
            self.entry_func_fr.destroy()
        except Exception:
            pass

        self.entry_func_fr = tk.LabelFrame(self, text='Блок ввода данных временной функции')
        self.entry_func_fr.grid(row=4, column=0, columnspan=3, padx=5, sticky='NWE')
        self.description_fr()

        tk.Label(self.entry_func_fr, text='Время').grid(row=0, column=0, pady=3, padx=2)
        self.entry_time = tk.Entry(self.entry_func_fr, width=50, textvariable=self.time_entry_vel, justify='left')
        self.entry_time.grid(row=0, column=1, pady=3, padx=2, columnspan=7, sticky='WEN')

        self.entry_time.bind('<Return>', self.__row_sort_method)
        self.entry_time.bind('<FocusOut>', self.__get_row_callback)

        tk.Label(self.entry_func_fr, text='Зн. функции').grid(row=2, column=0, pady=3, padx=2)
        self.entry_func = tk.Entry(self.entry_func_fr, width=50, textvariable=self.func_entry_vel, justify='left')
        self.entry_func.grid(row=2, column=1, pady=3, padx=2, columnspan=7, sticky='WEN')

        self.entry_func.bind('<FocusOut>', self.__get_row_callback)

        self.entryScroll_func = tk.Scrollbar(self.entry_func_fr, orient=tk.HORIZONTAL,
                                             command=self.__scrollHandler_func)
        self.entryScroll_func.grid(row=3, column=0, columnspan=8, sticky='WEN')
        self.entry_func["xscrollcommand"] = self.entryScroll_func.set

        self.entryScroll_time = tk.Scrollbar(self.entry_func_fr, orient=tk.HORIZONTAL,
                                             command=self.__scrollHandler_time)
        self.entryScroll_time.grid(row=1, column=0, columnspan=8, sticky='WEN')
        self.entry_time["xscrollcommand"] = self.entryScroll_time.set

        # self.button_read_gen = tk.Button(self.entry_func_fr, width=10, text='Прочитать', state='normal',
        #                                  command=self.row_get)
        # self.button_read_gen.grid(row=7, column=1, padx=3, pady=3)

        tk.Label(self.entry_func_fr, text='Ограничение времени').grid(row=4, column=0, columnspan=2, sticky='W')
        self.entry_time_label = tk.Label(self.entry_func_fr, text=f'{self._grd_corners}')
        self.entry_time_label.grid(row=4, column=2, sticky='W')
        tk.Label(self.entry_func_fr, text='Ограничение функции').grid(row=5, column=0, columnspan=2, sticky='W')
        self.entry_func_label = tk.Label(self.entry_func_fr, text='[0 : 1]')
        self.entry_func_label.grid(row=5, column=2, sticky='W')

        self.obriv_tf_lavel = tk.Label(self.entry_func_fr, text='Принудительно обнулить временную\n'
                                                                'функцию с момента времени:')
        self.obriv_tf_lavel.grid(row=6, column=0, columnspan=2, sticky='W')

        self.entry_time_fix = tk.Entry(self.entry_func_fr, textvariable=self.entry_time_fix_val, width=10,
                                       justify='center')
        self.entry_time_fix.grid(row=6, column=2, sticky='W')

        self._error_label = tk.Label(self.entry_func_fr)
        self._error_label.grid(row=8, column=0, padx=5, pady=5, sticky='WN', columnspan=5)

        self.fix_bind_id = self.entry_time_fix.bind("<FocusOut>", self.__get_row_callback)

        self.__row_grid_configure()

        # self.button_save_def.configure(state='disabled')
        # self.button_save.configure(state='disabled')
        self.button_change_method.configure(text='Дискретный метод', width=15,
                                            command=lambda: (self.entry_func_frame()))

        self.update()
        w = self.__nb_widget.winfo_width()
        h = self.__nb_widget.winfo_height()
        if w > 500:
            self.__root_widget.geometry(f'{w}x{h}')

    def ent(self, row_m, initiate=False):
        self.entry_func = []
        self.entry_time = []
        self.func_bind_id = []
        self.time_bind_id = []

        if row_m is False:
            self.func_entry_vel.clear()
            self.time_entry_vel.clear()

            self.time_entry_vel = [tk.StringVar() for _ in range(self.cell_numeric)]
            self.func_entry_vel = [tk.StringVar() for _ in range(self.cell_numeric)]

            if initiate:
                [self.func_entry_vel[i].set('1') for i in range(len(self.func_entry_vel))]

                self.time_entry_vel[0].set(f'{self._grd_data[0]}')
                self.time_entry_vel[-1].set(f'{self._grd_data[-1]}')

        elif row_m is True:
            self.cell_numeric = len(self.time_entry_vel)
            if self.cell_numeric == 0:
                self.cell_numeric = 2
                self.func_entry_vel.clear()
                self.time_entry_vel.clear()

                self.time_entry_vel = [tk.StringVar() for _ in range(self.cell_numeric)]
                self.func_entry_vel = [tk.StringVar() for _ in range(self.cell_numeric)]

        for i in range(int(self.cell_numeric)):
            self.entry_time.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=4 + i, column=0, pady=3, padx=2)

            self.entry_func.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=4 + i, column=1, pady=3, padx=2)

            time_bind = self.entry_time[i].bind("<FocusOut>", self.__get_callback)
            func_bind = self.entry_func[i].bind("<FocusOut>", self.__get_callback)

            self.time_bind_id.append(time_bind)
            self.func_bind_id.append(func_bind)

            self.entry_time[i].bind('<Shift-KeyPress Down>', lambda _, index=i: self.add_entry(index, _))
            self.entry_func[i].bind('<Shift-KeyPress Down>', lambda _, index=i: self.add_entry(index, _))
            self.entry_time[i].bind('<Shift-KeyPress Up>', lambda _, index=i: self.delete_entry(index, _))
            self.entry_func[i].bind('<Shift-KeyPress Up>', lambda _, index=i: self.delete_entry(index, _))

            self.entry_time[i].bind('<Return>', self.__sort_method)

        self.entry_time_fix_val.set(f'{self._grd_data[-1]}')
        self.end_time = self._grd_data

        self.entry_time_label = tk.Label(self.entry_func_fr, text=self._grd_corners)
        self.entry_time_label.grid(row=5 + int(self.cell_numeric), column=0)
        self.entry_func_label = tk.Label(self.entry_func_fr, text='[0 : 1]')
        self.entry_func_label.grid(row=5 + int(self.cell_numeric), column=1)

        self.obriv_tf_lavel = tk.Label(self.entry_func_fr, text='Принудительно обнулить\n'
                                                                'временную ф-ю с момента времени:')
        self.obriv_tf_lavel.grid(row=6 + len(self.func_entry_vel), column=0)

        self.entry_time_fix = tk.Entry(self.entry_func_fr, textvariable=self.entry_time_fix_val, width=10,
                                       justify='center')
        self.entry_time_fix.grid(row=6 + len(self.func_entry_vel), column=1)

        self.fix_bind_id = self.entry_time_fix.bind("<FocusOut>", self.__get_callback)

        d_t = 'Shift + Down - доб. яч. ниже выбранной\n' \
              'Shift + Up      - уд. выбранную яч.\n' \
              'Enter  -  сортировка'
        self.discrete_description_label = tk.Label(self.entry_func_fr, text=d_t, justify='left')
        self.discrete_description_label.grid(row=8 + len(self.func_entry_vel), column=0, columnspan=3)

        if initiate:
            self.get()

        self.__grid_configure()

    def load_data(self):
        time_ = self.db.get_share_data('time_full')
        func = self.db.get_share_data('func_full')
        self.entry_time_fix_val.set(self.db.get_share_data('tf_break'))

        if isinstance(self.func_entry_vel, tk.StringVar):
            pass
        else:
            for i in range(len(self.func_entry_vel)):
                self.func_entry_vel[i].set(str(func[i]))
                self.time_entry_vel[i].set(str(time_[i]))

        try:
            self.entry_f_val.set('{:0g}'.format(self.db.get_share_data('amplitude')))
        except TypeError:
            self.entry_f_val.set('1')

        if isinstance(self.func_entry_vel, tk.StringVar):
            self.row_get()
        else:
            self.get()

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
        self.entry_time_label.grid(row=5 + len(self.time_entry_vel), column=0)
        self.entry_func_label = tk.Label(self.entry_func_fr, width=9, text='[0 : 1]')
        self.entry_func_label.grid(row=5 + len(self.func_entry_vel), column=1)

        self.obriv_tf_lavel = tk.Label(self.entry_func_fr, text='Обрыв tf')
        self.obriv_tf_lavel.grid(row=6 + len(self.func_entry_vel), column=0)
        self.entry_time_fix_val.set(f'{A[-1]}')
        self.entry_time_fix = tk.Entry(self.entry_func_fr, textvariable=self.entry_time_fix_val, width=6)
        self.entry_time_fix.grid(row=6 + len(self.func_entry_vel), column=1)

        if len(self.func_entry_vel) != len(self.time_entry_vel):
            mb.showerror('Load error', 'Размерности не совпадают')
            self.onExit()

        # self.button_read_gen.configure(state='normal')
        # self.button_generate.configure(state='disabled')
        self.add_button.configure(state='normal')
        self.del_button.configure(state='normal')

    def add_entry(self, index, event):
        for i in self.entry_func:
            i.unbind_all('<Shift-KeyPress Down>')
            i.unbind_all('<Shift-KeyPress Up>')
            i.destroy()
        for i in self.entry_time:
            i.unbind_all('<Shift-KeyPress Down>')
            i.unbind_all('<Shift-KeyPress Up>')
            i.destroy()

        # print(index)

        self.entry_time.clear()
        self.entry_func.clear()

        self.func_entry_vel.insert(index + 1, tk.StringVar())
        self.func_entry_vel[index + 1].set('')

        self.time_entry_vel.insert(index + 1, tk.StringVar())
        self.time_entry_vel[index + 1].set('')

        for i in range(len(self.time_entry_vel)):
            self.entry_time.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=4 + i, column=0, pady=3, padx=2)
            self.entry_func.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=4 + i, column=1, pady=3, padx=2)

            time_bind = self.entry_time[i].bind("<FocusOut>", self.__get_callback)
            func_bind = self.entry_func[i].bind("<FocusOut>", self.__get_callback)

            self.time_bind_id.append(time_bind)
            self.func_bind_id.append(func_bind)

            self.entry_time[i].bind('<Shift-KeyPress Down>', lambda _, index=i: self.add_entry(index, _))
            self.entry_func[i].bind('<Shift-KeyPress Down>', lambda _, index=i: self.add_entry(index, _))
            self.entry_time[i].bind('<Shift-KeyPress Up>', lambda _, index=i: self.delete_entry(index, _))
            self.entry_func[i].bind('<Shift-KeyPress Up>', lambda _, index=i: self.delete_entry(index, _))

            self.entry_time[i].bind('<Return>', self.__sort_method)

        self.entry_time_label.grid_configure(row=len(self.func_entry_vel) + 4)
        self.entry_func_label.grid_configure(row=len(self.func_entry_vel) + 4)

        self.obriv_tf_lavel.grid_configure(row=len(self.func_entry_vel) + 5)
        self.entry_time_fix.grid_configure(row=len(self.func_entry_vel) + 5)

        self.discrete_description_label.grid_configure(row=8 + len(self.func_entry_vel))

        self.entry_time[index].focus()

        # self.button_calculate.configure(state='disabled')

    def delete_entry(self, index, event):
        for i in self.entry_func:
            i.destroy()
        for i in self.entry_time:
            i.destroy()

        self.entry_time.clear()
        self.entry_func.clear()

        self.func_entry_vel.pop(index)
        self.time_entry_vel.pop(index)

        # self.entry_func[index].grid_remove()
        # self.entry_time[index].grid_remove()
        # self.entry_func[index].destroy()
        # self.entry_time[index].destroy()

        # self.entry_func.pop(index)
        # self.entry_time.pop(index)

        for i in range(len(self.time_entry_vel)):
            # self.entry_time[i].grid_configure(row=4 + i, column=0, pady=3, padx=2)
            # self.entry_func[i].grid_configure(row=4 + i, column=1, pady=3, padx=2)

            self.entry_func.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=4 + i, column=1, pady=3, padx=2)
            self.entry_time.append(
                tk.Entry(self.entry_func_fr, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=4 + i, column=0, pady=3, padx=2)

            self.entry_time[i].bind('<Shift-KeyPress Down>', lambda _, index=i: self.add_entry(index, _))
            self.entry_func[i].bind('<Shift-KeyPress Down>', lambda _, index=i: self.add_entry(index, _))
            self.entry_time[i].bind('<Shift-KeyPress Up>', lambda _, index=i: self.delete_entry(index, _))
            self.entry_func[i].bind('<Shift-KeyPress Up>', lambda _, index=i: self.delete_entry(index, _))

            self.entry_time[i].bind('<Return>', self.__sort_method)

        self.entry_time_label.grid_configure(row=len(self.func_entry_vel) + 2 + 4)
        self.entry_func_label.grid_configure(row=len(self.func_entry_vel) + 2 + 4)

        self.obriv_tf_lavel.grid_configure(row=len(self.func_entry_vel) + 2 + 5)
        self.entry_time_fix.grid_configure(row=len(self.func_entry_vel) + 2 + 5)
        self.discrete_description_label.grid_configure(row=8 + len(self.func_entry_vel))

        # self.button_calculate.configure(state='disabled')

        try:
            self.entry_time[index].focus_set()
        except IndexError:
            pass

        self.get()

    def time_range(self):
        s = self.time_entry_vel.get()
        s.strip()
        if s[-1] != ']':
            return
        f_ind = s.find('[')
        s_ind = s.rfind(']')

        data = s[f_ind + 1:s_ind]
        data = data.split(';')
        print(data)
        fr = float(data[0])
        to = float(data[1])
        num = int(data[2])
        if fr < 0:
            print('Начало меньше нуля')
            return
        if fr > float(self.end_time[-1]):
            ask = mb.askyesno('info', f'Обнаружено что введённое значение {fr} '
                                      f'превышает конечное значение на временной сетке {self.end_time[0]}\n'
                                      f'Заменить {to} на {self.end_time[0]}?')
            if ask is True:
                fr = float(self.end_time[-1])

        if to > float(self.end_time[-1]):
            ask = mb.askyesno('info', f'Обнаружено что введённое значение {to} '
                                      f'превышает конечное значение на временной сетке {self.end_time[-1]}\n'
                                      f'Заменить {to} на {self.end_time[-1]}?')
            if ask is True:
                to = float(self.end_time[-1])

        if fr > to:
            mb.showerror('info', f'Начальное значение {fr} jkmit ')

        gen = np.linspace(fr, to, num)
        ins = ''
        for i in gen:
            ins += '{:.3g}'.format(i) + ' '
        return ins

    def row_get(self):
        self.func_list = []
        self.time_list = []

        if 'range' in self.time_entry_vel.get():
            print('range in line')
            try:
                t = self.time_range()
                if t is not None:
                    self.time_entry_vel.set(t)
                    print('range_выполнен')
                elif t is None:
                    raise Exception
            except Exception:
                return

        for i in self.time_entry_vel.get().split():
            try:
                self.time_list.append(float(i))
            except ValueError:
                print(f'{i} не может быть преобразовано в float')
                # mb.showerror('Value error', f'{i} не может быть преобразовано в float')
            except Exception:
                pass

        func_string = self.func_entry_vel.get()
        if '(' in func_string or 'T' in func_string:
            tmp = ''
            for i in range(len(self.time_list)):
                calc = func_string.replace('T', f'{self.time_list[i]}')

                try:
                    self.func_list.append(float(calc))
                    tmp += '{:.5g} '.format(float(calc))
                except Exception:
                    pass

            # self.func_entry_vel.set(tmp)

        else:
            for i in self.func_entry_vel.get().split():
                try:
                    self.func_list.append(float(i))
                except ValueError:
                    print(f'{i} не может быть преобразовано в float')
                    # mb.showerror('Value error', f'{i} не может быть преобразовано в float')
                    # return 0
                except Exception:
                    pass

        if len(self.func_list) != len(self.time_list):
            print('Размерности не совпадают!')
            self.entry_time.configure(bg='#F08080')
            self.entry_func.configure(bg='#F08080')
            if 'Размерности не совпадают' not in self._error_label['text']:
                self._error_label['text'] += '\nРазмерности не совпадают'
            # mb.showerror('Index error', 'Размерности не совпадают!')
            return
        else:
            self.entry_time.configure(bg='#FFFFFF')
            self.entry_func.configure(bg='#FFFFFF')

        time_list, func_list, _ = self.data_control()

        if time_list is None:
            return

        self.time_list = list(time_list)
        self.func_list = list(func_list)

        # print('time = ', self.time_list)
        # print('func = ', self.func_list)
        self.db.insert_share_data('count', len(self.time_list))
        self.db.insert_share_data('time', self.time_list)
        self.db.insert_share_data('func', self.func_list)

        try:
            if self.backup_fu is None or self.backup_tf is None:
                raise Exception

            self.db.insert_share_data('func_full', list(self.backup_fu))
            self.db.insert_share_data('time_full', list(self.backup_tf))

        except Exception:
            self.db.insert_share_data('func_full', None)
            self.db.insert_share_data('time_full', None)

        self.db.insert_share_data('tf_break', self.user_timeset)

        self.__painter()

    def get(self):

        # print('get', type(self.func_entry_vel[0]))

        self.func_list = []
        self.time_list = []

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
                    self.func_list[x] = 0
                    # mb.showerror('Value error', f'{self.func_entry_vel[x].get()} не является числом')
                    # return print(f'{self.func_entry_vel[x].get()} не является числом')

        for x, i in enumerate(self.time_list):
            if any([e in i for e in exeption_list]):
                self.time_list = self.eval_transformation(self.time_list, self.time_entry_vel)
                break
            else:
                try:
                    self.time_list[x] = float(self.time_entry_vel[x].get())
                except ValueError:
                    self.time_list[x] = 0
                    # mb.showerror('Value error', f'{self.time_entry_vel[x].get()} не является числом')
                    # return print(f'{self.time_entry_vel[x].get()} не является числом')

        time_list, func_list, _ = self.data_control()
        if time_list is None:
            return

        self.time_list = list(time_list)
        self.func_list = list(func_list)

        # print('time = ', self.time_list)
        # print('func = ', self.func_list)

        self.db.insert_share_data('count', len(self.time_list))
        self.db.insert_share_data('time', self.time_list)
        self.db.insert_share_data('func', self.func_list)

        try:
            if self.backup_fu is None or self.backup_tf is None:
                raise Exception

            self.db.insert_share_data('func_full', list(self.backup_fu))
            self.db.insert_share_data('time_full', list(self.backup_tf))

        except Exception:
            self.db.insert_share_data('func_full', self.func_list)
            self.db.insert_share_data('time_full', self.time_list)

        self.db.insert_share_data('tf_break', self.user_timeset)

        self.__painter()

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

    def interpolate_user_time(self):

        entry_t, entry_f, time_cell = self.data_control()

        time_count = []
        func_out = []
        for i in range(len(entry_t) - 1):
            k, b = Calculations().linear_dif(entry_f[i], entry_t[i], entry_f[i + 1], entry_t[i + 1])
            # print(f'k = {k} , b = {b}')
            # print(np.extract((time_cell == entry_t[i]),time_cell))
            dt = time_cell[i + 1] - time_cell[i]
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

    def data_control(self):
        try:
            self.user_timeset = float(self.entry_time_fix_val.get())
        except Exception:
            print('Ошибка при чтении обрыва')
            return None, None, None

        # print(f'функция {self.func_list}')
        # print(f'время {self.time_list}')
        entry_f = np.array(self.func_list)
        entry_t = np.array(self.time_list)

        if np.any(entry_f < 0):
            print('Значение функции не может быть отрицательным')
            mb.showerror('Entry error', 'Значение функции не может быть отрицательным')
            return None, None, None

        if self.user_timeset > self._grd_data[-1]:
            self.user_timeset = self._grd_data[-1]
            self.entry_time_fix_val.set(str(self.user_timeset))

        self.backup_tf = np.copy(entry_t)
        self.backup_fu = np.copy(entry_f)

        # блок проверки на ограничение пользователем тайм функции
        if self._grd_data[-1] == self.user_timeset:
            time_cell = self._grd_data

            # if entry_t[-1] != time_cell[-1]:
            #     entry_t = np.append(entry_t, time_cell[-1])
            #     entry_f = np.append(entry_f, 0)
            # if entry_t[0] != 0 and entry_f[0] != 0:
            #     entry_t = np.insert(entry_t, 0, 0)
            #     entry_f = np.insert(entry_f, 0, 0)

        else:  # тут происходит какая-то муть, не пытайся понять - просто пройди в дебаге

            time_right_side = np.searchsorted(self._grd_data, self.user_timeset)
            time_cell = self._grd_data[:time_right_side]

            if self.user_timeset not in self.backup_tf:
                for i in range(len(self.backup_tf)):
                    if self.backup_tf[i] > self.user_timeset and i != 0:
                        self.backup_tf = np.insert(self.backup_tf, i, self.user_timeset)
                        self.backup_fu = np.insert(self.backup_fu, i, 0)
                        break

                for i in range(len(self.backup_tf)):
                    if self.backup_tf[i] >= time_cell[-1]:
                        self.backup_fu[i] = 0

            for i in range(len(entry_t)):
                if entry_t[i] == self.user_timeset:
                    entry_t = np.delete(entry_t, np.s_[i + 1:], 0)
                    entry_f = np.delete(entry_f, np.s_[i + 1:], 0)

                    # entry_t = np.append(entry_t, self._grd_data[time_right_side[0] + 1])
                    # entry_f = np.append(entry_f, 0)

                    break

                if entry_t[i] > time_cell[-1]:
                    entry_t = np.delete(entry_t, np.s_[i:], 0)
                    entry_f = np.delete(entry_f, np.s_[i:], 0)

                    if entry_t[-1] != time_cell[-1]:
                        entry_t = np.append(entry_t, time_cell[-1])
                        entry_f = np.append(entry_f, 0)

                    break

        self._timefunction_interface_exceptions(entry_t)

        return entry_t, entry_f, time_cell

    def _timefunction_interface_exceptions(self, entry_t):
        tmp_time_error = []
        out_of_grid_bounds_flag = False

        for i in range(len(entry_t) - 1):
            if entry_t[i] > entry_t[i + 1]:
                tmp_time_error.append(f'{i} - {i + 1}')
                if type(self.entry_time) is list:
                    self.entry_time[i].configure(bg='#F08080')

            else:
                if type(self.entry_time) is list:
                    self.entry_time[i].configure(bg='#FFFFFF')

        for i in range(len(entry_t)):
            if entry_t[i] > self._grd_data[-1]:
                if type(self.entry_time) is list:
                    self.entry_time[i].configure(bg='#F08080')
                else:
                    self.entry_time.configure(bg='#F08080')
                    out_of_grid_bounds_flag = True
                    break

                out_of_grid_bounds_flag = True

            else:
                if type(self.entry_time) is list:
                    self.entry_time[i].configure(bg='#FFFFFF')
                else:
                    self.entry_time.configure(bg='#FFFFFF')
                    break

        if len(tmp_time_error) != 0:
            # mb.showerror('Ошибка ввода времени', f'Время уменьшается на отрезке(ах): {" ".join(tmp_time_error)}\n'
            #                                      f'Исправьте ошибку или примините сортировку (клавиша enter)')
            self._error_label['text'] = f'Время уменьшается на отрезке(ах): {" ; ".join(tmp_time_error)}\n' \
                                        f'Исправьте ошибку или примините сортировку'
            if type(self.entry_time) is not list:
                self.entry_time.configure(bg='#F08080')
        else:
            self._error_label['text'] = ''
            if type(self.entry_time) is not list:
                self.entry_time.configure(bg='#FFFFFF')

        if out_of_grid_bounds_flag:
            self._error_label['text'] += '\nЗначения превышают обозначенный диапазон времени'

    def __painter(self):
        try:
            self.figure.clf()
            self.chart_type.draw()

        except AttributeError:
            pass

        g = self.figure.add_subplot(111)

        # major_axis = self.time_list[-1] / 10
        # g.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(major_axis))

        formatter = matplotlib.ticker.FormatStrFormatter("%.2g")
        g.xaxis.set_major_formatter(formatter)

        g.grid(which='major',
               color='grey',
               alpha=0.8)

        g.minorticks_on()
        g.grid(which='minor',
               color='gray',
               linestyle=':',
               alpha=0.3)

        g.plot(self.time_list, self.func_list, linewidth=1.8)
        g.tick_params(axis='x', which='major', labelsize=9, labelrotation=45)
        g.set_xlabel('Time , s', fontsize=10, labelpad=1.)

        self.figure.tight_layout()
        # g.set_ylabel('Function', fontsize=14)
        self.canvas.draw()

    def __row_grid_configure(self):
        self.constants_fr.grid(row=0, column=0, sticky='NW', padx=5, columnspan=3)
        self.button_change_method.grid(row=1, column=0, padx=5, pady=5, sticky='NW', columnspan=2)
        self.entry_func_fr.grid(row=2, column=0, columnspan=3, padx=5, sticky='NE')
        self.graph_fr.grid(row=3, column=0, padx=5, pady=5, columnspan=20, rowspan=20, sticky='NW')

    def __grid_configure(self):
        self.constants_fr.grid(row=0, column=0, sticky='NW', padx=5, columnspan=3)
        self.button_change_method.grid(row=1, column=0, padx=5, pady=5, sticky='NW', columnspan=2)
        self.entry_func_fr.grid(row=2, column=0, columnspan=3, padx=5, sticky='NE')
        self.graph_fr.grid(row=0, column=4, padx=5, pady=5, columnspan=20, rowspan=20, sticky='N')

    def __get_callback(self, event):
        self.get()

    def __get_row_callback(self, event):
        self.row_get()

    def __get_amplitude_callback(self, event):
        try:
            self.db.insert_share_data('amplitude', float(self.entry_f_val.get()))
            self.entry_f.configure(bg='#FFFFFF')
        except Exception:
            self.entry_f.configure(bg='#F08080')

    def set_amplitude(self):
        try:
            self.entry_f_val.set('{:0g}'.format(self.db.get_share_data('amplitude')))
        except Exception:
            self.entry_f_val.set('')

    def __scrollHandler_func(self, *L):
        op, howMany = L[0], L[1]
        if op == "scroll":
            units = L[2]
            self.entry_func.xview_scroll(howMany, units)
        elif op == "moveto":
            self.entry_func.xview_moveto(howMany)

    def __scrollHandler_time(self, *L):
        op, howMany = L[0], L[1]
        if op == "scroll":
            units = L[2]
            self.entry_time.xview_scroll(howMany, units)
        elif op == "moveto":
            self.entry_time.xview_moveto(howMany)

    def __row_sort_method(self, event):

        time = self.time_entry_vel.get().split()
        func = self.func_entry_vel.get().split()

        if len(time) != len(func):
            # print('Размерности не сопадают, сортировка невозможна')
            mb.showerror('Index error', 'Размерности не сопадают, сортировка невозможна')
            return

        try:
            time = list(map(eval, time))
            func = list(map(eval, func))
        except Exception:
            print('Заполнены не все ячейки')
            return

        d = dict(zip(time, func))

        time = sorted(time)

        time_sorted = ''
        func_sorted = ''
        for i in range(len(time)):
            time_sorted += str(time[i]) + ' '
            func_sorted += str(d[time[i]]) + ' '

        self.time_entry_vel.set(time_sorted)
        self.func_entry_vel.set(func_sorted)
        print('Сортировка времени завершена')

    def __sort_method(self, event):
        if len(self.time_list) != len(self.time_entry_vel):
            print('Размерности не сопадают, сортировка невозможна')
            return

        time = [i.get() for i in self.time_entry_vel]
        func = [i.get() for i in self.func_entry_vel]

        try:
            time = list(map(eval, time))
            func = list(map(eval, func))
        except Exception:
            print('Заполнены не все ячейки')
            return

        d = dict(zip(time, func))

        time = sorted(time)

        for i in range(len(time)):
            self.time_entry_vel[i].set(str(time[i]))
            self.func_entry_vel[i].set(str(d[time[i]]))

        print('Сортировка времени завершена')
        self.get()

    def onExit(self):
        self.quit()

    def __change_db_integrate_flag_state(self, event):

        if self._integrate_decode_dict[self._integrate_combobox.get()]:
            self.db.insert_share_data('integrate', True)
            self.amplitude_label['text'] = 'Суммарный выход\nиз источника'

        else:
            self.db.insert_share_data('integrate', False)
            self.amplitude_label['text'] = 'Максимальная мощность источника'


if __name__ == '__main__':

    class TreeDataStructure:
        def __init__(self, obj_name, part_list=[]):
            self.obj_name = obj_name

            self.particle_list = part_list
            self.__obj_structure = {self.obj_name: {}, 'share_data': {}}

            self.__insert_first_level()
            self.__insert_share_data()

        def __insert_first_level(self):
            for i in self.particle_list:
                self.__obj_structure[self.obj_name].update({f'{i}': {}})

            self.__obj_structure[self.obj_name].update({'Current': {}})
            self.__obj_structure[self.obj_name].update({'Sigma': {}})

        def __insert_share_data(self):
            self.__obj_structure['share_data'].update({'amplitude': None,
                                                       'count': None,
                                                       'time': [],
                                                       'func': [],
                                                       'lag': None,
                                                       'time_full': None,
                                                       'func_full': None,
                                                       'tf_break': None
                                                       })

        def insert_share_data(self, key, value):
            # if key in self.obj_structure['share_data'].keys():
            #     print(f'Ключ {key} был перезаписан')
            self.__obj_structure['share_data'].update({key: value})

            # print(self.obj_structure['share_data'].values())

        def insert_first_level(self, key):
            self.__obj_structure[self.obj_name].update({key: {}})

        def insert_second_level(self, first_level_key, key, val):
            self.__obj_structure[self.obj_name][first_level_key].update({key: val})

        def insert_third_level(self, first_level_key, second_level_key, key, val):
            self.__obj_structure[self.obj_name][first_level_key][second_level_key].update({key: val})

        def delete_first_level(self, first_level_key):
            self.__obj_structure[self.obj_name].pop(first_level_key)

        def delete_second_level(self, second_level_key):
            for items in self.__obj_structure[self.obj_name].items():
                for key in items[-1].keys():
                    if key == second_level_key:
                        self.__obj_structure[self.obj_name][items[0]].pop(key)
                        return

        def get_last_level_data(self, first_level_key, second_level_key, third_level_key):
            return self.__obj_structure[self.obj_name][first_level_key][second_level_key][third_level_key]

        def get_first_level_keys(self):
            return self.__obj_structure[self.obj_name].keys()

        def get_second_level_keys(self, first_key):
            return self.__obj_structure[self.obj_name][first_key].keys()

        def get_share_data(self, key):
            return self.__obj_structure['share_data'][key]


    root = tk.Tk()

    data = TreeDataStructure('test')
    time = [0, 1e-9, 5e-8, 1e-7, 1.5e-6, 2e-6]
    func = [0, 1, 0.9, 0.5, 0.6, 0]

    data.insert_share_data('amplitude', 123)
    data.insert_share_data('time_full', time)
    data.insert_share_data('func_full', func)
    data.insert_share_data('tf_break', time[-1])

    ex = FrameGen(root, r'C:\work\Test_projects\wpala', data)
    ex.cell_numeric = len(time)
    ex._notebooks()
    ex.grid(row=0, column=0, rowspan=30, columnspan=30, sticky='nwse')

    ex.load_data()

    root.mainloop()
