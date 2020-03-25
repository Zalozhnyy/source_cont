import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

from utility import config_read, source_number, time_func_dict, pr_dir, source_list
from Main_frame import FrameGen


class Flu(FrameGen):
    def notebooks(self):
        self._notebooks()

        self.button_read_gen = tk.Button(self, width=10, text='Read', command=self.get, state='disabled')
        self.button_read_gen.grid(row=6, column=2)
        self.button_calculate = tk.Button(self, width=10, text='Calculate', command=self.calculate, state='disabled')
        self.button_calculate.grid(row=1, column=5, padx=3)

        self.entry_f_val.set(1.)
        label_f = tk.Label(self, text='F')
        label_f.grid(row=2, column=5, padx=3, sticky='E')
        entry_f = tk.Entry(self, width=3, textvariable=self.entry_f_val)
        entry_f.grid(row=2, column=6, padx=3)

    def get(self):

        # print('get', type(self.func_entry_vel[0]))
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

        self.button_calculate.configure(state='active')

        # print('time = ', self.time_list)
        # print('func = ', self.func_list)

    def calculate(self):

        if len(self.spectr) == 0:
            self.spectr_dir = fd.askopenfilename(title='Выберите файл spectr',
                                                 initialdir=f'{config_read()[0]}/pechs/spectr',
                                                 filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
            self.spectr = np.loadtxt(self.spectr_dir, skiprows=3)

        else:
            answer = mb.askyesno(title="Spectr", message="Выбрать новый спектр?")
            if answer is True:
                self.spectr_dir = fd.askopenfilename(title='Выберите файл spectr', initialdir=f'{config_read()[0]}',
                                                     filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
                self.spectr = np.loadtxt(self.spectr_dir, skiprows=3)

        self.calculate_lay_pl()

    def calculate_lay_pl(self):

        func_out, time_count = self.interpolate_user_time()
        func_out = np.array(func_out)
        time_count = np.array(time_count)
        output_matrix = np.column_stack((time_count, func_out))

        # integrate
        # E_cp = np.sum(self.spectr[:, 0] * self.spectr[:, 1]) / np.sum(self.spectr[:, 1])

        F = float(self.entry_f_val.get())
        # intergal_tf = integrate.simps(y=output_matrix[:, 1], x=output_matrix[:, 0], dx=output_matrix[:, 0])

        # koef = F / (0.23 * E_cp * intergal_tf * 1e3 * 1.6e-19)

        file_name = f'time functions/time_{self.name}.tf'
        # np.savetxt(f'{pr_dir()}/time functions/time_{self.name}.tf', output_matrix, fmt='%-8.4g',
        #            header=f'1 pechs\n{time_count[0]} {time_count[-1]} {koef}\n{len(time_count)}', delimiter='\t',
        #            comments='')
        np.savetxt(f'{pr_dir()}/time functions/time_{self.name}.tf', output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_{self.name}.tf\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')

        time_func_dict.update({f'{self.name}': os.path.normpath(file_name)})

        self.output_dictionary_flu()

        figure = plt.Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot(time_count, func_out, label='Пользовательская функция')

        ax.set_xlabel('Time , s', fontsize=14)
        ax.set_ylabel('Function', fontsize=14)
        chart_type = FigureCanvasTkAgg(figure, self)

        chart_type.get_tk_widget().grid(row=2, column=8, rowspan=40, columnspan=20, padx=10)
        ax.set_title(f'{self.name}')
        ax.legend()

    def output_dictionary_flu(self):
        layers = []
        [layers.append(i) for i in self.name]

        self.pr_dict.update({
            '<номер источника>': source_number,
            '<тип источника>': self.energy_type,
            '<название источника>': self.name,
            '<номер слоя>': 0,
            '<номер слоя из>': layers[-2],
            '<номер слоя в>': layers[-1],
            '<амплитуда источинка в ближней зоне источника>': 0,
            '<амплитуда источинка в дальней зоне источника>': float(self.entry_f_val.get()),
            '<спектр источника>': self.spectr_dir,
            '<временная функция источинка>': time_func_dict.get(f'{self.name}'),
            '<запаздывание(0 - нет, 1 - есть)>': 1,
            '<X-координата источника>': 0,
            '<Y-координата источника>': 0,
            '<Z-координата источника>': 0,
            '<X-координата объекта>': 0,
            '<Y-координата объекта>': 0,
            '<Z-координата объекта>': 0,
            '<полярный угол поворта локальной системы координат относительно глобальной>': None,
            '<азимутальный угол поворта локальной системы координат относительно глобальной>': None,
            '<X-компонента направляющего косинуса для расчета в дальней зоне>': None,
            '<Y-компонента направляющего косинуса для расчета в дальней зоне>': None,
            '<Z-компонента направляющего косинуса для расчета в дальней зоне>': None
        })
        delete_keys = ['<номер слоя>',
                       '<X-координата источника>',
                       '<Y-координата источника>',
                       '<Z-координата источника>',
                       '<X-координата объекта>',
                       '<Y-координата объекта>',
                       '<Z-координата объекта>',
                       '<полярный угол поворта локальной системы координат относительно глобальной>',
                       '<азимутальный угол поворта локальной системы координат относительно глобальной>',
                       '<X-компонента направляющего косинуса для расчета в дальней зоне>',
                       '<Y-компонента направляющего косинуса для расчета в дальней зоне>',
                       '<Z-компонента направляющего косинуса для расчета в дальней зоне>',
                       '<амплитуда источинка в ближней зоне источника>'
                       ]

        for key in delete_keys:
            if key in self.pr_dict.keys():
                self.pr_dict.pop(key)

        print('flu')
        source_list.append(self.pr_dict)

        # with open(rf'output dicts/{self.name}_out.txt', 'w', encoding='utf-8') as file:
        #     for item in self.pr_dict.items():
        #         file.write(f'{item[0]}\n')
        #         file.write(f'{item[1]}\n')
