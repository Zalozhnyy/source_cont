import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Project_reader import DataParcer
from Main_frame import FrameGen
from utility import *


class FluTab(FrameGen):

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

    def button_states(self):
        self.button_calculate.configure(state='active')

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

        self.output_dictionary_flu()

        # построение графиков
        if self.graph_frame_exist == 1:
            self.graph_fr.destroy()

        self.graph_fr = tk.LabelFrame(self, text='График', width=30)
        self.graph_fr.grid(row=0, column=4, padx=10, pady=10, rowspan=10, columnspan=20, sticky='N')
        self.graph_painter(time_count, func_out, self.graph_fr)
        self.graph_frame_exist = 1

    def output_dictionary_flu(self):

        file_name = f'time functions/time_{self.name}.tf'
        np.savetxt(f'{pr_dir()}/time functions/time_{self.name}.tf', self.output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_{self.name}.tf\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')

        layers = []
        [layers.append(i) for i in self.name]

        time_for_dict, func_for_dict,_ = self.data_control()

        remp_sources_dict_val = {'source_type': self.energy_type,
                                 'source_name': self.name,
                                 'layer_index_from': layers[-2],
                                 'layer_index_in': layers[-1],
                                 'amplitude': self.koef,
                                 'len_tf': len(time_for_dict),
                                 'time': time_for_dict,
                                 'value': func_for_dict,
                                 'lag': 0,
                                 'koord_ist': '',
                                 'distribution': None}
        remp_sourses_dict.update({self.name: remp_sources_dict_val})

        time_func_dict.update({f'{self.name}': os.path.normpath(file_name)})

        pr_dict = {}
        pr_dict.update({
            '<номер источника>': source_number,
            '<тип источника>': self.energy_type,
            '<название источника>': self.name,
            '<номер слоя>': 0,
            '<номер слоя из>': layers[-2],
            '<номер слоя в>': layers[-1],
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
