import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter import simpledialog
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
import os

from Project_reader import DataParser
from Spectre_one_interface import SpectreOneInterface


class SpectreConfigure(tk.Toplevel):
    def __init__(self, path='', parent=None):
        super().__init__(parent)

        self.path = path

        self.title('Редактор спектра')
        # self.grab_set()

        self.spectre_frame = None
        self.spectre_path = ''

        self.spectre_entry_val = []
        self.spectre_entry = []

        self.spectre_frame = None
        self.frame_description = None

        self.spectre_type_cb = None
        self.sp_type_dict = {'Фиксированный': 'SP_0',
                             'Разыгрывание': 'SP_1',
                             'Пятый': 'SP_5',
                             'DISCRETE': 'DISCRETE',
                             'CONTINUOUS': 'CONTINUOUS'}

        self.row_changer = None

        self.lines = None
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

        self.sp_one_interface = None

        self.constructor()

    def pechs_check(self):

        if self.path == '':
            self.path == os.getcwd()

        if os.path.exists(os.path.join(self.path, r'pechs\materials')):
            self.materials_path = os.path.join(self.path, r'pechs\materials')
            print(f'Materials обнаружен в {self.materials_path}')
            # mb.showinfo('PECHS', f'Materials обнаружен в {self.materials_path}')

        else:
            mb.showinfo('PECHS', 'Папка pechs/materials не обнаружена.\nВыберите папку materials')
            self.materials_path = fd.askdirectory(title='Выберите папку materials', initialdir=self.path)
            print(f'Materials обнаружен в {self.materials_path}')
            if self.materials_path == '':
                return 0

        photon_path = os.path.join(self.materials_path, r'mat-air\photon\xtbl.23')
        if not os.path.exists(photon_path):
            mb.showerror('PATH', f'Файл xtbl.23 не был найден в дирекории {os.path.normpath(photon_path)}\n'
                                 f'Укажите путь к файлу напрямую')

            photon_path = fd.askopenfilename(title='Выберите файл xtbl.23 для фотонов', initialdir=self.path)
            if photon_path == '':
                return 0

        self.photon_table = np.loadtxt(photon_path, skiprows=18)
        self.photon_table = 10 ** self.photon_table

        return 1

    def constructor(self):
        self.button_open_spectre = tk.Button(self, text='Выбрать спектр', command=self.open_spectre, width=13)
        self.button_open_spectre.grid(row=0, column=0, padx=3, pady=3, sticky='WN')

        self.button_create_spectre = tk.Button(self, text='Создать спектр', command=self.create_spectre, width=13)
        self.button_create_spectre.grid(row=0, column=1, padx=3, pady=3, sticky='WN')

        self.save_button = tk.Button(self, text='Сохранить', command=lambda: self._save_data(False), width=13)
        self.save_button.grid(row=2, column=0, pady=3, padx=3, sticky='WN')
        self.save_as_button = tk.Button(self, text='Сохранить как', command=lambda: self._save_data(True), width=13)
        self.save_as_button.grid(row=2, column=1, pady=3, padx=3, sticky='WN')

        combobox_values = ['Фиксированный', 'Разыгрывание', 'Пятый', 'DISCRETE', 'CONTINUOUS']
        self.spetre_type_cobbobox = ttk.Combobox(self, value=[val for val in combobox_values], width=13,
                                                 state='readonly')
        self.spetre_type_cobbobox.grid(row=0, column=3)
        self.spetre_type_cobbobox.set('Тип спектра')

        self.bind_class(self.spetre_type_cobbobox, "<<ComboboxSelected>>", self.__cb_react)

    def open_spectre(self, use_constructor=True, use_chose_spectre=None):
        if use_chose_spectre is None:
            self.spectre_path = fd.askopenfilename(title='Выберите файл spectre',
                                                   filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
            if self.spectre_path == '':
                return
        else:
            self.spectre_path = use_chose_spectre

        self.__destroy_frames()

        with open(self.spectre_path, 'r') as file:
            lines = file.readlines()

        self.lines = lines
        self.spectre_number_data = int(lines[2])

        if use_constructor is False:
            return self.spectre_number_data, self.spectre_path

        if 'SP_TYPE=CONTINUOUS' in lines[0]:
            with open(self.spectre_path, 'r') as file:
                lines = file.readlines()
            out = []
            for i in range(len(lines)):
                if i == 2:
                    a = [lines[i].strip(), '0']
                    out.append(a)
                elif i > 2:
                    out.append(lines[i].strip().split())

            data = np.array(out, dtype=float)
            self.spectre_type_cb = 'CONTINUOUS'
            labels = ['Энергия (кеВ)', 'Доля(не нормируется)']
            self.description_discrete_cont(True, data.shape[0])
            self.spectre_frame_constructor(data, labels, 'CONTINUOUS')

        elif 'SP_TYPE=DISCRETE' in lines[0]:
            data = np.loadtxt(self.spectre_path, skiprows=2)
            self.spectre_type_cb = 'DISCRETE'
            labels = ['Энергия (кеВ)', 'Доля(не нормируется)']
            self.description_discrete_cont(True, data.shape[0])
            self.spectre_frame_constructor(data, labels, 'DISCRETE')
            # self.rows_count_val.trace('r', lambda name, index, mode: self.__creator('DISCRETE', labels, 2))

        elif 'Номер спектра' in lines[1] and lines[6].strip() == '0':
            self.spectre_type_cb = 'SP_0'
            self.spetre_type_cobbobox.set('Фиксированный')
            data = self.description_sp_zero(True, self.spectre_type_cb)
            labels = ['№', 'Энергия (MеВ)', 'TETA(град.)', 'FI(град.)', 'Доля(не нормируется)']
            self.spectre_frame_constructor(data, labels, 'SP_0')
            # self.rows_count_val.trace('w', lambda name, index, mode: self.__creator('SP_0', labels, 5))

        elif 'Номер спектра' in lines[1] and lines[6].strip() == '5':
            check = self.pechs_check()
            if check == 0:
                return

            self.elph = DataParser(self.path).elph_reader()
            self.spectre_type_cb = 'SP_5'
            self.spetre_type_cobbobox.set(self.spectre_type_cb)
            data = self.description_sp_zero(True, self.spectre_type_cb)
            labels = ['№', 'Энергия (кеВ)', 'Доля(не нормируется)', 'Сечение см\u00b2/г', 'Энергия электрона']
            self.spectre_frame_constructor(data, labels, 'SP_5')
            # self.rows_count_val.trace('w', lambda name, index, mode: self.__creator('SP_5', labels, 5))

        elif 'Номер спектра' in lines[1] and lines[6].strip() == '1':
            self.spectre_type_cb = 'SP_1'
            self.spetre_type_cobbobox.set('Разыгрывание')

            self.sp_one_interface = SpectreOneInterface(self, self.spectre_path)
            self.sp_one_interface.data_load()

            self.sp_one_interface.grid(row=3, column=0, columnspan=12, rowspan=60, sticky="W", padx=10)



        else:
            f = self.spectre_path
            osCommandString = f"notepad.exe {f}"
            os.system(osCommandString)
            self.destroy()

            # mb.showerror('Spectre error', 'Тип спектра не был распознан')

        # self.spectre_frame_constructor(data)

    def description_sp_zero(self, from_data, spectre_type):
        self.rowsp = len(self.lines[:13]) + 1

        sp_t = {'SP_0': '0',
                'SP_5': '5'}

        self.frame_description = ttk.Frame(self)
        self.frame_description.grid(row=3, column=0, columnspan=12, rowspan=self.rowsp, sticky="W", padx=10)

        for i in range(13):

            if i == 0:
                self.spectre_note_val = tk.StringVar()
                self.spectre_note_val.set(self.lines[i].strip())
                self.spectre_note = tk.Entry(self.frame_description, textvariable=self.spectre_note_val, width=50)
                self.spectre_note.grid(row=i, column=0, columnspan=12, sticky='NW')

            elif i == 2:
                self.spectre_number_val = tk.StringVar()
                self.spectre_number_val.set(self.lines[i].strip())
                self.spectre_number = tk.Entry(self.frame_description, textvariable=self.spectre_number_val, width=10)
                self.spectre_number.grid(row=i, column=0, columnspan=12, sticky='NW')

            elif i == 3:
                a = 'Мощность спектра (шт/см\u00b2/с)- для поверхностных, (шт/см\u00b3/с)- для объемных'
                tk.Label(self.frame_description, text=a, justify='left').grid(row=i, column=0,
                                                                              columnspan=12,
                                                                              sticky='NW')

            elif i == 4:
                self.spectre_power_val = tk.StringVar()
                self.spectre_power_val.set(self.lines[i].strip())
                self.spectre_power = tk.Entry(self.frame_description, textvariable=self.spectre_power_val, width=10)
                self.spectre_power.grid(row=i, column=0, columnspan=12, sticky='NW')

            elif i == 6 or i == 5:
                pass
                # self.spectre_type = tk.Label(self.frame_description, text=sp_t.get(spectre_type))
                # self.spectre_type.grid(row=i, column=0, columnspan=12, sticky='NW')

            elif i == 8:
                self.rows_count_calc = tk.Label(self.frame_description, text=self.lines[i].strip(), justify='left')
                self.rows_count_calc.grid(row=i, column=0, columnspan=12, sticky='NW')

            elif i == 10:
                self.starts_count_val = tk.StringVar()
                self.starts_count_val.set(self.lines[i].strip())
                self.starts_count_val.trace('w', lambda name, index, mode: self.__starts_count_change())
                self.starts_count = tk.Entry(self.frame_description, textvariable=self.starts_count_val, width=10)
                self.starts_count.grid(row=i, column=0, columnspan=2, sticky='NW')

            elif i == 12:
                self.rows_count_val = tk.StringVar()
                self.rows_count_val.set(self.lines[i].strip())
                self.rows_count = tk.Entry(self.frame_description, textvariable=self.rows_count_val, width=10)
                self.rows_count.grid(row=i, column=0, columnspan=2, sticky='NW')
                self.rows_count.bind('<Return>', self.__creator)

                tk.Label(self.frame_description, text='Нажмите Enter для применения').grid(row=i, column=2,
                                                                                           columnspan=6, sticky='NW')

            else:
                tk.Label(self.frame_description, text=self.lines[i].strip(), justify='left').grid(row=i, column=0,
                                                                                                  columnspan=12,
                                                                                                  sticky='NW')

        if from_data is True:
            out = []
            for i in range(14, 14 + int(self.rows_count_val.get())):
                out.append(self.lines[i].strip().split())
            return np.array(out, dtype=str)

    def description_discrete_cont(self, from_data, data_shape):
        self.rowsp = 2

        self.frame_description = ttk.Frame(self)
        self.frame_description.grid(row=3, column=0, columnspan=12, rowspan=self.rowsp, sticky="W", padx=10)

        tk.Label(self.frame_description, text='Число ячеек таблици (ниже)').grid(row=0, column=0, columnspan=12,
                                                                                 sticky='NW')

        self.rows_count_val = tk.StringVar()
        self.rows_count = tk.Entry(self.frame_description, textvariable=self.rows_count_val, width=10)
        self.rows_count.grid(row=1, column=0, columnspan=2, sticky='NW')
        tk.Label(self.frame_description, text='Нажмите Enter для применения').grid(row=1, column=2,
                                                                                   columnspan=6, sticky='NW')
        self.rows_count.bind('<Return>', self.__creator)

        if from_data is True:
            self.rows_count_val.set(f'{data_shape}')
        else:
            self.rows_count_val.set('')

    def create_spectre(self):
        if self.spectre_type_cb is None:
            print('Выберите тип создаваемого спектра')
            return

        self.__destroy_frames()

        if type(self.lines) is list:
            self.lines.clear()

        if self.spectre_type_cb == 'SP_0':
            self.lines = self._sp_zero_form.copy()
            self.description_sp_zero(False, self.spectre_type_cb)
            labels = ['№', 'Энергия (MеВ)', 'TETA(град.)', 'FI(град.)', 'Доля(не нормируется)']
            # self.rows_count_val.trace('w', lambda name, index, mode: self.__creator('SP_0', labels, 5))

        if self.spectre_type_cb == 'SP_5':
            check = self.pechs_check()
            if check == 0:
                return

            self.elph = DataParser(self.path).elph_reader()
            self.lines = self._sp_zero_form.copy()
            self.description_sp_zero(False, self.spectre_type_cb)
            labels = ['№', 'Энергия (МеВ)', 'Доля(не нормируется)', 'Сечение см\u00b2/г', 'Энергия электрона']
            # self.rows_count_val.trace('w', lambda name, index, mode: self.__creator('SP_5', labels, 5))

        if self.spectre_type_cb == 'SP_1':
            sp_one_interface = SpectreOneInterface(self, None)
            sp_one_interface.grid(row=3, column=0, columnspan=12, rowspan=60, sticky="W", padx=10)

        if self.spectre_type_cb == 'DISCRETE':
            self.description_discrete_cont(False, 1)

        if self.spectre_type_cb == 'CONTINUOUS':
            self.description_discrete_cont(False, 1)

    def spectre_frame_constructor(self, data, labels, type):
        row_count = data.shape[0]
        column_count = data.shape[1]

        self.__destroy_sp_frame()

        self.spectre_frame = ttk.Frame(self)
        self.spectre_frame.grid(row=4 + self.rowsp, column=0, rowspan=10, columnspan=12, padx=10, sticky='NW')

        for i, x in enumerate(labels):
            tk.Label(self.spectre_frame, text=x).grid(row=0, column=i)

        for i in range(row_count):
            tmp_val = []

            for j in range(column_count):
                tmp_val.append(tk.StringVar())
            self.spectre_entry_val.append(tmp_val)

        if type == 'SP_0':
            self.data_insert_sp_zero(data)
        if type == 'SP_5':
            self.data_insert_sp_five(data)
        if type == 'DISCRETE':
            self.data_insert_discrete(data)
        if type == 'CONTINUOUS':
            self.data_insert_cont(data)

    def data_insert_sp_zero(self, data):
        row_count = data.shape[0]
        column_count = data.shape[1]
        for i in range(row_count):

            tmp_entry = []
            for j in range(column_count):
                tmp_entry.append(tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], width=15,
                                          justify='center'))
                tmp_entry[j].grid(row=1 + i, column=j)
            self.spectre_entry.append(tmp_entry)

        self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
        self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=column_count - 1)

        for i in range(row_count):  # Нааполнение данными
            for j in range(column_count):
                if j == column_count - 1:
                    self.spectre_entry_val[i][j].trace('w',
                                                       lambda name, index, mode: self.__energy_part_callback(-1))

                self.spectre_entry_val[i][j].set(data[i, j])

        [self.spectre_entry[i][0].configure(state='readonly', width=5) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][2].configure(state='normal', width=8) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][3].configure(state='normal', width=8) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][4].configure(state='normal', width=16) for i in range(len(self.spectre_entry))]

    def data_insert_sp_five(self, data):
        row_count = data.shape[0]
        column_count = data.shape[1]
        for i in range(row_count):

            tmp_entry = []
            for j in range(column_count):
                tmp_entry.append(
                    tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], justify='center'))
                tmp_entry[j].grid(row=1 + i, column=j)
            self.spectre_entry.append(tmp_entry)

        self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
        self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=2)

        for i in range(row_count):  # Нааполнение данными
            for j in range(column_count):
                if j == 0:
                    try:
                        self.spectre_entry_val[i][j].set('{:.5g}'.format(data[i, j]))
                    except ValueError:
                        self.spectre_entry_val[i][j].set(data[i, j])
                if j == 1:
                    self.spectre_entry_val[i][j].trace('w',
                                                       lambda name, index, mode, sv=(
                                                           i, j, self.spectre_entry_val[i][
                                                               j]): self.__energy_callback_sp_five(
                                                           sv))
                    try:
                        self.spectre_entry_val[i][j].set('{:.5g}'.format(data[i, j]))
                    except ValueError:
                        self.spectre_entry_val[i][j].set(data[i, j])

                if j == 2:
                    self.spectre_entry_val[i][j].trace('w',
                                                       lambda name, index, mode: self.__energy_part_callback(2))

                    try:
                        self.spectre_entry_val[i][j].set('{:.3g}'.format(data[i, j]))
                    except ValueError:
                        self.spectre_entry_val[i][j].set(data[i, j])

        [self.spectre_entry[i][0].configure(state='readonly', width=5) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][1].configure(state='normal', width=13) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][2].configure(state='normal', width=13) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][3].configure(state='readonly', width=13) for i in range(len(self.spectre_entry))]
        [self.spectre_entry[i][4].configure(state='readonly', width=13) for i in range(len(self.spectre_entry))]

    def data_insert_discrete(self, data):
        row_count = data.shape[0]
        column_count = data.shape[1]
        for i in range(row_count):

            tmp_entry = []
            for j in range(column_count):
                tmp_entry.append(tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], width=15,
                                          justify='center'))
                tmp_entry[j].grid(row=1 + i, column=j)
            self.spectre_entry.append(tmp_entry)

        self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
        self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=column_count - 1)

        for i in range(row_count):  # Нааполнение данными
            for j in range(column_count):
                if j == column_count - 1:
                    self.spectre_entry_val[i][j].trace('w',
                                                       lambda name, index, mode: self.__energy_part_callback(-1))

                try:
                    self.spectre_entry_val[i][j].set('{:.6g}'.format(data[i, j]))
                except ValueError:
                    self.spectre_entry_val[i][j].set(data[i, j])

    def data_insert_cont(self, data):
        row_count = data.shape[0]
        column_count = data.shape[1]

        for i in range(row_count):

            tmp_entry = []
            for j in range(column_count):
                tmp_entry.append(tk.Entry(self.spectre_frame, textvariable=self.spectre_entry_val[i][j], width=15,
                                          justify='center'))
                tmp_entry[j].grid(row=1 + i, column=j)
            self.spectre_entry.append(tmp_entry)

        self.spectre_entry[0][1]['state'] = 'disabled'

        self.sum_energy_part = tk.Label(self.spectre_frame, text='0')
        self.sum_energy_part.grid(row=len(self.spectre_entry) + 1, column=column_count - 1)

        for i in range(row_count):  # Нааполнение данными
            for j in range(column_count):
                if i != 0:
                    if j == column_count - 1:
                        self.spectre_entry_val[i][j].trace('w',
                                                           lambda name, index, mode: self.__energy_part_callback(-1))
                try:
                    self.spectre_entry_val[i][j].set('{:.6g}'.format(data[i, j]))
                except ValueError:
                    self.spectre_entry_val[i][j].set(data[i, j])

        self.spectre_entry_val[0][1].set('')

    def _save_data(self, save_as):

        if save_as is True:
            save_path = fd.asksaveasfilename(initialdir=self.path)
            if save_path == '':
                return
        elif save_as is False:
            if self.spectre_path == '':
                mb.showerror('save error', 'Воспользуйтесь кнопкой "Сохранить как"')
            save_path = self.spectre_path

        print(self.spectre_type_cb)
        if self.spectre_type_cb == 'SP_0' or self.spectre_type_cb == 'SP_5':

            decode_number = {'SP_5': 5, 'SP_0': 0}

            out_header = self._sp_zero_form.copy()
            if self.spectre_power_val.get() == '':
                mb.showerror('SAVE', 'Не указана мощность спектра')
                return
            if self.spectre_number_val.get() == '':
                mb.showerror('save', 'Не указан номер спектра')
                return
            if self.rows_count_calc['text'] == '':
                mb.showerror('save', 'Не указано число частиц запускаемых на каждом шаге')
                return
            if self.rows_count_calc['text'] == '':
                mb.showerror('save', 'Не указано число частиц запускаемых на каждом шаге')
                return
            if self.starts_count_val.get() == '':
                mb.showerror('save', 'Не указано количество запусков одинаковых частиц')
                return
            if self.rows_count_val.get() == '':
                return

            out_header[0] = self.spectre_note_val.get()
            out_header[2] = self.spectre_number_val.get()
            out_header[3] = 'Мощность спектра (шт/см**2/с)- для поверхностных, (шт/см**3/с)- для объемных'
            out_header[4] = self.spectre_power_val.get()
            out_header[6] = f'{decode_number[self.spectre_type_cb]}'
            out_header[8] = self.rows_count_calc['text']
            out_header[10] = self.starts_count_val.get()
            out_header[12] = self.rows_count_val.get()

            if self.spectre_type_cb == 'SP_5':
                out_header[
                    13] = 'Таблица частиц  ( №,  Энергия фотонов(MeВ), Доля(не нормируется), Сечение(см**2/г), Энергия электронов(MeВ))'

            out_data = []
            for i, x in enumerate(self.spectre_entry_val):
                row = []
                for j in range(len(self.spectre_entry_val[i])):
                    row.append(self.spectre_entry_val[i][j].get())
                out_data.append(row)
            out_data = np.array(out_data, dtype=float)

            # print(out_header)
            # print(out_data)
            header = ''
            for i, x in enumerate(out_header):
                if i == len(out_header) - 1:
                    header += x
                else:
                    header += x + '\n'
            np.savetxt(save_path, out_data, comments='', header=header, delimiter='\t',
                       fmt=['%i', '%3.3g', '%3.4g', '%4.4g', '%3.4g'])

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

            np.savetxt(save_path, out_data, comments='', header=header, delimiter='\t', fmt=['%.5g', '%.8g'])

        if self.spectre_type_cb == 'DISCRETE':
            header = f'SP_TYPE=CONTINUOUS\n' \
                     f'[DATA]'

            out_data = []
            for i in range(len(self.spectre_entry_val)):
                row = []
                for j in range(len(self.spectre_entry_val[i])):
                    row.append(self.spectre_entry_val[i][j].get())
                out_data.append(row)
            out_data = np.array(out_data, dtype=float)

            np.savetxt(save_path, out_data, comments='', header=header, delimiter='\t', fmt=['%.5g', '%.8g'])

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

    def __energy_part_callback(self, index):
        sum = 0
        try:
            for i in range(len(self.spectre_entry_val)):
                sum += eval(self.spectre_entry_val[i][index].get())
            self.sum_energy_part['text'] = '{:.4g}'.format(sum)
        except:
            self.sum_energy_part['text'] = 'Заполните ячейки'

    # def __creator(self, type, labels, column):
    #
    #     try:
    #         rows = int(self.rows_count_val.get())
    #         if rows > 80:
    #             raise Exception
    #         old_elems = self.spectre_entry_val.copy()
    #         data = np.empty((rows, column), dtype=str)
    #         self.spectre_frame_constructor(data, labels, type)
    #         if type == 'SP_0' or type == 'SP_5':
    #             self.rows_count_ag['text'] = self.rows_count_val.get()
    #
    #         for i in range(len(self.spectre_entry_val)):
    #             for j in range(len(self.spectre_entry_val[i])):
    #                 try:
    #                     self.spectre_entry_val[i][j].set(old_elems[i][j].get())
    #                 except IndexError:
    #                     self.spectre_entry_val[i][j].set('erro')
    #
    #         if type == 'SP_0' or type == 'SP_5':
    #             [self.spectre_entry_val[i][0].set(str(i + 1)) for i in range(int(self.rows_count_val.get()))]
    #
    #     except:
    #         print('err')
    #         pass

    def __creator(self, event):
        type = self.spectre_type_cb
        if type == 'DISCRETE' or type == 'CONTINUOUS':
            labels = ['Энергия (кеВ)', 'Доля(не нормируется)']
            column = 2
        if type == 'SP_0':
            labels = ['№', 'Энергия (MеВ)', 'TETA(град.)', 'FI(град.)', 'Доля(не нормируется)']
            column = 5
        if type == 'SP_5':
            labels = ['№', 'Энергия фотона (MeВ)', 'Доля(не нормируется)', 'Сечение см\u00b2/г',
                      'Энергия электрона (MeВ)']
            column = 5

        try:
            rows = int(self.rows_count_val.get())
            if rows > 80 or rows < 0:
                raise Exception
            old_elems = self.spectre_entry_val.copy()
            data = np.empty((rows, column), dtype=str)
            self.spectre_frame_constructor(data, labels, type)

            for i in range(len(self.spectre_entry_val)):
                for j in range(len(self.spectre_entry_val[i])):
                    try:
                        self.spectre_entry_val[i][j].set(old_elems[i][j].get())
                    except IndexError:
                        self.spectre_entry_val[i][j].set('')

            if type == 'SP_0' or type == 'SP_5':
                [self.spectre_entry_val[i][0].set(str(i + 1)) for i in range(int(self.rows_count_val.get()))]

                val_starts = int(self.starts_count_val.get())
                val_row_count = eval(self.rows_count_val.get())

                if val_starts < 1:
                    raise Exception

                self.rows_count_calc['text'] = f'{val_starts * val_row_count}'

        except:
            print('error')
            pass

    def __cb_react(self, event):
        self.spectre_type_cb = self.sp_type_dict.get(self.spetre_type_cobbobox.get())
        print(self.spectre_type_cb)

    def __starts_count_change(self):
        try:
            val_starts = int(self.starts_count_val.get())
            val_row_count = eval(self.rows_count_val.get())

            if val_starts < 1:
                raise Exception

            self.rows_count_calc['text'] = f'{val_starts * val_row_count}'

        except:
            print('starts_count_val error')

    def __destroy_frames(self):
        try:
            self.frame_description.grid_forget()
            self.frame_description.destroy()
            self.spectre_frame.grid_forget()
            self.spectre_frame.destroy()
            self.spectre_entry.clear()
            self.spectre_entry_val.clear()

        except:
            pass

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


if __name__ == '__main__':
    root = tk.Tk()

    x = SpectreConfigure(parent=root)

    root.mainloop()
