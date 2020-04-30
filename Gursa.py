import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from scipy import integrate

from Pe_source import PeSource
from Main_frame import FrameGen
from utility import *
from Project_reader import DataParcer


class Gursa(FrameGen):
    def notebooks(self):
        self._notebooks()
        self.constants_frame()
        self.gursa_frame()

        self.button_calculate.destroy()

        self.gursa_numeric = 1

        # отслеживание отрисованных источников
        path = os.path.join(self.path, check_folder(self.path).get('PAR'))
        self.max_gursa_count, numbers_convert = DataParcer(path).par_decoder()
        self.gursa_numbers = {}
        for i in numbers_convert:
            self.gursa_numbers.update({f'Gursa_{i}': False})  # Хранит отрисован ли данный источник

        self.gursa_graphs_checkbutton_val = tk.BooleanVar()
        self.gursa_graphs_checkbutton_val.set(1)
        gursa_graphs_checkbutton = tk.Checkbutton(self, text='Построение графиков',
                                                  variable=self.gursa_graphs_checkbutton_val, onvalue=1, offvalue=0)
        gursa_graphs_checkbutton.grid(row=1, column=6, columnspan=2)

    def constants_frame(self):
        self.constants_fr = tk.LabelFrame(self, text='Константы', width=20)
        self.constants_fr.grid(row=1, column=2, sticky='NWSE', padx=5, rowspan=2, columnspan=3)

        self.entry_f_val.set(1.)
        label_f = tk.Label(self.constants_fr, text='F , квант')
        label_f.grid(row=0, column=0, padx=3, sticky='E')
        entry_f = tk.Entry(self.constants_fr, width=8, textvariable=self.entry_f_val)
        entry_f.grid(row=0, column=2, padx=3)

        ###Полярные\Азимутальные углы
        self.polar_angle_val = tk.StringVar()
        self.polar_angle_val.set('0')
        tk.Label(self.constants_fr, text='Полярный угол поворота', width=25).grid(row=1, column=0, columnspan=2)
        self.polar_angle = tk.Entry(self.constants_fr, textvariable=self.polar_angle_val, width=5)
        self.polar_angle.grid(row=1, column=2, padx=3)

        self.azi_angle_val = tk.StringVar()
        self.azi_angle_val.set('0')
        tk.Label(self.constants_fr, text='Азимутальный угол поворота', width=25).grid(row=2, column=0, columnspan=2)
        self.azi_angle = tk.Entry(self.constants_fr, textvariable=self.azi_angle_val, width=5)
        self.azi_angle.grid(row=2, column=2, padx=3)
        # _________________________

    def gursa_frame(self):
        self.gursa_fr = tk.LabelFrame(self, text='Гурса')
        self.gursa_fr.grid(row=4, column=3, sticky='NE', padx=5, rowspan=10, columnspan=3)

        self.gursa_combobox = ttk.Combobox(self.gursa_fr, values=self.gursa_dict.keys(), width=10, state='disabled')
        self.gursa_combobox.grid(row=0, column=2, pady=3, padx=3)
        self.delete_gursa_class_button = tk.Button(self.gursa_fr, text='Удалить', command=self.regrid_gursa,
                                                   width=8, state='disabled')
        self.delete_gursa_class_button.grid(row=0, column=1, padx=3, pady=3)

        self.add_button_gursa = tk.Button(self.gursa_fr, text='Добавить источник', width=15, command=self.gursa_cw,
                                          state='disabled')
        self.add_button_gursa.grid(row=0, column=0, padx=3, pady=3)

    def gursa_cw(self):

        try:
            if self.gursa_numeric >= self.max_gursa_count:
                raise Exception
        except Exception:
            mb.showerror('Max limit', f'Максимальное количество источников = {self.max_gursa_count}')
            return print(f'Максимальное количество источников = {self.max_gursa_count}')

        self.x = PeSource(self.parent, name=f'Gursa_{self.gursa_numeric}')
        self.x.path = self.path
        self.x.F = float(self.entry_f_val.get())

        self.wait_window(self.x)

        if self.x.calc_state == 1:
            self.gursa_count.append(self.x)

            self.gursa_dict.update({f'{self.x.name}': self.x})

            for label in self.gursa_label_dict.values():
                label.destroy()

            for i in range(len(self.gursa_dict.keys())):
                self.gursa_label_dict.update(
                    {f'{self.gursa_count[i].name}': tk.Label(self.gursa_fr, text=f'{self.gursa_count[i].name}')})

            for i, label in enumerate(self.gursa_label_dict.values()):
                label.grid(row=1 + i, column=0, pady=3)

            keys = []
            for i in self.gursa_dict.keys():
                keys.append(i)
            self.gursa_combobox.configure(values=keys)

            self.spectr = self.x.Spektr_output

            self.calculate_gursa()
            self.delete_gursa_class_button.configure(state='active')
            self.gursa_combobox.configure(state='active')

            if self.x.spectr_type.get() == 1:
                type = 'DISCRETE'
                np.savetxt(f'{self.path}/time functions/Gursa/Spektr_output_{self.x.name}.txt',
                           self.x.Spektr_output, fmt='%-6.3g', header='SP_TYPE={}\n[DATA]'.format(type),
                           comments='', delimiter='\t')

                self.Spektr_output_2 = np.copy(self.x.Spektr_output)
                for i in range(self.Spektr_output_2.shape[0]):
                    if self.Spektr_output_2[i, 0] >= 100:
                        self.Spektr_output_2[i, 0] = self.Spektr_output_2[i, 0] / 2
                self.Spektr_output_2[:, 0] = self.x.Spektr_output[:, 0] * 10 ** -3
                self.Spektr_output_2 = np.insert(self.Spektr_output_2, 1, np.zeros(self.Spektr_output_2.shape[0]
                                                                                   , dtype=int), axis=1)
                self.Spektr_output_2 = np.insert(self.Spektr_output_2, 1, np.zeros(self.Spektr_output_2.shape[0]
                                                                                   , dtype=int), axis=1)

                np.savetxt(f'{self.path}/time functions/Gursa/IL_{self.x.name}.txt', self.Spektr_output_2,
                           fmt='%-6.3g', comments='', delimiter='\t',
                           header='Пример фиксированного спектра\n'
                                  'Номер спектра (номер частицы)\n'
                                  f'{self.gursa_numeric}\n'
                                  f'Мощность спектра (шт). Пользователь задает его задает.\n'
                                  f'{self.x.F}\n'
                                  f'Тип спектра\n'
                                  f'0\n'
                                  f'Число частиц (количество энергий в спектре)\n'
                                  f'{self.x.Spektr_output.shape[0]}\n'
                                  f'Количество запусков одинаковых частиц\n'
                                  f'1\n'
                                  f'Количество элементов в таблице(ниже)\n'
                                  f'{self.x.Spektr_output.shape[0]}\n'
                                  f'№,  Энергия (MeВ), TETA(град.), FI(град.), Доля')

            elif self.x.spectr_type.get() == 0:
                type = 'CONTINUOUS'
                np.savetxt(
                    f'{self.path}/time functions/Gursa/Spektr_output_{self.x.name}.txt',
                    self.x.Spektr_output, fmt='%-6.3g', comments='', delimiter='\t',
                    header='SP_TYPE={}\n[DATA]\n{:.2g}'.format(type, self.x.spectr_cont[0, 0]))

                out_sp = np.copy(self.x.Spektr_output)
                for i in range(out_sp.shape[0]):
                    if out_sp[i, 0] >= 100:
                        out_sp[i, 0] = out_sp[i, 0] / 2
                out_sp[:, 0] = self.x.spectr_cont_half[:] * 10 ** -3
                out_sp = np.insert(out_sp, 1, np.zeros(out_sp.shape[0], dtype=int), axis=1)
                out_sp = np.insert(out_sp, 1, np.zeros(out_sp.shape[0], dtype=int), axis=1)

                np.savetxt(f'{self.path}/time functions/Gursa/IL_{self.x.name}.txt', out_sp,
                           fmt='%-6.3g', comments='', delimiter='\t',
                           header='Пример фиксированного спектра\n'
                                  'Номер спектра (номер частицы)\n'
                                  f'{self.gursa_numeric}\n'
                                  f'Мощность спектра (шт). Пользователь задает его задает.\n'
                                  f'{self.x.F}\n'
                                  f'Тип спектра\n'
                                  f'0\n'
                                  f'Число частиц (количество энергий в спектре)\n'
                                  f'{out_sp.shape[0]}\n'
                                  f'Количество запусков одинаковых частиц\n'
                                  f'1\n'
                                  f'Количество элементов в таблице(ниже)\n'
                                  f'{out_sp.shape[0]}\n'
                                  f'№,  Энергия (MeВ), TETA(град.), FI(град.), Доля')

            self.gursa_numeric += 1

            time_func_dict.update({f'{self.x.name}': [f'time functions/Gursa/time_{self.x.name}.tf',
                                                      f'time functions/Gursa/Spektr_output_{self.x.name}.txt']})

            self.output_dictionary_gursa()

    def calculate_gursa(self):
        func_out, time_count = self.interpolate_user_time()
        func_out = np.array(func_out)
        time_count = np.array(time_count)
        output_matrix = np.column_stack((time_count, func_out))

        # integrate
        E_cp = np.sum(self.spectr[:, 0] * self.spectr[:, 1]) / np.sum(self.spectr[:, 1])

        F = float(self.entry_f_val.get())
        intergal_tf = integrate.simps(y=output_matrix[:, 1], x=output_matrix[:, 0], dx=output_matrix[:, 0])

        # self.koef = F / (0.23 * E_cp * intergal_tf * 1e3 * 1.6e-19)
        self.koef = F / intergal_tf

        file_name = f'time functions/Gursa/time_{self.x.name}.tf'
        # np.savetxt(f'{pr_dir()}/time functions/Gursa/time_{self.x.name}.tf', output_matrix, fmt='%-8.4g',
        #            header=f'1 pechs\n{time_count[0]} {time_count[-1]} {koef}\n{len(time_count)}', delimiter='\t',
        #            comments='')
        np.savetxt(f'{self.path}/time functions/Gursa/time_{self.x.name}.tf', output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_{self.x.name}.tf\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')

        if self.gursa_graphs_checkbutton_val.get() is True:
            # построение графиков
            if self.graph_frame_exist == 1:
                self.graph_fr.destroy()

            self.graph_fr = tk.LabelFrame(self, text='График', width=30)
            self.graph_fr.grid(row=2, column=6, padx=10, pady=10, rowspan=15, columnspan=10, sticky='N')
            self.graph_painter(time_count, func_out, self.graph_fr, dpi=70)
            self.graph_frame_exist = 1

            figure1 = plt.Figure(figsize=(6, 4), dpi=70)
            ax = figure1.add_subplot(111)
            ax.semilogy(self.x.pe_source_graph[:, 0], self.x.pe_source_graph[:, 1])

            ax.set_xlabel('Radius between objects, km', fontsize=12)
            ax.set_ylabel('Energy part', fontsize=12)
            chart_type = FigureCanvasTkAgg(figure1, self.graph_fr)

            chart_type.get_tk_widget().grid(row=5, column=0, padx=5, pady=5, sticky='N')
            ax.set_title('Photon flux, $\mathdefault{1/cm^{2}}$')
            ax.legend()
            self.graph_frame_exist = 1

    def regrid_gursa(self):

        for i, ob in enumerate(source_list):
            if ob.get('< название источника >') == self.gursa_combobox.get():
                mb.showinfo('work', 'work')
                source_list.pop(i)

        self.gursa_label_dict.get(self.gursa_combobox.get()).grid_forget()

        self.gursa_dict.pop(self.gursa_combobox.get())
        time_func_dict.pop(self.gursa_combobox.get())

        self.gursa_label_dict.pop(self.gursa_combobox.get())

        self.gursa_count.clear()
        for val in self.gursa_dict.values():
            self.gursa_count.append(val)

        for i, label in enumerate(self.gursa_label_dict.values()):
            # print(label)
            label.grid_configure(row=1 + i)

        keys = []
        for i in self.gursa_dict.keys():
            keys.append(i)
        self.gursa_combobox.configure(values=keys)

        self.gursa_numeric -= 1

    def button_states(self):
        self.add_button_gursa.configure(state='active')

    def local_get(self):
        self.get()
        self.button_states()

    def local_get_row(self):
        self.row_get()
        self.button_states()

    def output_dictionary_gursa(self):
        class_gursa = self.x
        # for class_gursa in self.gursa_dict.values():

        time_for_dict, func_for_dict, _ = self.data_control()

        remp_sources_dict_val = save_for_remp_form(source_type='Gursa',
                                                   source_name=class_gursa.name,
                                                   amplitude=self.koef,
                                                   time_for_dict=time_for_dict,
                                                   func_for_dict=func_for_dict,
                                                   lag_and_koord=0,
                                                   spectre=class_gursa.spectr_directory)

        remp_sourses_dict.update({class_gursa.name: remp_sources_dict_val})

        # pr_dict = {}
        # pr_dict.update({
        #     '<номер источника>': source_number,
        #     '<тип источника>': 'Gursa',
        #     '<название источника>': class_gursa.name,
        #     '<номер слоя>': 0,
        #     '<номер слоя из>': 0,
        #     '<номер слоя в>': 0,
        #     '<амплитуда источинка в ближней зоне источника>': self.koef,
        #     '<амплитуда источинка в дальней зоне источника>': 0,
        #     '<спектр источника>': time_func_dict.get(f'{class_gursa.name}')[1],
        #     '<временная функция источинка>': time_func_dict.get(f'{class_gursa.name}')[0],
        #     '<запаздывание(0 - нет, 1 - есть)>': 0,
        #     '<X-координата источника>': class_gursa.M2[0],
        #     '<Y-координата источника>': class_gursa.M2[1],
        #     '<Z-координата источника>': class_gursa.M2[2],
        #     '<X-координата объекта>': class_gursa.M1[0],
        #     '<Y-координата объекта>': class_gursa.M1[1],
        #     '<Z-координата объекта>': class_gursa.M1[2],
        #     '<полярный угол поворта локальной системы координат относительно глобальной>': eval(
        #         self.polar_angle_val.get()),
        #     '<азимутальный угол поворта локальной системы координат относительно глобальной>': eval(
        #         self.azi_angle_val.get()),
        #     '<X-компонента направляющего косинуса для расчета в дальней зоне>': None,
        #     '<Y-компонента направляющего косинуса для расчета в дальней зоне>': None,
        #     '<Z-компонента направляющего косинуса для расчета в дальней зоне>': None
        # })
        #
        # delete_keys = ['<номер слоя>',
        #                '<номер слоя из>',
        #                '<номер слоя в>',
        #                '<X-компонента направляющего косинуса для расчета в дальней зоне>',
        #                '<Y-компонента направляющего косинуса для расчета в дальней зоне>',
        #                '<Z-компонента направляющего косинуса для расчета в дальней зоне>',
        #                '<амплитуда источинка в дальней зоне источника>'
        #                ]
        #
        # for key in delete_keys:
        #     if key in pr_dict.keys():
        #         pr_dict.pop(key)
        #
        # source_list.append(pr_dict)
