import tkinter as tk
from tkinter import ttk
from scipy import integrate
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from Main_frame import FrameGen
from utility import *


class PlaneWave(FrameGen):

    def notebooks(self):
        self._notebooks()
        self.constants_frame()
        self.plane_wave_const_frame()

    def plane_wave_const_frame(self):
        self.plane_wave_fr = tk.LabelFrame(self, text='Плоская волна', width=20)
        self.plane_wave_fr.grid(row=1, column=4, sticky='NWSE', padx=5, columnspan=2, rowspan=3)

        self.button_calculate.grid_configure(row=4, column=4, sticky='NE')

        cells_label = tk.Label(self.plane_wave_fr, text='Количество ячеек\nв волновой зоне')
        cells_label.grid(row=0, column=0, rowspan=2, padx=3, pady=3)

        self.entry_f_val.set(1)
        cells_entry = tk.Entry(self.plane_wave_fr, width=5, textvariable=self.entry_f_val)
        cells_entry.grid(row=0, column=1, padx=3, pady=3, rowspan=2)

        self.wave_direction = {'X': 1, '-X': -1,
                               'Y': 2, '-Y': -2,
                               'Z': 3, '-Z': -3}
        self.wave_direction_combobox = ttk.Combobox(self.plane_wave_fr, width=3,
                                                    value=[key for key in self.wave_direction.keys()])
        self.wave_direction_combobox.grid(row=2, column=1, padx=3, pady=3, rowspan=2)
        self.wave_direction_combobox.set('X')

        wave_direction_label = tk.Label(self.plane_wave_fr, text='Направление движения\nволны')
        wave_direction_label.grid(row=2, column=0, rowspan=2, padx=3, pady=3)

        self.bind_class(self.wave_direction_combobox, "<<ComboboxSelected>>",
                        self.cdirection_react)  # react на щелчки мышью

        self.sub_wave_direction_combobox_value = []
        self.sub_wave_direction_combobox = ttk.Combobox(self.plane_wave_fr, width=3, state='disabled',
                                                        value=[key for key in self.wave_direction.keys()])
        self.sub_wave_direction_combobox.grid(row=4, column=1, padx=3, rowspan=1)

    def constants_frame(self):
        self.constants_fr = tk.LabelFrame(self, text='Константы', width=20)
        self.constants_fr.grid(row=1, column=2, sticky='NWSE', padx=5, columnspan=2)

        self.entry_f_val.set(1.)
        label_f = tk.Label(self.constants_fr, text='F , кал/см\u00b2')
        label_f.grid(row=0, column=0, padx=3, sticky='E')
        entry_f = tk.Entry(self.constants_fr, width=8, textvariable=self.entry_f_val)
        entry_f.grid(row=0, column=2, padx=3)

    def cdirection_react(self, event):

        react_dict = {'X': [23, 32], '-X': [23, 32],
                      'Y': [13, 31], '-Y': [13, 31],
                      'Z': [21, 12], '-Z': [21, 12]}

        current_axe = self.wave_direction_combobox.get()
        vals_for_combobox = []
        for val in react_dict.get(current_axe):
            vals_for_combobox.append(val)

        self.sub_wave_direction_combobox.configure(value=[val for val in vals_for_combobox], state='normal')
        self.sub_wave_direction_combobox.set(vals_for_combobox[0])

    def local_get(self):
        self.get()
        self.button_states()

    def local_get_row(self):
        self.row_get()
        self.button_states()

    def button_states(self):
        self.button_calculate.configure(state='active', command=self.stectr_choice)

    def stectr_choice(self):
        self.spectr_dir = fd.askopenfilename(title='Выберите файл spectr',
                                             initialdir=f'{config_read()[0]}/pechs/spectr',
                                             filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))

        try:
            self.spectr = np.loadtxt(self.spectr_dir, skiprows=3)
        except Exception:
            print('Чтение невозможно выбирете правильный файл')
            return
        self.calculate()

    def calculate(self):
        func_out, time_count = self.interpolate_user_time()
        func_out = np.array(func_out)
        time_count = np.array(time_count)
        self.output_matrix = np.column_stack((time_count, func_out))

        # integrate
        E_cp = np.sum(self.spectr[:, 0] * self.spectr[:, 1]) / np.sum(self.spectr[:, 1])

        F = float(self.entry_f_val.get())
        intergal_tf = integrate.simps(y=self.output_matrix[:, 1], x=self.output_matrix[:, 0],
                                      dx=self.output_matrix[:, 0])

        self.koef = F / (0.23 * E_cp * intergal_tf * 1e3 * 1.6e-19)

        self.output_dictionary_plane()

        figure = plt.Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot(time_count, func_out, label='Пользовательская функция')

        ax.set_xlabel('Time , s', fontsize=14)
        ax.set_ylabel('Function', fontsize=14)
        chart_type = FigureCanvasTkAgg(figure, self)

        chart_type.get_tk_widget().grid(row=1, column=6, rowspan=20, columnspan=20, padx=10)
        ax.set_title(f'{self.name}')
        ax.legend()

    def output_dictionary_plane(self):

        file_name = f'time functions/time_{self.name}.tf'
        np.savetxt(f'{pr_dir()}/time functions/time_{self.name}.tf', self.output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_{self.name}.tf\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')


        time_for_dict, func_for_dict, _ = self.data_control()

        remp_sources_dict_val = {'source_type': self.energy_type,
                                 'source_name': self.name,
                                 'amplitude': self.koef,
                                 'len_tf': len(time_for_dict),
                                 'time': time_for_dict,
                                 'value': func_for_dict,
                                 'lag': 1,
                                 'koord_ist': None,
                                 'distribution': None}
        remp_sourses_dict.update({self.name: remp_sources_dict_val})

        time_func_dict.update({f'{self.name}': os.path.normpath(file_name)})

        pr_dict = {}
        pr_dict.update({
            '<номер источника>': source_number,
            '<тип источника>': self.energy_type,
            '<название источника>': self.name,
            '<номер слоя>': 0,
            '<амплитуда источинка в ближней зоне источника>': 0,
            '<амплитуда источинка в дальней зоне источника>': self.koef,
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
            if key in pr_dict.keys():
                pr_dict.pop(key)

        source_list.append(pr_dict)