import os
import sys

sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter import simpledialog
import numpy as np
from scipy import integrate

from source_Project_reader import DataParser
from source_Spectre_one_interface import SpectreOneInterface, ScrolledWidget


class SpectreConfigure(tk.Frame):
    def __init__(self, path='', parent=None):
        super().__init__(parent)

        self.path = path
        self.parent = parent

        self.parent.title('Редактор спектра')

        self.spectre_frame = None
        self.spectre_path = ''

        self.spectre_entry_val = []
        self.spectre_entry = []

        self.spectre_frame = None
        self.frame_description = None

        self.spectre_type_cb = None
        self.sp_type_dict = {'Фиксированный': 'SP_0',
                             'Разыгрывание': 'SP_1',
                             'Упрощённый перенос ИИ': 'SP_5',
                             'Граничный': 'SP_2',
                             'Дискретный': 'DISCRETE',
                             'Непрерывный': 'CONTINUOUS'}

        self._sp_zero_form = ['Пример фиксированного спектра',
                              'Номер спектра',
                              '1',
                              'Мощность спектра (шт/см\u00b2/с)- для поверхностных, (шт/см\u00b3/с)- для объемных',
                              '',
                              'Тип спектра (0-фиксированный, 1-разыгрывание, 3-от координат, 4-от времени, 5-с учетом ослабления)',
                              '0',
                              'Число частиц (запускаемых на каждом шаге) Np=Nзап*Nэл',
                              '',
                              'Количество запусков одинаковых частиц (1-без повторных запусков)',
                              '1',
                              'Количество элементов в таблице(ниже)',
                              '',
                              'Таблица частиц  ( №,  Энергия (MeВ), TETA(град.), FI(град.), Доля(не нормируется))']

        self.lines = []

        self.sp_one_interface = None

        self.data_struct = None

        self.delete_buttons = []

        self.constructor()

    def pechs_check(self):

        find_mat_air = False

        # for name in pech_names:
        if os.path.exists(os.path.join(self.path, r'materials\mat-air')):
            self.mat_air_path = os.path.join(self.path, r'materials\mat-air')
            self.mat_air_path = os.path.normpath(self.mat_air_path)
            print(f'Mat_air обнаружен в {self.mat_air_path}')
            find_mat_air = True

        if find_mat_air is False:
            mb.showinfo('Перенос', 'Папка materials/mat_air не обнаружена.\nВыберите папку mat_air')
            self.mat_air_path = fd.askdirectory(title='Выберите папку materials', initialdir=self.path)
            print(f'mat_air обнаружен в {self.mat_air_path}')
            if self.mat_air_path == '':
                return 0

        photon_path = os.path.join(self.mat_air_path, r'photon\xtbl.23')
        if not os.path.exists(photon_path):
            mb.showerror('PATH', f'Файл xtbl.23 не был найден в дирекории {os.path.normpath(photon_path)}\n'
                                 f'Укажите путь к файлу напрямую')

            photon_path = fd.askopenfilename(title='Выберите файл xtbl.23 для фотонов', initialdir=self.path)
            if photon_path == '':
                return 0

        self.photon_table = np.loadtxt(photon_path, skiprows=18)
        self.photon_table = 10 ** self.photon_table
        a = np.column_stack((self.photon_table[:, 0], self.photon_table[:, 1]))
        # print(a)
        #
        # plt.plot(self.photon_table[:, 0], self.photon_table[:, 1])
        # plt.show()

        return 1

    def constructor(self):
        self.button_open_spectre = tk.Button(self, text='Выбрать спектр', command=self.open_spectre, width=13)
        self.button_open_spectre.grid(row=0, column=0, padx=3, pady=3, sticky='WN')

        self.button_create_spectre = tk.Button(self, text='Создать спектр', command=self.create_spectre, width=13)
        self.button_create_spectre.grid(row=0, column=1, padx=3, pady=3, sticky='WN')

        self.save_button = tk.Button(self, text='Сохранить', command=lambda: self._save_data(False), width=13,
                                     state='disabled')
        self.save_button.grid(row=2, column=0, pady=3, padx=3, sticky='WN')
        self.save_as_button = tk.Button(self, text='Сохранить как', command=lambda: self._save_data(True), width=13,
                                        state='disabled')
        self.save_as_button.grid(row=2, column=1, pady=3, padx=3, sticky='WN')

        self.spectre_type_combobox_values = ['Фиксированный',
                                             'Разыгрывание',
                                             'Граничный',
                                             'Упрощённый перенос ИИ',
                                             'Дискретный',
                                             'Непрерывный']
        self.spetre_type_cobbobox = ttk.Combobox(self, value=[val for val in self.spectre_type_combobox_values],
                                                 width=25,
                                                 state='readonly')
        self.spetre_type_cobbobox.grid(row=0, column=3, padx=5)
        self.spetre_type_cobbobox.set('Тип спектра')

        # self.bind_class(self.spetre_type_cobbobox, "<<ComboboxSelected>>", self.__cb_react)

    def open_spectre(self, use_constructor=True, use_chose_spectre=None):
        if use_chose_spectre is None:
            self.spectre_path = fd.askopenfilename(title='Выберите файл spectre', initialdir=self.path,
                                                   filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
            if self.spectre_path == '':
                return
        else:
            self.spectre_path = use_chose_spectre

        self.save_button['state'] = 'normal'
        self.save_as_button['state'] = 'normal'

        self.__destroy_frames()

        with open(self.spectre_path, 'r') as file:
            lines = file.readlines()

        if use_constructor is False:
            self.spectre_number_data = int(lines[2])
            return self.spectre_number_data, self.spectre_path

        try:
            if 'SP_TYPE=CONTINUOUS' in lines[0]:

                self.spectre_type_cb = 'CONTINUOUS'
                self.spetre_type_cobbobox.set('CONTINUOUS')

                labels = ['Энергия (кеВ)', 'Доля(не нормируется)']

                self.data_struct = SpectreDataStructure(self.spectre_path)
                self.data_struct.spectre_type_identifier()

                self.description_discrete_cont()

                self.rows_count_val.set(str(self.data_struct.data.shape[0]))

                self.spectre_frame_constructor(labels, 'CONTINUOUS')

            elif 'SP_TYPE=DISCRETE' in lines[0]:

                self.spectre_type_cb = 'DISCRETE'
                self.spetre_type_cobbobox.set('DISCRETE')

                labels = ['Энергия (кеВ)', 'Доля(не нормируется)']

                self.data_struct = SpectreDataStructure(self.spectre_path)
                self.data_struct.spectre_type_identifier()

                self.description_discrete_cont()

                self.rows_count_val.set(str(self.data_struct.data.shape[0]))

                self.spectre_frame_constructor(labels, 'DISCRETE')

            elif 'Номер спектра' in lines[1] and lines[6].strip() == '0':
                self.spectre_type_cb = 'SP_0'
                self.spetre_type_cobbobox.set('Фиксированный')

                self.data_struct = SpectreDataStructure(self.spectre_path)
                self.data_struct.spectre_type_identifier()
                self.description_sp_zero()

                self.from_data_struct_to_interface()

                labels = ['№', 'Энергия (MеВ)', 'TETA(град.)', 'FI(град.)', 'Доля(не нормируется)']
                self.spectre_frame_constructor(labels, 'SP_0')
                # self.rows_count_val.trace('w', lambda name, index, mode: self.__creator('SP_0', labels, 5))

            elif 'Номер спектра' in lines[1] and lines[6].strip() == '5':
                check = self.pechs_check()
                if check == 0:
                    return

                self.elph = DataParser(self.path).elph_reader()
                self.spectre_type_cb = 'SP_5'
                self.spetre_type_cobbobox.set('Упрощённый перенос ИИ')

                self.data_struct = SpectreDataStructure(self.spectre_path)
                self.data_struct.spectre_type_identifier()
                self.description_sp_zero()

                self.from_data_struct_to_interface()

                if self.data_struct.sp_5_type == 1:
                    labels = ['№', 'Эн. фотона (MeВ) от', 'Эн. фотона (MeВ) до', 'Средняя эн. фотона (MeВ)',
                              'Доля(не нормируется)',
                              'Сечение см\u00b2/г',
                              'Энергия электрона (MeВ)']
                elif self.data_struct.sp_5_type == 0:
                    labels = ['№', 'Энергия фотона (MeВ)', 'Доля(не нормируется)', 'Сечение см\u00b2/г',
                              'Энергия электрона (MeВ)']

                else:
                    return

                self.spectre_frame_constructor(labels, 'SP_5')

            elif 'Номер спектра' in lines[1] and lines[6].strip() == '1':
                self.spectre_type_cb = 'SP_1'
                self.spetre_type_cobbobox.set('Разыгрывание')

                self.sp_one_interface = SpectreOneInterface(self.parent, self.spectre_path)
                self.sp_one_interface.data_load()

                self.sp_one_interface.grid(row=3, column=0, columnspan=12, rowspan=60, sticky="W", padx=10)

            elif 'Номер спектра' in lines[1] and lines[6].strip() == '2':
                self.spectre_type_cb = 'SP_2'
                self.spetre_type_cobbobox.set('Граничный')

                self.data_struct = SpectreDataStructure(self.spectre_path)
                self.data_struct.spectre_type_identifier()
                self.description_sp_zero()

                self.from_data_struct_to_interface()

                labels = ['№', 'Энергия (MеВ)', 'Доля(не нормируется)']
                self.spectre_frame_constructor(labels, 'SP_2')

            else:
                raise Exception

        except IndexError:
            print('Файл не похож на спектр')
            self.open_notepad_with_chosen_file()
        except:
            print('Тип спектра не распознан или структура нарушена.')
            self.open_notepad_with_chosen_file()

        try:
            self.__starts_count_change()
        except:
            pass

    def open_notepad_with_chosen_file(self):
        f = self.spectre_path
        osCommandString = f"notepad.exe {f}"
        os.system(osCommandString)
        self.parent.destroy()

    def create_spectre(self):
        self.__cb_react()

        if self.spectre_type_cb is None:
            print('Выберите тип создаваемого спектра')
            return

        self.__destroy_frames()
        self.save_as_button['state'] = 'normal'

        self.save_button['state'] = 'disabled'
        self.spectre_path = ''

        if type(self.lines) is list:
            self.lines.clear()

        if self.spectre_type_cb == 'SP_0':
            self.data_struct = SpectreDataStructure()
            self.data_struct.spectre_type = 0

            self.description_sp_zero()

        if self.spectre_type_cb == 'SP_5':
            check = self.pechs_check()
            if check == 0:
                return

            self.elph = DataParser(self.path).elph_reader()
            self.data_struct = SpectreDataStructure()
            self.data_struct.spectre_type = 5

            self.description_sp_zero()

        if self.spectre_type_cb == 'SP_1':
            self.sp_one_interface = SpectreOneInterface(self.parent, self.spectre_path)
            self.sp_one_interface.sp_one_constructor()

            self.sp_one_interface.grid(row=3, column=0, columnspan=12, rowspan=60, sticky="W", padx=10)

        if self.spectre_type_cb == 'SP_2':
            self.data_struct = SpectreDataStructure()
            self.data_struct.spectre_type = 2

            self.description_sp_zero()

        if self.spectre_type_cb == 'DISCRETE':
            self.data_struct = SpectreDataStructure()
            self.data_struct.spectre_type = 'DISCRETE'

            self.description_discrete_cont()

        if self.spectre_type_cb == 'CONTINUOUS':
            self.data_struct = SpectreDataStructure()
            self.data_struct.spectre_type = 'CONTINUOUS'

            self.description_discrete_cont()

        try:
            self.__starts_count_change()
        except:
            pass

    def description_sp_zero(self):

        sp_t = {'SP_0': '0',
                'SP_5': '5',
                'SP_2': '2'}

        row = 0

        self.cf = ScrolledWidget(self, (850, 600))
        self.cf.grid(row=3, columnspan=50, pady=5, sticky="NWSE", rowspan=100)

        self.frame_description = tk.Frame(self.cf.frame)
        self.frame_description.grid(row=3, column=0, sticky="W", padx=10)

        # create 5 sp from perenos spectre
        if self.spectre_type_cb == 'SP_5':
            self.create_from_perenos_button = tk.Button(self.frame_description,
                                                        text='Преобразовать из спектра переноса',
                                                        command=self.perenos_to_five_spectre)
            self.create_from_perenos_button.grid(row=row, column=0, columnspan=12, sticky='NW')

            self.create_to_perenos_button = tk.Button(self.frame_description,
                                                      text='Преобразовать в спектр переноса',
                                                      command=self.five_spectre_to_perenos)
            self.create_to_perenos_button.grid(row=row, column=6, columnspan=12, sticky='NW')
            row += 1

        # commentary
        commentary_label = tk.Label(self.frame_description, text='Комментарий', justify='left')
        commentary_label.grid(row=row, column=0, columnspan=12, sticky='NW')
        row += 1

        self.spectre_note_val = tk.StringVar()
        self.spectre_note_val.set('')
        self.spectre_note = tk.Entry(self.frame_description, textvariable=self.spectre_note_val, width=80)
        self.spectre_note.grid(row=row, column=0, columnspan=12, sticky='NW')
        row += 1

        # number
        num_label = tk.Label(self.frame_description, text='Номер спектра', justify='left')
        num_label.grid(row=row, column=0, columnspan=12, sticky='NW')
        row += 1

        self.spectre_number_exception = tk.Label(self.frame_description, text='Введите целочисленое значение')
        self.spectre_number_exception.grid(row=row, column=2, columnspan=6, sticky='NW')
        self.spectre_number_exception.grid_remove()

        self.spectre_number_val = tk.StringVar()

        self.spectre_number = tk.Entry(self.frame_description, textvariable=self.spectre_number_val, width=10)
        self.spectre_number.grid(row=row, column=0, columnspan=2, sticky='NW')

        self.spectre_number_val.trace('w', lambda name, index, mode: self._data_validation([int],
                                                                                           self.spectre_number_val,
                                                                                           self.spectre_number,
                                                                                           self.spectre_number_exception))
        self.spectre_number_val.set('')

        row += 1

        if self.spectre_type_cb != 'SP_5':
            # Power
            p_t = 'Мощность спектра (шт/см\u00b2/с)- для поверхностных, (шт/см\u00b3/с)- для объемных'
            power_label = tk.Label(self.frame_description, text=p_t, justify='left')
            power_label.grid(row=row, column=0, columnspan=12, sticky='NW')
            row += 1

            self.spectre_power_exception = tk.Label(self.frame_description, text='Введите значение')
            self.spectre_power_exception.grid(row=row, column=2, columnspan=6, sticky='NW')
            self.spectre_power_exception.grid_remove()

            self.spectre_power_val = tk.StringVar()
            self.spectre_power = tk.Entry(self.frame_description, textvariable=self.spectre_power_val, width=10)
            self.spectre_power.grid(row=row, column=0, columnspan=2, sticky='NW')

            self.spectre_power_val.trace('w', lambda name, index, mode: self._data_validation([int, float],
                                                                                              self.spectre_power_val,
                                                                                              self.spectre_power,
                                                                                              self.spectre_power_exception))
            self.spectre_power_val.set('1')

            row += 1

        self.spectre_type_val = tk.StringVar()
        self.spectre_type_val.set(sp_t[self.spectre_type_cb])

        p = 'Число частиц (запускаемых на каждом шаге)'
        pcount_label = tk.Label(self.frame_description, text=p, justify='left')
        pcount_label.grid(row=row, column=0, columnspan=12, sticky='NW')
        row += 1

        self.rows_count_calc = tk.Label(self.frame_description, text='1', justify='left')
        self.rows_count_calc.grid(row=row, column=0, columnspan=12, sticky='NW')
        row += 1

        # Одинаковые частицы
        p = 'Количество запусков одинаковых частиц (1-без повторных запусков)'
        ag_label = tk.Label(self.frame_description, text=p, justify='left')
        ag_label.grid(row=row, column=0, columnspan=12, sticky='NW')
        row += 1

        self.starts_count_exception = tk.Label(self.frame_description, text='Введите целочисленое значение')
        self.starts_count_exception.grid(row=row, column=2, columnspan=6, sticky='NW')
        self.starts_count_exception.grid_remove()

        self.starts_count_val = tk.StringVar()
        self.starts_count_val.trace('w', lambda name, index, mode: self.__starts_count_change())

        self.starts_count = tk.Entry(self.frame_description, textvariable=self.starts_count_val, width=10)
        self.starts_count.grid(row=row, column=0, columnspan=2, sticky='NW')

        self.starts_count_val.trace('w', lambda name, index, mode: self._data_validation([int],
                                                                                         self.starts_count_val,
                                                                                         self.starts_count,
                                                                                         self.starts_count_exception))

        self.starts_count_val.set('1')

        row += 1

        if self.spectre_type_cb == 'SP_2':
            p = 'Вектор направления (x, y, z).  Значения вводить через пробел.'
            ag_label = tk.Label(self.frame_description, text=p, justify='left')
            ag_label.grid(row=row, column=0, columnspan=12, sticky='NW')
            row += 1

            self.direction_vector_result = tk.Label(self.frame_description, text='Длина вектора = ')
            self.direction_vector_result.grid(row=row, column=4, columnspan=8, sticky='NW')

            self.direction_vector_val = tk.StringVar()
            self.direction_vector_val.trace('w', lambda name, index, mode: self.__direction_vector_calc())
            self.direction_vector = tk.Entry(self.frame_description, textvariable=self.direction_vector_val, width=25)
            self.direction_vector.grid(row=row, column=0, columnspan=4, sticky='NW')

            self.direction_vector_val.set('1 0 0')

            row += 1

        # Количество элементов в таблице(ниже)
        p = 'Количество элементов в таблице(ниже)'
        ag_label = tk.Label(self.frame_description, text=p, justify='left')
        ag_label.grid(row=row, column=0, columnspan=12, sticky='NW')
        row += 1

        self.rows_count_val = tk.StringVar()
        self.rows_count_val.set('0')
        self.rows_count = tk.Entry(self.frame_description, textvariable=self.rows_count_val, width=10)
        self.rows_count.grid(row=row, column=0, columnspan=2, sticky='NW')
        self.rows_count.bind('<Return>', self.__creator)

        tk.Label(self.frame_description, text='Нажмите Enter для применения').grid(row=row, column=2,
                                                                                   columnspan=6, sticky='NW')
        row += 1

        if self.spectre_type_cb == 'SP_5' or self.spectre_type_cb == 'SP_2':
            # Вид спектра (0-точечный ,1-непрерывный)
            p = 'Вид спектра'
            ag_label = tk.Label(self.frame_description, text=p, justify='left')
            ag_label.grid(row=row, column=0, columnspan=12, sticky='NW')
            row += 1

            combobox_values = ['Точечный', 'Непрерывный']
            self.sp_5_combobox = ttk.Combobox(self.frame_description, value=[val for val in combobox_values],
                                              width=13,
                                              state='readonly')
            self.sp_5_combobox.grid(row=row + 1, column=0, columnspan=12, sticky='NW')
            self.sp_5_combobox.set('Точечный')

            self.bind_class(self.sp_5_combobox, "<<ComboboxSelected>>", self.__creator)

    def description_discrete_cont(self):

        self.cf = ScrolledWidget(self, (850, 600))
        self.cf.grid(row=3, columnspan=12, pady=5, sticky="NWSE", rowspan=100)

        self.frame_description = ttk.Frame(self.cf.frame)
        self.frame_description.grid(row=3, column=0, sticky="W", padx=10)

        tk.Label(self.frame_description, text='Количество элементов в таблице(ниже)').grid(row=0, column=0,
                                                                                           columnspan=12,
                                                                                           sticky='NW')

        self.rows_count_val = tk.StringVar()
        self.rows_count = tk.Entry(self.frame_description, textvariable=self.rows_count_val, width=10)
        self.rows_count.grid(row=1, column=0, columnspan=2, sticky='NW')
        tk.Label(self.frame_description, text='Нажмите Enter для применения').grid(row=1, column=2,
                                                                                   columnspan=6, sticky='NW')
        self.rows_count.bind('<Return>', self.__creator)

    def spectre_frame_constructor(self, labels, type):
        self.__destroy_sp_frame()

        self.spectre_frame = ttk.Frame(self.cf.frame)
        self.spectre_frame.grid(row=20, column=0, rowspan=10, columnspan=12, padx=10, sticky='NW')

        for i, x in enumerate(labels):
            tk.Label(self.spectre_frame, text=x).grid(row=0, column=i)

        if type == 'SP_0':
            self.data_insert_sp_zero()
        if type == 'SP_2':
            self.data_insert_sp_two()
        if type == 'SP_5':
            self.data_insert_sp_five()
        if type == 'DISCRETE':
            self.data_insert_discrete()
        if type == 'CONTINUOUS':
            self.data_insert_cont()

    def from_data_struct_to_interface(self):

        self.spectre_note_val.set(self.data_struct.description)
        self.spectre_number_val.set(str(self.data_struct.sp_number))
        self.spectre_number_val.set(str(self.data_struct.sp_number))

        if self.data_struct.spectre_type != 5:
            self.spectre_power_val.set(str(self.data_struct.sp_power))

        self.starts_count_val.set(str(self.data_struct.starts_count))

        self.rows_count_val.set(str(self.data_struct.data.shape[0]))

        if self.data_struct.spectre_type == 5:
            if self.data_struct.sp_5_type == 0:
                self.sp_5_combobox.set('Точечный')
            elif self.data_struct.sp_5_type == 1:
                self.sp_5_combobox.set('Непрерывный')

    def data_insert_sp_zero(self):
        row_count = self.data_struct.data.shape[0]
        column_count = 5

        for i in range(row_count):
            tmp_val = []
            for j in range(column_count):
                a = tk.StringVar()
                tmp_val.append(a)
            self.spectre_entry_val.append(tmp_val)

        for i in range(row_count):
            tmp_entry = []
            for j in range(column_count):
                tmp_entry.append(tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], width=15,
                                          justify='center'))
                tmp_entry[j].grid(row=1 + i, column=j)
                tmp_entry[j].bind("<FocusOut>", lambda _, a=i, b=j: self.__insert_data_to_data_struct(a, b, _))

            self.spectre_entry.append(tmp_entry)

            self.delete_buttons.append(tk.Button(self.spectre_frame, text='-',
                                                 command=lambda index=i: self.__delete_entry(index, 1,
                                                                                             column_count + 1)))
            self.delete_buttons[i].grid(row=1 + i, column=column_count + 1, sticky='W')

        self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
        self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=column_count - 1)

        for i in range(row_count):  # Нааполнение данными
            for j in range(column_count):
                if j == 4:
                    self.spectre_entry_val[i][j].trace('w',
                                                       lambda name, index, mode: self.__energy_part_callback(-1))

                self.__insert_to_interface_from_data_struct(i, j)

        [self.spectre_entry[i][0].configure(state='readonly', width=5) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][2].configure(state='normal', width=8) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][3].configure(state='normal', width=8) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][4].configure(state='normal', width=16) for i in range(len(self.spectre_entry))]

    def data_insert_sp_two(self):

        if self.sp_5_combobox.get() == 'Точечный':
            row_count = self.data_struct.data.shape[0]
            column_count = 3

            for i in range(row_count):
                tmp_val = []
                for j in range(column_count):
                    a = tk.StringVar()
                    tmp_val.append(a)
                self.spectre_entry_val.append(tmp_val)

            for i in range(row_count):
                tmp_entry = []
                for j in range(column_count):
                    tmp_entry.append(tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], width=15,
                                              justify='center'))
                    tmp_entry[j].grid(row=1 + i, column=j)
                    tmp_entry[j].bind("<FocusOut>", lambda _, a=i, b=j: self.__insert_data_to_data_struct(a, b, _))

                self.spectre_entry.append(tmp_entry)

                self.delete_buttons.append(tk.Button(self.spectre_frame, text='-',
                                                     command=lambda index=i: self.__delete_entry(index, 1,
                                                                                                 column_count + 1)))
                self.delete_buttons[i].grid(row=1 + i, column=column_count + 1, sticky='W')

            self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
            self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=column_count - 1)

            for i in range(row_count):  # Нааполнение данными
                for j in range(column_count):
                    if j == 2:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode: self.__energy_part_callback(-1))

                    self.__insert_to_interface_from_data_struct(i, j)

            [self.spectre_entry[i][0].configure(state='readonly', width=5) for i in range(len(self.spectre_entry))]
            # [self.spectre_entry[i][2].configure(state='normal', width=8) for i in range(len(self.spectre_entry))]
            # [self.spectre_entry[i][3].configure(state='normal', width=8) for i in range(len(self.spectre_entry))]

        elif self.sp_5_combobox.get() == 'Непрерывный':
            row_count = self.data_struct.data.shape[0]
            column_count = 5

            for i in range(row_count):
                tmp_val = []
                for j in range(column_count):
                    a = tk.StringVar()
                    tmp_val.append(a)
                self.spectre_entry_val.append(tmp_val)

            for i in range(row_count):
                tmp_entry = []
                for j in range(column_count):
                    tmp_entry.append(tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], width=15,
                                              justify='center'))
                    tmp_entry[j].grid(row=1 + i, column=j)
                    tmp_entry[j].bind("<FocusOut>", lambda _, a=i, b=j: self.__insert_data_to_data_struct(a, b, _))

                self.spectre_entry.append(tmp_entry)

                self.delete_buttons.append(tk.Button(self.spectre_frame, text='-',
                                                     command=lambda index=i: self.__delete_entry(index, 1,
                                                                                                 column_count + 1)))
                self.delete_buttons[i].grid(row=1 + i, column=column_count + 1, sticky='W')

            self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
            self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=column_count - 1)

            for i in range(row_count):  # Нааполнение данными
                for j in range(column_count):
                    if j == 4:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode: self.__energy_part_callback(-1))
                    if j == 2:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode, sv=(
                                                               i, j, self.spectre_entry_val[i][
                                                                   j]): self.__avg_energy_callback(
                                                               sv))
                    if j == 1:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode, sv=(
                                                               i, j, self.spectre_entry_val[i][
                                                                   j]): self.__avg_energy_callback(
                                                               sv))

                    self.__insert_to_interface_from_data_struct(i, j)

            [self.spectre_entry[i][0].configure(state='readonly', width=5) for i in range(len(self.spectre_entry))]
            # [self.spectre_entry[i][2].configure(state='normal', width=8) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][3].configure(state='disabled', width=13) for i in range(len(self.spectre_entry))]

    def data_insert_sp_five(self):
        row_count = self.data_struct.data.shape[0]

        if self.sp_5_combobox.get() == 'Точечный':
            column_count = 5

            for i in range(row_count):
                tmp_val = []
                for j in range(column_count):
                    tmp_val.append(tk.StringVar())
                self.spectre_entry_val.append(tmp_val)

            for i in range(row_count):

                tmp_entry = []
                for j in range(column_count):
                    tmp_entry.append(
                        tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], justify='center'))
                    tmp_entry[j].grid(row=1 + i, column=j)
                    tmp_entry[j].bind("<FocusOut>", lambda _, a=i, b=j: self.__insert_data_to_data_struct(a, b, _))

                self.spectre_entry.append(tmp_entry)
                self.delete_buttons.append(tk.Button(self.spectre_frame, text='-',
                                                     command=lambda index=i: self.__delete_entry(index, 1,
                                                                                                 column_count + 1)))
                self.delete_buttons[i].grid(row=1 + i, column=column_count + 1, sticky='W')

            self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
            self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=2)

            for i in range(row_count):  # Нааполнение данными
                for j in range(column_count):
                    if j == 0:
                        self.__insert_to_interface_from_data_struct(i, j)

                    if j == 1:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode, sv=(
                                                               i, j, self.spectre_entry_val[i][
                                                                   j]): self.__energy_callback_sp_five(
                                                               sv))
                        self.__insert_to_interface_from_data_struct(i, j)

                    if j == 2:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode: self.__energy_part_callback(2))
                        self.__insert_to_interface_from_data_struct(i, j)

            [self.spectre_entry[i][0].configure(state='readonly', width=5) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][1].configure(state='normal', width=13) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][2].configure(state='normal', width=13) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][3].configure(state='readonly', width=13) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][4].configure(state='readonly', width=13) for i in range(len(self.spectre_entry))]

        elif self.sp_5_combobox.get() == 'Непрерывный':
            self.cf.canvas.configure(width=950)
            column_count = 7

            for i in range(row_count):
                tmp_val = []
                for j in range(column_count):
                    tmp_val.append(tk.StringVar())
                self.spectre_entry_val.append(tmp_val)

            for i in range(row_count):

                tmp_entry = []
                for j in range(column_count):
                    tmp_entry.append(
                        tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], justify='center'))
                    tmp_entry[j].grid(row=2 + i, column=j)
                    tmp_entry[j].bind("<FocusOut>", lambda _, a=i, b=j: self.__insert_data_to_data_struct(a, b, _))

                self.spectre_entry.append(tmp_entry)
                self.delete_buttons.append(tk.Button(self.spectre_frame, text='-',
                                                     command=lambda index=i: self.__delete_entry(index, 2,
                                                                                                 column_count + 1)))
                self.delete_buttons[-1].grid(row=2 + i, column=column_count + 1, sticky='W')

            self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
            self.sum_energy_part.grid(row=len(self.spectre_entry) + 2, column=4)

            for i in range(row_count):  # Нааполнение данными
                for j in range(column_count):
                    if j == 0:
                        self.__insert_to_interface_from_data_struct(i, j)

                    if j == 1:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode, sv=(
                                                               i, j, self.spectre_entry_val[i][
                                                                   j]): self.__avg_energy_callback(
                                                               sv))
                        self.__insert_to_interface_from_data_struct(i, j)

                    if j == 2:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode, sv=(
                                                               i, j, self.spectre_entry_val[i][
                                                                   j]): self.__avg_energy_callback(
                                                               sv))
                        self.__insert_to_interface_from_data_struct(i, j)

                    if j == 3:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode, sv=(
                                                               i, j, self.spectre_entry_val[i][
                                                                   j]): self.__energy_callback_sp_five_cont(
                                                               sv))
                        self.__insert_to_interface_from_data_struct(i, j)

                    if j == 4:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode: self.__energy_part_callback(4))
                        self.__insert_to_interface_from_data_struct(i, j)

            [self.spectre_entry[i][0].configure(state='readonly', width=5) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][1].configure(state='normal', width=13) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][2].configure(state='normal', width=13) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][3].configure(state='readonly', width=13) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][4].configure(state='normal', width=13) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][5].configure(state='readonly', width=13) for i in range(len(self.spectre_entry))]
            [self.spectre_entry[i][6].configure(state='readonly', width=13) for i in range(len(self.spectre_entry))]

    def data_insert_discrete(self):
        row_count = self.data_struct.data.shape[0]
        column_count = self.data_struct.data.shape[1]

        for i in range(row_count):
            tmp_val = []
            for j in range(column_count):
                a = tk.StringVar()
                tmp_val.append(a)
            self.spectre_entry_val.append(tmp_val)

        for i in range(row_count):

            tmp_entry = []
            for j in range(column_count):
                tmp_entry.append(tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], width=20,
                                          justify='center'))
                tmp_entry[j].grid(row=1 + i, column=j, padx=5)
                tmp_entry[j].bind("<FocusOut>", lambda _, a=i, b=j: self.__insert_data_to_data_struct(a, b, _))

            self.spectre_entry.append(tmp_entry)

            self.delete_buttons.append(tk.Button(self.spectre_frame, text='-',
                                                 command=lambda index=i: self.__delete_entry(index, 1,
                                                                                             column_count + 1)))
            self.delete_buttons[i].grid(row=1 + i, column=column_count + 1, sticky='W')

        self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
        self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=column_count - 1)

        for i in range(row_count):  # Нааполнение данными
            for j in range(column_count):
                if j == column_count - 1:
                    self.spectre_entry_val[i][j].trace('w',
                                                       lambda name, index, mode: self.__energy_part_callback(-1))

                self.__insert_to_interface_from_data_struct(i, j, 'float')

    def data_insert_cont(self):
        row_count = self.data_struct.data.shape[0]
        column_count = self.data_struct.data.shape[1]

        for i in range(row_count):
            tmp_val = []
            for j in range(column_count):
                if i == 0 and j == 1:
                    continue

                a = tk.StringVar()
                tmp_val.append(a)

            self.spectre_entry_val.append(tmp_val)

        for i in range(row_count):

            tmp_entry = []
            for j in range(column_count):
                if i == 0 and j == 1:
                    continue
                tmp_entry.append(tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], width=20,
                                          justify='center'))
                tmp_entry[j].grid(row=1 + i, column=j, padx=5)
                tmp_entry[j].bind("<FocusOut>", lambda _, a=i, b=j: self.__insert_data_to_data_struct(a, b, _))

            self.spectre_entry.append(tmp_entry)
            if i > 0:
                self.delete_buttons.append(tk.Button(self.spectre_frame, text='-',
                                                     command=lambda index=i: self.__delete_entry(index, 1,
                                                                                                 column_count + 1)))
                self.delete_buttons[-1].grid(row=1 + i, column=column_count + 1, sticky='W')

        self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
        self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=column_count - 1)

        for i in range(row_count):  # Нааполнение данными
            for j in range(column_count):
                if i != 0:
                    if j == column_count - 1:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode: self.__energy_part_callback(-1))
                if i == 0 and j == 1:
                    continue

                self.__insert_to_interface_from_data_struct(i, j, 'float')

    def _save_data(self, save_as):

        all_field_correct = self._check_data_for_save()
        if all_field_correct is None:
            return

        if save_as is True:
            save_path = fd.asksaveasfilename(initialdir=self.path)
            if save_path == '':
                return
            self.spectre_path = save_path
            self.save_button['state'] = 'normal'

        elif save_as is False:
            if self.spectre_path == '':
                mb.showerror('save error', 'Воспользуйтесь кнопкой "Сохранить как"')
                return
            save_path = self.spectre_path

        if self.spectre_type_cb == 'SP_0':

            decode_number = {'SP_0': 0}

            out_header = self._sp_zero_form.copy()

            out_header[0] = self.spectre_note_val.get()
            out_header[2] = self.spectre_number_val.get()
            out_header[3] = 'Мощность спектра (шт/см**2/с)- для поверхностных, (шт/см**3/с)- для объемных'
            out_header[4] = self.spectre_power_val.get()
            out_header[6] = f'{decode_number[self.spectre_type_cb]}'
            out_header[8] = self.rows_count_calc['text']
            out_header[10] = self.starts_count_val.get()
            out_header[12] = str(len(self.spectre_entry_val))

            out_data = []
            for i, x in enumerate(self.spectre_entry_val):
                row = []
                for j in range(len(self.spectre_entry_val[i])):
                    row.append(self.spectre_entry_val[i][j].get())
                out_data.append(row)
            out_data = np.array(out_data, dtype=float)

            header = ''
            for i, x in enumerate(out_header):
                if i == len(out_header) - 1:
                    header += x
                else:
                    header += x + '\n'

            np.savetxt(save_path, out_data, comments='', header=header, delimiter='   ',
                       fmt=['%.2g', '%5.5E', '%3.3g', '%3.3g', '%5.5E'])

            mb.showinfo('Save', f'Сохранено в {os.path.normpath(save_path)}')
            self.spectre_path = save_path

        if self.spectre_type_cb == 'SP_2':
            decode_number = {'SP_5': 5,
                             'SP_2': 2}
            type_decode = {'Точечный': 0, 'Непрерывный': 1}

            out_header = self._sp_zero_form.copy()

            out_header[0] = self.spectre_note_val.get()
            out_header[2] = self.spectre_number_val.get()
            out_header[3] = 'Мощность спектра (шт/см**2/с)- для поверхностных, (шт/см**3/с)- для объемных'
            out_header[4] = self.spectre_power_val.get()
            out_header[6] = f'{decode_number[self.spectre_type_cb]}'
            out_header[8] = self.rows_count_calc['text']
            out_header[10] = self.starts_count_val.get()
            out_header[12] = str(len(self.spectre_entry_val))
            out_header.insert(13, 'Вид спектра (0-точечный ,1-непрерывный)')
            s_type = type_decode[self.sp_5_combobox.get()]
            out_header.insert(14, str(s_type))

            out_header.insert(11, 'Вектор направления (x, y, z)')
            out_header.insert(12, self.direction_vector_val.get())

            if s_type == 0:
                out_header[
                    -1] = 'Таблица частиц (' \
                          '№, ' \
                          'Энергия (MеВ), ' \
                          'Доля(не нормируется)'
            if s_type == 1:
                out_header[
                    -1] = 'Таблица частиц (' \
                          '№, ' \
                          'Энергия (MeВ) от, ' \
                          'Энергия (MeВ) до, ' \
                          'Средняя энергия (MeВ), ' \
                          'Доля(не нормируется)'

            out_data = []
            for i, x in enumerate(self.spectre_entry_val):
                row = []
                for j in range(len(self.spectre_entry_val[i])):
                    row.append(self.spectre_entry_val[i][j].get())
                out_data.append(row)
            out_data = np.array(out_data, dtype=float)

            header = ''
            for i, x in enumerate(out_header):
                if i == len(out_header) - 1:
                    header += x
                else:
                    header += x + '\n'

            if s_type == 0:
                np.savetxt(save_path, out_data, comments='', header=header, delimiter='   ',
                           fmt=['%.2g', '%5.5E', '%5.5E'])
            elif s_type == 1:
                np.savetxt(save_path, out_data, comments='', header=header, delimiter='   ',
                           fmt=['%.2g', '%5.5E', '%5.5E', '%5.5E', '%5.5E'])

            mb.showinfo('Save', f'Сохранено в {os.path.normpath(save_path)}')
            self.spectre_path = save_path

        if self.spectre_type_cb == 'SP_5':

            decode_number = {'SP_5': 5,
                             'SP_2': 2}
            type_decode = {'Точечный': 0, 'Непрерывный': 1}

            out_header = self._sp_zero_form.copy()

            out_header[0] = self.spectre_note_val.get()
            out_header[2] = self.spectre_number_val.get()
            out_header[3] = 'Мощность спектра (шт/см**2/с)- для поверхностных, (шт/см**3/с)- для объемных'
            out_header[4] = '1.0'
            out_header[6] = f'{decode_number[self.spectre_type_cb]}'
            out_header[8] = self.rows_count_calc['text']
            out_header[10] = self.starts_count_val.get()
            out_header[12] = str(len(self.spectre_entry_val))
            out_header.insert(13, 'Вид спектра (0-точечный ,1-непрерывный)')
            s_type = type_decode[self.sp_5_combobox.get()]
            out_header.insert(14, str(s_type))

            if s_type == 0:
                out_header[
                    -1] = 'Таблица частиц (№, ' \
                          'Энергия фотона (MeВ), ' \
                          'Доля(не нормируется), ' \
                          'Сечение см**2/г, ' \
                          'Энергия электрона (MeВ))'
            if s_type == 1:
                out_header[
                    -1] = 'Таблица частиц (' \
                          '№, ' \
                          'Эн. фотона (MeВ) от, ' \
                          'Эн. фотона (MeВ) до, ' \
                          'Средняя эн. фотона (MeВ), ' \
                          'Доля(не нормируется), ' \
                          'Сечение см**2/г, ' \
                          'Энергия электрона (MeВ))'

            out_data = []
            for i, x in enumerate(self.spectre_entry_val):
                row = []
                for j in range(len(self.spectre_entry_val[i])):
                    row.append(self.spectre_entry_val[i][j].get())
                out_data.append(row)
            out_data = np.array(out_data, dtype=float)

            header = ''
            for i, x in enumerate(out_header):
                if i == len(out_header) - 1:
                    header += x
                else:
                    header += x + '\n'

            if s_type == 0:
                np.savetxt(save_path, out_data, comments='', header=header, delimiter='   ',
                           fmt=['%.2g', '%5.5E', '%5.5E', '%5.5E', '%5.5E'])

            elif s_type == 1:
                np.savetxt(save_path, out_data, comments='', header=header, delimiter='   ',
                           fmt=['%.2g', '%5.5E', '%5.5E', '%5.5E', '%5.5E', '%5.5E', '%5.5E'])

            mb.showinfo('Save', f'Сохранено в {os.path.normpath(save_path)}')
            self.spectre_path = save_path

        if self.spectre_type_cb == 'CONTINUOUS':
            header = f'SP_TYPE=CONTINUOUS\n' \
                     f'[DATA]\n' \
                     f'{self.spectre_entry_val[0][0].get()}'
            out_data = []
            for i in range(1, len(self.spectre_entry_val)):
                row = []
                for j in range(len(self.spectre_entry_val[i])):
                    row.append(self.spectre_entry_val[i][j].get())
                out_data.append(row)
            out_data = np.array(out_data, dtype=float)

            np.savetxt(save_path, out_data, comments='', header=header, delimiter='   ', fmt=['%5.5E', '%5.6E'])
            mb.showinfo('Save', f'Сохранено в {os.path.normpath(save_path)}')
            self.spectre_path = save_path

        if self.spectre_type_cb == 'DISCRETE':
            header = f'SP_TYPE=DISCRETE\n' \
                     f'[DATA]'

            out_data = []
            for i in range(len(self.spectre_entry_val)):
                row = []
                for j in range(len(self.spectre_entry_val[i])):
                    row.append(self.spectre_entry_val[i][j].get())
                out_data.append(row)
            out_data = np.array(out_data, dtype=float)

            np.savetxt(save_path, out_data, comments='', header=header, delimiter='   ', fmt=['%5.5E', '%5.6E'])

        if self.spectre_type_cb == 'SP_1':
            a = self.sp_one_interface.save()
            if a is None:
                return
            with open(os.path.join(save_path), 'w') as f:
                f.write(a)
            mb.showinfo('Сохранено', f'Сохранено в {save_path}')

    def __energy_callback_sp_five(self, index):
        i, j = index[0], index[1]
        obj = index[2]

        try:
            energy = eval(obj.get())
            if energy == 0:
                raise Exception

            KSI = np.interp(energy * 10 ** 6, self.photon_table[:, 0], self.photon_table[:, 1])
            self.spectre_entry_val[i][j + 2].set('{:.5g}'.format(KSI))

            if energy <= self.elph[-1, 0]:
                energy_el = np.interp(energy, self.elph[:, 0], self.elph[:, 1])

            else:
                energy_el = self.elph_ext(energy)

            self.spectre_entry_val[i][j + 3].set('{:.5g}'.format(energy_el))

        except:
            self.spectre_entry_val[i][j + 2].set('')
            self.spectre_entry_val[i][j + 3].set('')

    def __energy_callback_sp_five_cont(self, index):
        i, j = index[0], index[1]
        obj = index[2]

        try:
            energy = eval(obj.get())
            if energy == 0:
                raise Exception

            KSI = np.interp(energy * 10 ** 6, self.photon_table[:, 0], self.photon_table[:, 1])
            self.spectre_entry_val[i][5].set('{:.5g}'.format(KSI))

            if energy <= self.elph[-1, 0]:
                energy_el = np.interp(energy, self.elph[:, 0], self.elph[:, 1])

            else:
                energy_el = self.elph_ext(energy)

            self.spectre_entry_val[i][6].set('{:.5g}'.format(energy_el))

        except:

            self.spectre_entry_val[i][5].set('')
            self.spectre_entry_val[i][6].set('')

    def __avg_energy_callback(self, index):
        i, j = index[0], index[1]
        obj = index[2]

        try:
            arg1 = float(self.spectre_entry_val[i][1].get())
            arg2 = float(self.spectre_entry_val[i][2].get())

            val = (arg1 + arg2) / 2

            self.spectre_entry_val[i][3].set('{:.5g}'.format(val))
        except:
            self.spectre_entry_val[i][3].set('')

    def __energy_part_callback(self, index):
        sum = 0
        try:
            if self.spectre_type_cb == 'CONTINUOUS':
                for i in range(1, len(self.spectre_entry_val)):
                    sum += float(self.spectre_entry_val[i][index].get())
            else:
                for i in range(len(self.spectre_entry_val)):
                    sum += float(self.spectre_entry_val[i][index].get())
            self.sum_energy_part['text'] = '{:.5g}'.format(sum)
        except:
            self.sum_energy_part['text'] = 'Заполните ячейки'

    def __creator(self, event):
        type = self.spectre_type_cb
        try:
            rows = int(self.rows_count_val.get())
            if rows > 120 or rows < 0:
                return
        except:
            return

        if type == 'DISCRETE' or type == 'CONTINUOUS':
            labels = ['Энергия (кэВ)', 'Доля(не нормируется)']
            if self.data_struct.data is None or self.data_struct.spectre_type != type:
                self.data_struct.create_empty_data((rows, 2))
                self.data_struct.data[:, :] = None
            else:
                self.data_struct.change_shape(rows, 2)

        elif type == 'SP_0':
            labels = ['№', 'Энергия (MеВ)', 'TETA(град.)', 'FI(град.)', 'Доля(не нормируется)']
            if self.data_struct.data is None or self.data_struct.spectre_type != 0:
                self.data_struct.create_empty_data((rows, 5))
            else:
                self.data_struct.change_shape(rows, 5)

        elif type == 'SP_5' and self.sp_5_combobox.get() == 'Точечный':
            labels = ['№', 'Энергия фотона (MeВ)', 'Доля(не нормируется)', 'Сечение см\u00b2/г',
                      'Энергия электрона (MeВ)']

            if self.data_struct.sp_5_type == 1 and self.data_struct.spectre_type == 5:
                self.data_struct.five_sp_convert(rows)

            elif self.data_struct.data is None or self.data_struct.spectre_type != 5:
                self.data_struct.sp_5_type = 0
                self.data_struct.create_empty_data((rows, 5))

            else:
                self.data_struct.change_shape(rows, 5)

        elif type == 'SP_5' and self.sp_5_combobox.get() == 'Непрерывный':

            if self.data_struct.sp_5_type == 0 and self.data_struct.spectre_type == 5:
                self.data_struct.five_sp_convert(rows)

            elif self.data_struct.data is None or self.data_struct.spectre_type != 5:
                self.data_struct.sp_5_type = 1
                self.data_struct.create_empty_data((rows, 7))

            else:
                self.data_struct.change_shape(rows, 7)

            labels = ['№', 'Эн. фотона (MeВ) от', 'Эн. фотона (MeВ) до', 'Средняя эн. фотона (MeВ)',
                      'Доля(не нормируется)',
                      'Сечение см\u00b2/г',
                      'Энергия электрона (MeВ)']

        elif type == 'SP_2' and self.sp_5_combobox.get() == 'Точечный':
            labels = ['№', 'Энергия (MеВ)', 'Доля(не нормируется)']

            if self.data_struct.sp_5_type == 1 and self.data_struct.spectre_type == 2:
                self.data_struct.five_sp_convert(rows)

            elif self.data_struct.data is None or self.data_struct.spectre_type != 2:
                self.data_struct.sp_5_type = 0
                self.data_struct.create_empty_data((rows, 3))

            else:
                self.data_struct.change_shape(rows, 3)

        elif type == 'SP_2' and self.sp_5_combobox.get() == 'Непрерывный':

            if self.data_struct.sp_5_type == 0 and self.data_struct.spectre_type == 2:
                self.data_struct.five_sp_convert(rows)

            elif self.data_struct.data is None or self.data_struct.spectre_type != 2:
                self.data_struct.sp_5_type = 1
                self.data_struct.create_empty_data((rows, 5))

            else:
                self.data_struct.change_shape(rows, 5)

            labels = ['№', '  Энергия (MeВ) от   ', '  Энергия (MeВ) до   ', 'Средняя энергия (MeВ)',
                      'Доля(не нормируется)']

        else:
            print('При создании не был опознан тип')
            return

        self.spectre_frame_constructor(labels, type)

        if type == 'SP_0' or type == 'SP_5' or type == 'SP_2':

            val_starts = int(self.starts_count_val.get())
            val_row_count = int(self.rows_count_val.get())

            if val_starts < 1:
                return

            self.rows_count_calc['text'] = f'{val_starts * val_row_count}'

    def __direction_vector_calc(self):
        try:
            x = float(self.direction_vector_val.get().split()[0])
            y = float(self.direction_vector_val.get().split()[1])
            z = float(self.direction_vector_val.get().split()[2])

            length = (x ** 2 + y ** 2 + z ** 2) ** 0.5

            if length < 0.99 or length > 1.01:
                self.direction_vector.configure(bg='#F08080')
                self.direction_vector_result['text'] = 'Длина вектора = {:.2g} |  Должна быть равна 1'.format(length)

            else:
                self.direction_vector.configure(bg='white')
                self.direction_vector_result['text'] = 'Длина вектора = {:.2g}'.format(length)
        except:
            self.direction_vector.configure(bg='#F08080')

    def __cb_react(self):
        self.spectre_type_cb = self.sp_type_dict.get(self.spetre_type_cobbobox.get())
        print(self.spectre_type_cb)

    def __starts_count_change(self):
        try:
            val_starts = int(self.starts_count_val.get())
            val_row_count = eval(self.rows_count_val.get())

            # if val_starts < 1:
            #     raise Exception

            self.rows_count_calc['text'] = f'{val_starts * val_row_count}'

        except:
            self.rows_count_calc['text'] = f'{0}'

    def __destroy_frames(self):

        try:
            self.cf.grid_forget()
            self.cf.destroy()

            self.spectre_entry.clear()
            self.spectre_entry_val.clear()

            for i in self.delete_buttons:
                i.destroy()

            self.delete_buttons.clear()
        except:
            pass

        # self.spectre_frame.grid_forget()
        # self.spectre_frame.destroy()

        # self.frame_description.grid_forget()
        # self.frame_description.destroy()

        if self.sp_one_interface is not None:
            try:
                self.sp_one_interface.destroy_widget()
                self.sp_one_interface = None
            except:
                pass

    def __destroy_sp_frame(self):
        try:
            self.spectre_frame.grid_forget()
            self.spectre_frame.destroy()
            self.spectre_entry.clear()
            self.spectre_entry_val.clear()

            for i in self.delete_buttons:
                i.destroy()

            self.delete_buttons.clear()

        except:
            pass

    def elph_ext(self, point):
        X = self.elph[:, 0]
        Y = self.elph[:, 1]

        x0, y0 = X[-1], Y[-1]
        x1, y1 = X[1000], Y[1000]

        k = (y0 - y1) / (x0 - x1)
        b = y0 - k * x0

        out_energy = k * point + b

        return out_energy

    def __delete_entry(self, index, start_row, column):

        for k in range(len(self.spectre_entry_val[index])):
            self.spectre_entry[index][k].grid_forget()
            self.spectre_entry[index][k].destroy()

        self.spectre_entry_val.pop(index)
        self.spectre_entry.pop(index)

        self.data_struct.data = np.delete(self.data_struct.data, index, axis=0)

        if self.spectre_type_cb == 'CONTINUOUS':
            self.delete_buttons[index - 1].destroy()
            self.delete_buttons.pop(index - 1)

        else:
            self.delete_buttons[index].destroy()
            self.delete_buttons.pop(index)

        # print(f'index -- {index}')
        # print(f'кнопки -- {len(self.delete_buttons)}')
        # print(f'vars -- {len(self.spectre_entry_val)}')
        # print(f'entrys -- {len(self.spectre_entry)}')

        if self.spectre_type_cb == 'CONTINUOUS':  # в континиус первую строку удалять нельзя, отсюда танцы
            for i in range(1, len(self.spectre_entry_val)):
                for j in range(len(self.spectre_entry_val[i])):
                    self.spectre_entry[i][j].grid_configure(row=start_row + i)
                self.delete_buttons[i - 1].grid_configure(row=start_row + i)
                self.delete_buttons[i - 1].configure(command=lambda ind=i: self.__delete_entry(ind, start_row, column))
        else:
            for i in range(len(self.spectre_entry_val)):
                for j in range(len(self.spectre_entry_val[i])):
                    self.spectre_entry[i][j].grid_configure(row=start_row + i)
                self.delete_buttons[i].grid_configure(row=start_row + i)
                self.delete_buttons[i].configure(command=lambda ind=i: self.__delete_entry(ind, start_row, column))

        if self.spectre_type_cb != 'DISCRETE' and self.spectre_type_cb != 'CONTINUOUS':

            for i in range(len(self.spectre_entry_val)):
                self.spectre_entry_val[i][0].set(str(i + 1))
                self.data_struct.data[i, 0] = i + 1

    def __insert_to_interface_from_data_struct(self, i, j, type='float'):
        if type == 'float':
            if self.data_struct.data[i, j] is None:
                self.spectre_entry_val[i][j].set('')
            else:
                self.spectre_entry_val[i][j].set('{:.6g}'.format(self.data_struct.data[i, j]))

        if 'nan' in self.spectre_entry_val[i][j].get():
            self.spectre_entry_val[i][j].set('')

    def __insert_data_to_data_struct(self, i, j, event):

        try:
            a = self.spectre_entry_val[i][j].get()
        except IndexError:
            return

        if a == '':
            self.data_struct.data[i, j] = None
        else:
            try:
                if ',' in a:
                    a = a.replace(',', '.')

                a = float(a)
                self.data_struct.data[i, j] = a
            except ValueError:
                self.data_struct.data[i, j] = None

    def perenos_to_five_spectre(self):
        """
        Function convert perenos spectre to five spectre and creates gui.

        All data store in data struct class.
        """

        perenos_spectre = fd.askopenfilename(title='Выберите файл spectre',
                                             filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))

        if perenos_spectre == '':
            return

        # perenos_spectre = r'C:\work\Test_projects\wpala\spectr_3_49_norm_na_1.txt'

        self.data_struct = SpectreDataStructure(perenos_spectre)
        self.data_struct.spectre_type_identifier()
        if self.data_struct.data is None:
            return
        perenos_data = self.data_struct.data.copy()
        perenos_type = self.data_struct.spectre_type

        if perenos_type == 'CONTINUOUS':
            self.sp_5_combobox.set('Непрерывный')

            self.data_struct.create_empty_data((perenos_data.shape[0] - 1, 7))
            self.data_struct.sp_5_type = 1
            self.data_struct.spectre_type = 5

            for i in range(1, perenos_data.shape[0]):
                self.data_struct.data[i - 1, 1] = perenos_data[i - 1, 0] * 1e-3
                self.data_struct.data[i - 1, 2] = perenos_data[i, 0] * 1e-3
                self.data_struct.data[i - 1, 4] = perenos_data[i, 1]

            for i in range(self.data_struct.data.shape[0]):
                self.data_struct.data[i, 0] = i + 1

            labels = ['№', 'Эн. фотона (MeВ) от', 'Эн. фотона (MeВ) до', 'Средняя эн. фотона (MeВ)',
                      'Доля(не нормируется)',
                      'Сечение см\u00b2/г',
                      'Энергия электрона (MeВ)']
            self.spectre_frame_constructor(labels, 'SP_5')

        if perenos_type == 'DISCRETE':
            self.sp_5_combobox.set('Точечный')

            self.data_struct.create_empty_data((perenos_data.shape[0], 5))
            self.data_struct.sp_5_type = 0
            self.data_struct.spectre_type = 5

            self.data_struct.data[:, 1] = perenos_data[:, 0] * 1e-3
            self.data_struct.data[:, 2] = perenos_data[:, 1]

            for i in range(self.data_struct.data.shape[0]):
                self.data_struct.data[i, 0] = i + 1

            labels = ['№', 'Энергия фотона (MeВ)', 'Доля(не нормируется)', 'Сечение см\u00b2/г',
                      'Энергия электрона (MeВ)']
            self.spectre_frame_constructor(labels, 'SP_5')

        self.rows_count_val.set(str(self.data_struct.data.shape[0]))
        self.rows_count_calc['text'] = str(int(self.rows_count_val.get() * int(self.starts_count_val.get())))

    def five_spectre_to_perenos(self):
        """Convert gui from five spectre to perenos spectre"""
        self.__destroy_frames()

        five_data = self.data_struct.data.copy()
        five_type = self.data_struct.sp_5_type

        if five_type == 0:  # discrete
            self.description_discrete_cont()
            self.data_struct.create_empty_data((five_data.shape[0], 2))

            self.data_struct.data[:, 0] = five_data[:, 1] * 1e3
            self.data_struct.data[:, 1] = five_data[:, 2]

            labels = ['Энергия (кэВ)', 'Доля(не нормируется)']
            self.spectre_frame_constructor(labels, 'DISCRETE')
            self.spetre_type_cobbobox.set('Дискретный')
            self.spectre_type_cb = 'DISCRETE'

        if five_type == 1:  # CONTINUOUS
            self.description_discrete_cont()
            self.data_struct.create_empty_data((five_data.shape[0], 2))

            for i in range(1, five_data.shape[0]):
                self.data_struct.data[i - 1, 0] = five_data[i - 1, 1] * 1e3
                self.data_struct.data[i, 0] = five_data[i, 2] * 1e3
                self.data_struct.data[i, 1] = five_data[i, 4]

            labels = ['Энергия (кэВ)', 'Доля(не нормируется)']
            self.spectre_frame_constructor(labels, 'CONTINUOUS')
            self.spetre_type_cobbobox.set('Непрерывный')
            self.spectre_type_cb = 'CONTINUOUS'

        self.rows_count_val.set(str(self.data_struct.data.shape[0]))

        # print(np.sum(self.data_struct.data[:, 1]))

    def onExit(self):
        self.parent.quit()
        self.parent.destroy()

    def _data_validation(self, dtype, value_obj, entry_object, exception_label):

        try:
            val = eval(value_obj.get())
        except:
            val = None

        if type(val) not in dtype or val is None:
            entry_object.configure(bg='#F08080')
            exception_label.grid()

        else:
            entry_object.configure(bg='#FFFFFF')
            exception_label.grid_remove()

    def _check_data_for_save(self):
        if self.data_struct is None:
            mb.showerror('save', 'Не введены данные')

            return

        if self.data_struct.data is None:
            mb.showerror('save', 'Не введены данные')
            return

        if self.spectre_type_cb == 'SP_0':
            if self.spectre_power_val.get() == '':
                mb.showerror('SAVE', 'Не указана мощность спектра')
                return
            if self.spectre_number_val.get() == '':
                mb.showerror('save', 'Не указан номер спектра')
                return
            if self.rows_count_calc['text'] == '':
                mb.showerror('save', 'Не указано число частиц запускаемых на каждом шаге')
                return
            if self.starts_count_val.get() == '':
                mb.showerror('save', 'Не указано количество запусков одинаковых частиц')
                return
            if self.rows_count_val.get() == '':
                return

        if self.spectre_type_cb == 'SP_5' or self.spectre_type_cb == 'SP_2':

            if self.spectre_number_val.get() == '':
                mb.showerror('save', 'Не указан номер спектра')
                return
            if self.rows_count_calc['text'] == '':
                mb.showerror('save', 'Не указано число частиц запускаемых на каждом шаге')
                return
            if self.starts_count_val.get() == '':
                mb.showerror('save', 'Не указано количество запусков одинаковых частиц')
                return
            if self.rows_count_val.get() == '':
                return

        if np.any(np.isnan(self.data_struct.data)):
            mb.showerror('save', 'Заполните все поля в значениях спектра.\n'
                                 '(Значения сохраняются после удаления курсора из области ввода)')
            return

        return True


class SpectreDataStructure:
    def __init__(self, path=None):
        self.spectre_path = path

        self.spectre_type = None

        self.description = ''
        self.sp_number = None
        self.sp_power = None
        self.starts_count = None

        self.sp_5_type = None

        self.data = None

    def spectre_type_identifier(self):
        with open(self.spectre_path, 'r') as file:
            lines = file.readlines()

        if 'SP_TYPE=CONTINUOUS' in lines[0]:
            self.spectre_type = 'CONTINUOUS'

        elif 'SP_TYPE=DISCRETE' in lines[0]:
            self.spectre_type = 'DISCRETE'

        else:
            try:
                self.spectre_type = int(lines[6].strip())
            except:
                print('Тип спектра не опознан')
                self.data = None
                return

        self.start_read()

    def start_read(self):
        with open(self.spectre_path, 'r') as file:
            lines = file.readlines()

        if self.spectre_type == 0:
            self.description = lines[0].strip()
            self.sp_number = int(lines[2].strip())
            self.sp_power = float(lines[4].strip())
            self.starts_count = int(lines[10].strip())

            tmp = []
            for line in lines[14:]:
                line = line.strip().split()
                tmp.append(line)

            self.data = np.array(tmp, dtype=float)

        if self.spectre_type == 2:
            self.description = lines[0].strip()
            self.sp_number = int(lines[2].strip())
            self.sp_power = float(lines[4].strip())
            self.starts_count = int(lines[10].strip())
            self.direction_vector = list(map(float, lines[12].strip().split()))

            tmp = []
            for line in lines[18:]:
                line = line.strip().split()
                tmp.append(line)

            self.data = np.array(tmp, dtype=float)

        if self.spectre_type == 5:
            self.description = lines[0].strip()
            self.sp_number = int(lines[2].strip())
            self.sp_power = float(lines[6].strip())
            self.starts_count = int(lines[10].strip())
            self.sp_5_type = int(lines[14].strip())

            tmp = []
            for line in lines[16:]:
                line = line.strip().split()
                tmp.append(line)

            self.data = np.array(tmp, dtype=float)

        if self.spectre_type == 'DISCRETE':
            self.data = np.loadtxt(self.spectre_path, skiprows=2, dtype=float)

        if self.spectre_type == 'CONTINUOUS':
            self.data = np.loadtxt(self.spectre_path, skiprows=3, dtype=float)

            with open(self.spectre_path, 'r') as file:
                lines = file.readlines()

            start = (lines[2].strip())

            self.data = np.insert(self.data, 0, [start, None], axis=0)

    def create_empty_data(self, shape=(0, 0)):
        self.data = np.zeros((shape[0], shape[1]), dtype=float)

        if self.spectre_type != 'DISCRETE' and self.spectre_type != 'CONTINUOUS':
            if self.spectre_type == 0:
                self.data[:, 1] = None

            if self.spectre_type == 2:
                if self.sp_5_type == 0:
                    self.data[:, 1] = None
                elif self.sp_5_type == 1:
                    self.data[:, 1:3] = None

            if self.spectre_type == 5:
                if self.sp_5_type == 0:
                    self.data[:, 1] = None
                elif self.sp_5_type == 1:
                    self.data[:, 1:3] = None

            for i in range(self.data.shape[0]):
                self.data[i, 0] = i + 1

    def change_shape(self, rows, append_shape):
        d = [None for _ in range(append_shape)]

        if rows < self.data.shape[0]:
            delta = self.data.shape[0] - rows
            for i in range(delta):
                self.data = np.delete(self.data, -1, axis=0)
        elif rows > self.data.shape[0]:
            delta = rows - self.data.shape[0]
            for i in range(delta):
                self.data = np.append(self.data, [d], axis=0)

        if self.spectre_type == 0 or self.spectre_type == 5:
            for i in range(self.data.shape[0]):
                self.data[i, 0] = i + 1

    def five_sp_convert(self, rows):

        if self.sp_5_type == 0:
            self.zero_to_one_convert(rows)
        elif self.sp_5_type == 1:
            self.one_to_zero_convert(rows)

    def zero_to_one_convert(self, rows):
        old_data = self.data.copy()

        self.create_empty_data((rows, 7))
        self.sp_5_type = 1

        for i in range(self.data.shape[0]):
            for j in range(self.data.shape[1]):
                if j == 1:
                    try:
                        self.data[i][j] = old_data[i, j]
                    except IndexError:
                        self.data[i][j] = None
                if j == 2 and i != self.data.shape[0] - 1:
                    try:
                        self.data[i][j] = old_data[i + 1, 1]
                    except IndexError:
                        self.data[i][j] = None
                if j == 4:
                    try:
                        self.data[i][j] = old_data[i, 2]
                    except IndexError:
                        self.data[i][j] = None

    def one_to_zero_convert(self, rows):
        old_data = self.data.copy()

        self.create_empty_data((rows, 5))
        self.sp_5_type = 0

        for i in range(self.data.shape[0]):
            for j in range(self.data.shape[1]):
                if j == 1:
                    try:
                        self.data[i][j] = old_data[i, j]
                    except IndexError:
                        self.data[i][j] = None
                if j == 2:
                    try:
                        self.data[i][j] = old_data[i, 4]
                    except IndexError:
                        self.data[i][j] = None


if __name__ == '__main__':
    root = tk.Tk()

    x = SpectreConfigure(parent=root, path=r'C:\work\Test_projects\wpala')
    x.grid(sticky='NWSE')

    root.protocol("WM_DELETE_WINDOW", x.onExit)

    root.mainloop()

    # a = SpectreDataStructure(r'C:\Users\Nick\Desktop\sp_2_ex')
    # a.spectre_type_identifier()
    # print(a.direction_vector)
    # print(a.data)
