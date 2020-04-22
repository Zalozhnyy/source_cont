import numpy as np
import tkinter as tk
from scipy import integrate
import os

from Project_reader import DataParcer
from Main_frame import FrameGen
from utility import *
from Exceptions import *


class UnitedLayers(FrameGen):

    def notebooks(self):
        self._notebooks()
        self.constants_frame()

    def local_get(self):
        self.get()
        self.button_states()
        self.button_calculate.configure(command=self.stectr_choice)

    def local_get_row(self):
        self.row_get()
        self.button_states()
        self.button_calculate.configure(command=self.stectr_choice)

    def stectr_choice(self):

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

        self.project_checker()

    def button_states(self):
        self.button_calculate.configure(state='active')

    def project_checker(self):
        self.label_num = 0
        self.layers_label_list = []

        LAY = DataParcer(self.lay_dir).lay_decoder()

        self.calculate()

        self.source_labels = tk.LabelFrame(self, text='Источники')
        self.source_labels.grid(row=4, column=3, rowspan=10)
        global source_number
        for i in range(LAY.shape[0]):
            if LAY[i, 1] == 1:
                energy_type = 'Current'
                name = f'{energy_type}_layer_{i}'
                self.output_dictionary_current(name, energy_type)
                source_number += 1

                lay_label = tk.Label(self.source_labels, text=f'{name}')
                lay_label.grid(row=7 + self.label_num, column=3)
                self.layers_label_list.append(lay_label)
                self.label_num += 1

            if LAY[i, 2] == 1:
                energy_type = 'Sigma'
                name = f'{energy_type}_layer_{i}'
                self.output_dictionary_current(name, energy_type)
                source_number += 1

                lay_label = tk.Label(self.source_labels, text=f'{name}')
                lay_label.grid(row=7 + self.label_num, column=3)
                self.layers_label_list.append(lay_label)
                self.label_num += 1

        # for key in PL.keys():
        #     ar = PL.get(key)
        #     for i in range(ar.shape[0]):
        #         for j in range(1, ar.shape[1]):
        #             if ar[i, j] == 1:
        #                 energy_type = f'Источник электронов №{key} из {j}го в {i}й'
        #                 name = f'Flu_e_{key}_{j}{i}'
        #                 self.output_dictionary_flu(name, energy_type)
        #                 source_number += 1
        #
        #                 lay_label = tk.Label(self.source_labels, text=f'{name}')
        #                 lay_label.grid(row=7 + self.label_num, column=3)
        #                 self.layers_label_list.append(lay_label)
        #                 self.label_num += 1
        #
        #     if ar[:, 0].any() == 1:
        #         mb.showinfo('ERROR', 'Частицы в нулевом слое!')

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

        # построение графиков
        if self.graph_frame_exist == 1:
            self.graph_fr.destroy()

        self.graph_fr = tk.LabelFrame(self, text='График', width=30)
        self.graph_fr.grid(row=0, column=4, padx=10, pady=10, rowspan=10, columnspan=20, sticky='N')
        self.graph_painter(time_count, func_out, self.graph_fr)
        self.graph_frame_exist = 1

    def output_dictionary_current(self, name=None, energy_type=None):
        self.name = name
        self.energy_type = energy_type

        if self.name is None or self.energy_type is None:
            print('В current не прописан тип частиц')
            return

        file_name = f'time functions/time_{self.name}.tf'
        np.savetxt(f'{self.path}/time functions/time_{self.name}.tf', self.output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_{self.name}.tf\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')

        time_for_dict, func_for_dict, _ = self.data_control()

        if 'Current' in self.name:  # сохранение для Current
            axes = ['x', 'y', 'z']
            distr = ['JX', 'JY', 'JZ']
            for i in range(len(axes)):
                remp_sources_dict_val = save_for_remp_form(source_type='Current'+f'_{axes[i]}',
                                                           source_name=self.name,
                                                           layer_index=self.name.split('_')[-1],
                                                           amplitude=self.koef,
                                                           time_for_dict=time_for_dict,
                                                           func_for_dict=func_for_dict,
                                                           lag_and_koord=0,
                                                           distribution=distr[i])

                remp_sourses_dict.update({f'{self.name}|| axe: {axes[i]}': remp_sources_dict_val})

        elif 'Sigma' in self.name:  # сохранение для Sigma
            remp_sources_dict_val = save_for_remp_form(source_type='Sigma',
                                                       source_name=self.name,
                                                       layer_index=self.name.split('_')[-1],
                                                       amplitude=self.koef,
                                                       time_for_dict=time_for_dict,
                                                       func_for_dict=func_for_dict,
                                                       lag_and_koord=0)

            remp_sourses_dict.update({self.name: remp_sources_dict_val})

        else:
            print('Тип источника не обнаружен Current or Sigma')
            return


        time_func_dict.update({f'{self.name}': os.path.normpath(file_name)})

        pr_dict = {}
        pr_dict.update({
            '<номер источника>': source_number,
            '<тип источника>': self.energy_type,
            '<название источника>': self.name,
            '<номер слоя>': self.name.split('_')[-1],
            '<номер слоя из>': 0,
            '<номер слоя в>': 0,
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

        delete_keys = ['<номер слоя из>',
                       '<номер слоя в>',
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
