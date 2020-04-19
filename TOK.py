import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter import simpledialog
import numpy as np
import matplotlib.pyplot as plt
import os

from Main_frame import FrameGen
from utility import *


class InitialField(FrameGen):

    def notebooks(self):
        self.ini_f_labes_file = []

        rows = 0
        while rows < 50:
            self.rowconfigure(rows, weight=1, minsize=3)
            self.columnconfigure(rows, weight=1, minsize=3)
            rows += 1

        tk.Label(self, text='Ex').grid(row=2, column=5, sticky='E', padx=3)
        tk.Label(self, text='Ey').grid(row=3, column=5, sticky='E', padx=3)
        tk.Label(self, text='Ez').grid(row=4, column=5, sticky='E', padx=3)
        tk.Label(self, text='hx').grid(row=5, column=5, sticky='E', padx=3)
        tk.Label(self, text='hy').grid(row=6, column=5, sticky='E', padx=3)
        tk.Label(self, text='hz').grid(row=7, column=5, sticky='E', padx=3)

        self.some_x_val = [tk.StringVar() for _ in range(6)]

        for i in self.some_x_val:
            i.set('0')
        for i in range(6):
            some_x = tk.Entry(self, textvariable=self.some_x_val[i], width=4)
            some_x.grid(row=2 + i, column=6)

        ini_save_button = tk.Button(self, width=10, text='Save', state='normal', command=self.save_Initial_field)
        ini_save_button.grid(row=0, column=6, pady=5)

    def save_Initial_field(self):

        back = self.name

        if len(self.ini_f_labes_file) != 0:
            for i in self.ini_f_labes_file:
                i.destroy()
            self.ini_f_labes_file.clear()

        ask = mb.askyesno('?', 'Дать файлу уникальное имя?')
        if ask is True:
            self.name = tk.simpledialog.askstring('Введите имя файла', 'Func name')
            if len(self.name) == 0 or self.name == ' ':
                self.name = back
        self.ini_f_labes_file.append(tk.Label(self, text=f'time functions/time_{self.name}_koef.txt'))
        self.ini_f_labes_file[0].grid(row=0, column=7)
        Initial_field_values_dict = {
            'Ex': self.some_x_val[0].get(),
            'Ey': self.some_x_val[1].get(),
            'Ez': self.some_x_val[2].get(),
            'hx': self.some_x_val[3].get(),
            'hy': self.some_x_val[4].get(),
            'hz': self.some_x_val[5].get()
        }

        with open(rf'{pr_dir()}/time functions/time_{self.name}_koef.txt', "w", encoding='utf-8') as f:
            for item in Initial_field_values_dict.items():
                # print(f'{item[0]} = {item[1]}')
                f.write(f'{item[0]} = {item[1]}\n')


class ExternalField(FrameGen):
    def notebooks(self):
        self._notebooks()

        self.graph_ext_checkbutton = tk.BooleanVar()
        self.graph_ext_checkbutton.set(0)
        ttk.Checkbutton(self, text='Построение графика', variable=self.graph_ext_checkbutton,
                        onvalue=1, offvalue=0).grid(row=1, column=6, columnspan=2,padx=10,sticky='N')
        self.button_calculate.destroy()

        self.ext_frame()

    def ext_frame(self):
        self.ext_fr = tk.LabelFrame(self, text='Компоненты')
        self.ext_fr.grid(row=1, column=3, columnspan=3, rowspan=6,sticky='N')

        tk.Label(self.ext_fr, text='Ex').grid(row=0, column=0, sticky='E', padx=3)
        tk.Label(self.ext_fr, text='Ey').grid(row=1, column=0, sticky='E', padx=3)
        tk.Label(self.ext_fr, text='Ez').grid(row=2, column=0, sticky='E', padx=3)
        tk.Label(self.ext_fr, text='hx').grid(row=3, column=0, sticky='E', padx=3)
        tk.Label(self.ext_fr, text='hy').grid(row=4, column=0, sticky='E', padx=3)
        tk.Label(self.ext_fr, text='hz').grid(row=5, column=0, sticky='E', padx=3)

        self.external_field_values_dict = {
            'Ex': 0,
            'Ey': 0,
            'Ez': 0,
            'hx': 0,
            'hy': 0,
            'hz': 0
        }
        self.ext_load_tf_button = []
        self.some_x_val = [tk.StringVar() for _ in range(6)]

        for i in self.some_x_val:
            i.set('0')
        for i in range(6):
            some_x = tk.Entry(self.ext_fr, textvariable=self.some_x_val[i], width=4)
            some_x.grid(row=0 + i, column=1)

        keys = []
        [keys.append(i) for i in self.external_field_values_dict.keys()]

        for i in range(len(keys)):
            self.ext_load_tf_button.append(tk.Button(self.ext_fr, text=f'calc {keys[i]} tf', overrelief='ridge',
                                                     width=9, state='disabled'))
            self.ext_load_tf_button[i].grid(row=0 + i, column=2, padx=3, pady=2)

        self.ext_load_tf_button[0].configure(command=lambda: self.calculate_external_field(keys[0]))
        self.ext_load_tf_button[1].configure(command=lambda: self.calculate_external_field(keys[1]))
        self.ext_load_tf_button[2].configure(command=lambda: self.calculate_external_field(keys[2]))
        self.ext_load_tf_button[3].configure(command=lambda: self.calculate_external_field(keys[3]))
        self.ext_load_tf_button[4].configure(command=lambda: self.calculate_external_field(keys[4]))
        self.ext_load_tf_button[5].configure(command=lambda: self.calculate_external_field(keys[5]))

    def button_states(self):

        self.button_save.configure(state='active')
        self.button_save_def.configure(state='active')
        self.button_browse.configure(state='disabled')

        for button in self.ext_load_tf_button:
            button.configure(state='normal')

    def local_get(self):
        self.get()
        self.button_states()

    def local_get_row(self):
        self.row_get()
        self.button_states()

    def calculate_external_field(self, key):

        if len(self.spectr) == 0:
            try:
                self.spectr_dir, self.spectr_type = self.spectr_choice_classifier()
                self.spectr = self.spectr_choice_opener()
                if type(self.spectr) is int:
                    raise Exception('Чтение файла вызвало ошибку')
            except FileNotFoundError:
                print('Файл не выбран')
                return
            except Exception:
                print('stectr_choice unknown error')
                return
        else:
            answer = mb.askyesno(title="Spectr", message="Выбрать новый спектр?")
            if answer is True:
                self.spectr_dir, self.spectr_type = self.spectr_choice_classifier()

                self.spectr = self.spectr_choice_opener()
                if type(self.spectr) is int:
                    return

        self.external_field_values_dict = {
            'Ex': self.some_x_val[0].get(),
            'Ey': self.some_x_val[1].get(),
            'Ez': self.some_x_val[2].get(),
            'hx': self.some_x_val[3].get(),
            'hy': self.some_x_val[4].get(),
            'hz': self.some_x_val[5].get()
        }

        func_out, time_count = self.interpolate_user_time()
        func_out = np.array(func_out)
        time_count = np.array(time_count)
        output_matrix = np.column_stack((time_count, func_out))

        file_name = f'time functions/TOK/time_ext_{key}.tf'
        # np.savetxt(f'{pr_dir()}/time functions/TOK/time_ext_{key}.tf', output_matrix, fmt='%-8.4g',
        #            header=f'{key} = {self.external_field_values_dict.get(key)}\ntime\t\tfunc', delimiter='\t',
        #            comments='')
        np.savetxt(f'{pr_dir()}/time functions/TOK/time_ext_{key}.tf', output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_ext_{key}.tf\n'
                          f'<Составляющая поля>\n'
                          f'{key}\n'
                          f'<Значение составляющей поля>\n'
                          f'{self.external_field_values_dict.get(key)}\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')
        self.external_tf_num.append(file_name)

        print(f'{key}  рассчитан')

        time_for_dict, func_for_dict, _ = self.data_control()

        remp_sources_dict_val = {'source_type': self.energy_type,
                                 'source_name': self.name,
                                 'layer_index': self.name.split('_')[-1],
                                 'amplitude': None,
                                 'len_tf': len(time_for_dict),
                                 'time': time_for_dict,
                                 'value': func_for_dict,
                                 'lag': 0,
                                 'koord_ist': '',
                                 'distribution': None}
        remp_sourses_dict.update({f'{self.name}_{key}': remp_sources_dict_val})

        time_func_dict.update({f'{self.name}': os.path.normpath(file_name)})

        if self.name in time_func_dict.keys():
            time_func_dict.popitem()
        if len(self.external_tf_num) == 1:
            time_func_dict.update({f'{self.name}': self.external_tf_num[0]})
        else:
            time_func_dict.update({f'{self.name}': self.external_tf_num})

        if self.graph_ext_checkbutton.get() == 1:
            # построение графиков
            if self.graph_frame_exist == 1:
                self.graph_fr.destroy()

            self.graph_fr = tk.LabelFrame(self, text='График', width=30)
            self.graph_fr.grid(row=2, column=6, padx=10, pady=10, rowspan=6, columnspan=20, sticky='N')
            self.graph_painter(time_count, func_out, self.graph_fr)
            self.graph_frame_exist = 1


class Koshi(FrameGen):
    def koshi_nb(self):
        rows = 0
        while rows < 100:
            self.rowconfigure(rows, weight=0, minsize=5)
            self.columnconfigure(rows, weight=0, minsize=5)
            rows += 1
        source_button = tk.Button(self, text='Открыть программу source', command=lambda: os.startfile('source.exe'))
        source_button.grid(row=5, column=5)
