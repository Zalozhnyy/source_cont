import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Pe_source import PeSource
from Main_frame import FrameGen
from utility import pr_dir, source_number, time_func_dict, source_list


class Gursa(FrameGen):
    def notebooks(self):
        self._notebooks()

        self.button_read_gen = tk.Button(self, width=10, text='Read',
                                         command=lambda: (self.get(), self.button_states()),
                                         state='disabled')
        self.button_read_gen.grid(row=6, column=2)

        self.add_button_gursa = tk.Button(self, text='Add source', width=10, command=self.gursa_cw,
                                          state='disabled')
        self.add_button_gursa.grid(row=10, column=2)

        self.gursa_graphs_checkbutton_val = tk.BooleanVar()
        self.gursa_graphs_checkbutton_val.set(0)
        gursa_graphs_checkbutton = tk.Checkbutton(self, text='Построение графиков',
                                                  variable=self.gursa_graphs_checkbutton_val, onvalue=1, offvalue=0)
        gursa_graphs_checkbutton.grid(row=1, column=7, columnspan=2)

        self.gursa_combobox = ttk.Combobox(self, values=self.gursa_dict.keys(), width=8)
        self.gursa_combobox.grid(row=10, column=4)
        self.delete_gursa_class_button = tk.Button(self, text='Delete obj', command=self.regrid_gursa, width=8)
        self.delete_gursa_class_button.grid(row=11, column=4)

        self.entry_f_val.set(1.)
        label_f = tk.Label(self, text='F')
        label_f.grid(row=2, column=5, padx=3, sticky='E')
        entry_f = tk.Entry(self, width=3, textvariable=self.entry_f_val)
        entry_f.grid(row=2, column=6, padx=3)

    def gursa_cw(self):

        self.x = PeSource(self.parent, name=f'Gursa_{self.gursa_numeric}')
        self.x.F = float(self.entry_f_val.get())

        self.wait_window(self.x)

        if self.x.calc_state == 1:
            self.gursa_count.append(self.x)

            self.gursa_dict.update({f'{self.x.name}': self.x})

            for label in self.gursa_label_dict.values():
                label.destroy()

            for i in range(len(self.gursa_dict.keys())):
                self.gursa_label_dict.update(
                    {f'{self.gursa_count[i].name}': tk.Label(self, text=f'{self.gursa_count[i].name}')})

            for i, label in enumerate(self.gursa_label_dict.values()):
                label.grid(row=12 + i, column=2)

            keys = []
            for i in self.gursa_dict.keys():
                keys.append(i)
            self.gursa_combobox.configure(values=keys)

            self.gursa_numeric += 1

            self.spectr = self.x.Spektr_output

            self.calculate_gursa()

            if self.x.spectr_type.get() == 1:
                type = 'DISCRETE'
                np.savetxt(f'{pr_dir()}/time functions/Gursa/Spektr_output_{self.x.name}.txt',
                           self.x.Spektr_output, fmt='%-6.3g', header='SP_TYPE={}\n[DATA]'.format(type),
                           comments='', delimiter='\t')

            elif self.x.spectr_type.get() == 0:
                type = 'CONTINUOUS'
                np.savetxt(
                    f'{pr_dir()}/time functions/Gursa/Spektr_output_{self.x.name}.txt',
                    self.x.Spektr_output, fmt='%-6.3g', comments='', delimiter='\t',
                    header='SP_TYPE={}\n[DATA]\n{:.2g}'.format(type, self.x.spectr_cont[0, 0]))

            time_func_dict.update({f'{self.x.name}': [f'time functions/Gursa/time_{self.x.name}.tf',
                                                      f'time functions/Gursa/Spektr_output_{self.x.name}.txt']})

            self.output_dictionary_gursa()

    def calculate_gursa(self):
        func_out, time_count = self.interpolate_user_time()
        func_out = np.array(func_out)
        time_count = np.array(time_count)
        output_matrix = np.column_stack((time_count, func_out))

        # integrate
        # E_cp = np.sum(self.spectr[:, 0] * self.spectr[:, 1]) / np.sum(self.spectr[:, 1])

        F = float(self.entry_f_val.get())
        # intergal_tf = integrate.simps(y=output_matrix[:, 1], x=output_matrix[:, 0], dx=output_matrix[:, 0])

        # koef = F / (0.23 * E_cp * intergal_tf * 1e3 * 1.6e-19)

        file_name = f'time functions/Gursa/time_{self.x.name}.tf'
        # np.savetxt(f'{pr_dir()}/time functions/Gursa/time_{self.x.name}.tf', output_matrix, fmt='%-8.4g',
        #            header=f'1 pechs\n{time_count[0]} {time_count[-1]} {koef}\n{len(time_count)}', delimiter='\t',
        #            comments='')
        np.savetxt(f'{pr_dir()}/time functions/Gursa/time_{self.x.name}.tf', output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_{self.x.name}.tf\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')

        if self.gursa_graphs_checkbutton_val.get() is True:
            figure = plt.Figure(figsize=(8, 4.5), dpi=65)
            ax = figure.add_subplot(111)
            ax.plot(time_count, func_out, label='Пользовательская функция')

            ax.set_xlabel('Time , s', fontsize=12)
            ax.set_ylabel('Function', fontsize=12)
            chart_type = FigureCanvasTkAgg(figure, self)

            chart_type.get_tk_widget().grid(row=2, column=8, rowspan=15, columnspan=30, padx=10)
            ax.set_title(f'{self.x.name}')
            ax.legend()

            figure1 = plt.Figure(figsize=(8, 4.5), dpi=65)
            ax = figure1.add_subplot(111)
            ax.semilogy(self.x.pe_source_graph[:, 0], self.x.pe_source_graph[:, 1])

            ax.set_xlabel('Radius between objects, km', fontsize=12)
            ax.set_ylabel('Energy part', fontsize=12)
            chart_type = FigureCanvasTkAgg(figure1, self)

            chart_type.get_tk_widget().grid(row=17, column=8, rowspan=15, columnspan=30, padx=10, pady=10)
            ax.set_title('Photon flux, $\mathdefault{1/cm^{2}}$')
            ax.legend()

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
            label.grid_configure(row=12 + i)

        keys = []
        for i in self.gursa_dict.keys():
            keys.append(i)
        self.gursa_combobox.configure(values=keys)

    def button_states(self):
        self.button_generate.configure(state='disabled')
        self.entry_generate_value.configure(state='disabled')
        self.button_save.configure(state='active')
        self.button_save_def.configure(state='active')
        self.button_browse.configure(state='disabled')
        self.add_button_gursa.configure(state='active')

    def output_dictionary_gursa(self):
        class_gursa = self.x
        # for class_gursa in self.gursa_dict.values():

        pr_dict = {}
        pr_dict.update({
            '<номер источника>': source_number,
            '<тип источника>': 'Gursa',
            '<название источника>': class_gursa.name,
            '<номер слоя>': 0,
            '<номер слоя из>': 0,
            '<номер слоя в>': 0,
            '<амплитуда источинка в ближней зоне источника>': class_gursa.F,
            '<амплитуда источинка в дальней зоне источника>': 0,
            '<спектр источника>': time_func_dict.get(f'{class_gursa.name}')[1],
            '<временная функция источинка>': time_func_dict.get(f'{class_gursa.name}')[0],
            '<запаздывание(0 - нет, 1 - есть)>': 0,
            '<X-координата источника>': class_gursa.M2[0],
            '<Y-координата источника>': class_gursa.M2[1],
            '<Z-координата источника>': class_gursa.M2[2],
            '<X-координата объекта>': class_gursa.M1[0],
            '<Y-координата объекта>': class_gursa.M1[1],
            '<Z-координата объекта>': class_gursa.M1[2],
            '<полярный угол поворта локальной системы координат относительно глобальной>': None,
            '<азимутальный угол поворта локальной системы координат относительно глобальной>': None,
            '<X-компонента направляющего косинуса для расчета в дальней зоне>': None,
            '<Y-компонента направляющего косинуса для расчета в дальней зоне>': None,
            '<Z-компонента направляющего косинуса для расчета в дальней зоне>': None
        })

        delete_keys = ['<номер слоя>',
                       '<номер слоя из>',
                       '<номер слоя в>',
                       '<полярный угол поворта локальной системы координат относительно глобальной>',
                       '<азимутальный угол поворта локальной системы координат относительно глобальной>',
                       '<полярный угол поворта локальной системы координат относительно глобальной>',
                       '<X-компонента направляющего косинуса для расчета в дальней зоне>',
                       '<Y-компонента направляющего косинуса для расчета в дальней зоне>',
                       '<Z-компонента направляющего косинуса для расчета в дальней зоне>',
                       '<амплитуда источинка в дальней зоне источника>'
                       ]

        for key in delete_keys:
            if key in pr_dict.keys():
                pr_dict.pop(key)

        source_list.append(pr_dict)
