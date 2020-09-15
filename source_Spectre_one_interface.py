import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter import simpledialog

import os

from source_Project_reader import SpOneReader


class SpectreOneInterface(tk.Frame):
    def __init__(self, parent, spectre_path):
        super().__init__(parent)

        self.parent_frame = parent
        self.spectre_path = spectre_path

        self.parent_frame.geometry('850x790')
        self.parent_frame.resizable(width=True, height=True)

        self.parts_count_db = {
            'phi': 1,
            'theta': 1,
            'energy': 1,
            'starts': 1
        }

    def sp_one_constructor(self):
        self.row = 0

        self.cf = ScrolledWidget(self, (800, 700))
        self.cf.grid(row=3, columnspan=12, pady=5, sticky="NWSE", rowspan=100)

        # self.energy_frame_entry = ttk.Frame(cf.frame)
        # self.energy_frame_entry.grid(row=phi_row + 1, column=0, columnspan=12, sticky="NWSE")

        self.frame_description = ttk.LabelFrame(self.cf.frame, text='Редактор спектра')
        self.frame_description.grid(row=3, column=0, columnspan=12, rowspan=13, sticky="NWSE")

        # commentary
        commentary_label = tk.Label(self.frame_description, text='Комментарий', justify='left')
        commentary_label.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        self.spectre_note_val = tk.StringVar()
        self.spectre_note_val.set('')
        self.spectre_note = tk.Entry(self.frame_description, textvariable=self.spectre_note_val, width=80)
        self.spectre_note.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        # number
        num_label = tk.Label(self.frame_description, text='Номер спектра', justify='left')
        num_label.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        self.spectre_number_val = tk.StringVar()
        self.spectre_number_val.set('')
        self.spectre_number = tk.Entry(self.frame_description, textvariable=self.spectre_number_val, width=10)
        self.spectre_number.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        # Power
        p_t = 'Мощность спектра (шт/см\u00b2/с)- для поверхностных, (шт/см\u00b3/с)- для объемных'
        power_label = tk.Label(self.frame_description, text=p_t, justify='left')
        power_label.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        self.spectre_power_val = tk.StringVar()
        self.spectre_power_val.set('1')
        self.spectre_power = tk.Entry(self.frame_description, textvariable=self.spectre_power_val, width=10)
        self.spectre_power.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        # # SP_type
        # t_t = 'Тип спектра (0-фиксированный, 1-разыгрывание, 3-от координат, 4-от времени, 5-с учетом ослабления)'
        # type_label = tk.Label(self.frame_description, text=t_t, justify='left')
        # type_label.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        # self.row += 1

        self.spectre_type_val = tk.StringVar()
        self.spectre_type_val.set('1')
        # self.spectre_type_entry = tk.Entry(self.frame_description, textvariable=self.spectre_type_val, width=10,
        #                                    state='readonly')
        # self.spectre_type_entry.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        # self.row += 1

        # part_count
        p = 'Число частиц (запускаемых на каждом шаге)'
        pcount_label = tk.Label(self.frame_description, text=p, justify='left')
        pcount_label.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        self.part_count_val = tk.StringVar()
        self.part_count_val.set('0')
        self.part_count = tk.Entry(self.frame_description, textvariable=self.part_count_val, width=10, state='readonly')
        self.part_count.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        # number of elements
        p = 'Количество элементов по fi, theta, энергии (укажите через пробел)'
        elem_label = tk.Label(self.frame_description, text=p, justify='left')
        elem_label.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        self.elem_count_val = tk.StringVar()
        self.elem_count_val.set('0 0 0')
        self.elem_count_val.trace('w',
                                  lambda name, index, mode: self.__change_count_callback())

        self.elem_count = tk.Entry(self.frame_description, textvariable=self.elem_count_val, width=10, state='readonly')
        self.elem_count.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        # starts count
        p = 'Число частиц (сколько раз вызывается спектр)'
        pcount_label = tk.Label(self.frame_description, text=p, justify='left')
        pcount_label.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        self.starts_count_val = tk.StringVar()
        self.starts_count_val.set('1')
        self.starts_count_val.trace('w',
                                    lambda name, index, mode: self.__change_count_callback())

        self.starts_count = tk.Entry(self.frame_description, textvariable=self.starts_count_val, width=10,
                                     state='normal')
        self.starts_count.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        # phi type
        p = 'Тип спектра по fi'
        phy_label = tk.Label(self.frame_description, text=p, justify='left')
        phy_label.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.row += 1

        p_t = ['0', '1', '3']
        combobox_values = ['детерминированный', 'равномерный', 'нормальное распределение']
        self.phi_decode = dict(zip(combobox_values, p_t))

        self.phi_type_cobbobox = ttk.Combobox(self.frame_description, value=[val for val in combobox_values], width=20,
                                              state='readonly')
        self.phi_type_cobbobox.grid(row=self.row, column=0, columnspan=12, sticky='NW')
        self.phi_type_cobbobox.set('Тип спектра fi')

        self.bind_class(self.phi_type_cobbobox, "<<ComboboxSelected>>", self.__phi_constructor)
        self.row += 1

        # theta type
        p = 'Тип спектра по theta'
        theta_label = tk.Label(self.frame_description, text=p, justify='left')
        theta_label.grid(row=18, column=0, columnspan=12, sticky='NW')
        self.row += 1

        t_num = ['0', '1', '-1', '3']
        combobox_values = ['детерминированный', 'равномерный', 'равномерный по площади', 'нормальное распределение']
        self.theta_decode = dict(zip(combobox_values, t_num))
        self.theta_type_cobbobox = ttk.Combobox(self.frame_description, value=[val for val in combobox_values],
                                                width=20,
                                                state='readonly')
        self.theta_type_cobbobox.grid(row=19, column=0, columnspan=12, sticky='NW')
        self.theta_type_cobbobox.set('Тип спектра theta')

        self.bind_class(self.theta_type_cobbobox, "<<ComboboxSelected>>", self.__theta_constructor)
        self.row += 1

        # energy type
        p = 'Тип спектра по энергии'
        energy_label = tk.Label(self.frame_description, text=p, justify='left')
        energy_label.grid(row=28, column=0, columnspan=12, sticky='NW')
        self.row += 1

        e_num = ['0', '1', '2', '3']
        combobox_values = ['детерминированный', 'равномерный', 'по распределению', 'нормальное распределение']
        self.energy_decode = dict(zip(combobox_values, e_num))
        self.energy_type_cobbobox = ttk.Combobox(self.frame_description, value=[val for val in combobox_values],
                                                 width=20,
                                                 state='readonly')
        self.energy_type_cobbobox.grid(row=29, column=0, columnspan=12, sticky='NW')
        self.energy_type_cobbobox.set('Тип спектра energy')

        self.bind_class(self.energy_type_cobbobox, "<<ComboboxSelected>>", self.__energy_constructor)
        self.row += 1

    def __energy_constructor(self, event):
        energy_row = 0
        try:
            self.energy_frame_description.destroy()
            self.energy_frame_entry.destroy()
        except:
            pass

        cb = self.energy_decode[self.energy_type_cobbobox.get()]

        self.energy_frame_description = ttk.Frame(self.frame_description)
        self.energy_frame_description.grid(row=30, column=0, columnspan=12, sticky="NWSE", pady=5)
        self.row += 1
        energy_row += 1

        if cb == '0' or cb == '2':
            # phi levels
            p = 'Количество уровней по энергии'
            phy_label = tk.Label(self.energy_frame_description, text=p, justify='left')
            phy_label.grid(row=energy_row, column=0, columnspan=12, sticky='NW')
            energy_row += 1

            self.energy_levels_val = tk.StringVar()
            self.energy_levels_val.trace('w',
                                         lambda name, index, mode: self.__change_count_callback(True))

            self.energy_levels_val.set('0')
            self.energy_levels = tk.Entry(self.energy_frame_description, textvariable=self.energy_levels_val, width=10)
            self.energy_levels.grid(row=energy_row, column=0, columnspan=2, sticky='NW')
            tk.Label(self.energy_frame_description, text='Нажмите Enter для применения').grid(row=energy_row, column=3,
                                                                                              columnspan=7, sticky='NW')
            energy_row += 1

            self.energy_levels.bind('<Return>', lambda _, r=energy_row: self.__energy_entry_constructor(r, _))

        elif cb == '1':
            a = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{a[0]} {a[1]} {2}')
            self.parts_count_db['energy'] = 1

            self.energy_frame_entry = ttk.Frame(self.energy_frame_description)
            self.energy_frame_entry.grid(row=energy_row + 1, column=0, columnspan=12, sticky="NWSE")

            p = 'Значение(от до) (МэВ)'
            phy_label = tk.Label(self.energy_frame_entry, text=p, justify='left')
            phy_label.grid(row=0, column=0, columnspan=12, sticky='NW')

            self.energy_angles_val = [tk.StringVar() for _ in range(2)]

            self.energy_angles_entry = []

            for i in range(2):
                self.energy_angles_entry.append(
                    tk.Entry(self.energy_frame_entry, width=14, textvariable=self.energy_angles_val[i]))
                self.energy_angles_entry[i].grid(row=1 + i, column=0, sticky='NW', padx=3, pady=3)

        elif cb == '3':
            a = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{a[0]} {a[1]} {2}')
            self.parts_count_db['energy'] = 1

            self.energy_angles_entry = []
            self.energy_angles_val = [tk.StringVar() for _ in range(2)]

            self.energy_frame_entry = ttk.Frame(self.energy_frame_description)
            self.energy_frame_entry.grid(row=energy_row + 1, column=0, columnspan=12, sticky="NWSE")

            p = 'Мат.ожидание (МэВ)'
            M_label = tk.Label(self.energy_frame_entry, text=p, justify='left')
            M_label.grid(row=0, column=0, columnspan=12, sticky='NW')

            self.energy_angles_entry.append(
                tk.Entry(self.energy_frame_entry, width=14, textvariable=self.energy_angles_val[0]))
            self.energy_angles_entry[0].grid(row=1, column=0, sticky='NW', padx=3, pady=3)

            p = 'Дисперсия(корень) (МэВ)'
            D_label = tk.Label(self.energy_frame_entry, text=p, justify='left')
            D_label.grid(row=2, column=0, columnspan=12, sticky='NW')

            self.energy_angles_entry.append(
                tk.Entry(self.energy_frame_entry, width=14, textvariable=self.energy_angles_val[1]))
            self.energy_angles_entry[1].grid(row=3, column=0, sticky='NW', padx=3, pady=3)

    def __theta_constructor(self, event):
        theta_row = 0
        try:
            self.theta_frame_description.destroy()
            self.theta_frame_entry.destroy()
        except:
            pass

        cb = self.theta_decode[self.theta_type_cobbobox.get()]

        self.theta_frame_description = ttk.Frame(self.frame_description)
        self.theta_frame_description.grid(row=20, column=0, columnspan=12, sticky="NWSE", pady=5)
        self.row += 1
        theta_row += 1

        if cb == '0':
            # phi levels
            p = 'Количество уровней по theta'
            phy_label = tk.Label(self.theta_frame_description, text=p, justify='left')
            phy_label.grid(row=theta_row, column=0, columnspan=12, sticky='NW')
            theta_row += 1

            self.theta_levels_val = tk.StringVar()
            self.theta_levels_val.set('0')
            self.theta_levels = tk.Entry(self.theta_frame_description, textvariable=self.theta_levels_val, width=10)
            self.theta_levels.grid(row=theta_row, column=0, columnspan=2, sticky='NW')
            tk.Label(self.theta_frame_description, text='Нажмите Enter для применения').grid(row=theta_row, column=2,
                                                                                             columnspan=7, sticky='NW')
            theta_row += 1

            self.theta_levels.bind('<Return>', lambda _, r=theta_row: self.__theta_entry_constructor(r, _))

        elif cb == '1' or cb == '-1':
            a = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{a[0]} {2} {a[2]}')
            self.parts_count_db['theta'] = 1

            self.theta_frame_entry = ttk.Frame(self.theta_frame_description)
            self.theta_frame_entry.grid(row=theta_row + 1, column=0, columnspan=12, sticky="NWSE")

            p = 'Значение (от до) (градусы)'
            phy_label = tk.Label(self.theta_frame_entry, text=p, justify='left')
            phy_label.grid(row=0, column=0, columnspan=12, sticky='NW')

            self.theta_angles_val = [tk.StringVar() for _ in range(2)]

            self.theta_angles_entry = []

            for i in range(2):
                self.theta_angles_entry.append(
                    tk.Entry(self.theta_frame_entry, width=14, textvariable=self.theta_angles_val[i]))
                self.theta_angles_entry[i].grid(row=1 + i, column=0, sticky='NW', padx=3, pady=3)

        elif cb == '3':
            a = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{a[0]} {2} {a[2]}')
            self.parts_count_db['theta'] = 1

            self.theta_angles_entry = []
            self.theta_angles_val = [tk.StringVar() for _ in range(2)]

            self.theta_frame_entry = ttk.Frame(self.theta_frame_description)
            self.theta_frame_entry.grid(row=theta_row + 1, column=0, columnspan=12, sticky="NWSE")

            p = 'Мат.ожидание (МэВ)'
            M_label = tk.Label(self.theta_frame_entry, text=p, justify='left')
            M_label.grid(row=0, column=0, columnspan=12, sticky='NW')

            self.theta_angles_entry.append(
                tk.Entry(self.theta_frame_entry, width=14, textvariable=self.theta_angles_val[0]))
            self.theta_angles_entry[0].grid(row=1, column=0, sticky='NW', padx=3, pady=3)

            p = 'Дисперсия(корень) (МэВ)'
            D_label = tk.Label(self.theta_frame_entry, text=p, justify='left')
            D_label.grid(row=2, column=0, columnspan=12, sticky='NW')

            self.theta_angles_entry.append(
                tk.Entry(self.theta_frame_entry, width=14, textvariable=self.theta_angles_val[1]))
            self.theta_angles_entry[1].grid(row=3, column=0, sticky='NW', padx=3, pady=3)

    def __phi_constructor(self, event):
        phi_row = 0
        try:
            self.phi_frame_description.destroy()
            self.phi_frame_description.grid_forget()
            self.phi_frame_entry.destroy()
            self.phi_frame_entry.grid_forget()

        except:
            pass

        cb = self.phi_decode[self.phi_type_cobbobox.get()]

        self.phi_frame_description = ttk.Frame(self.frame_description)
        self.phi_frame_description.grid(row=14, column=0, columnspan=12, sticky="NWSE", pady=5)
        self.row += 1

        if cb == '0':
            # phi levels
            p = 'Количество уровней по fi'
            phy_label = tk.Label(self.phi_frame_description, text=p, justify='left')
            phy_label.grid(row=phi_row, column=0, columnspan=12, sticky='NW')
            phi_row += 1

            self.phi_levels_val = tk.StringVar()
            self.phi_levels_val.set('0')
            self.phi_levels = tk.Entry(self.phi_frame_description, textvariable=self.phi_levels_val, width=10)
            self.phi_levels.grid(row=phi_row, column=0, columnspan=2, sticky='NW')
            tk.Label(self.phi_frame_description, text='Нажмите Enter для применения').grid(row=phi_row, column=2,
                                                                                           columnspan=7, sticky='NW')
            phi_row += 1

            self.phi_levels.bind('<Return>', lambda _, r=phi_row: self.__phi_entry_constructor(r, _))

        elif cb == '1':

            a = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{2} {a[1]} {a[2]}')
            self.parts_count_db['phi'] = 1

            self.phi_frame_entry = ttk.Frame(self.phi_frame_description)
            self.phi_frame_entry.grid(row=phi_row + 1, column=0, columnspan=12, sticky="NWSE")

            p = 'Значение (от до) (градусы)'
            phy_label = tk.Label(self.phi_frame_entry, text=p, justify='left')
            phy_label.grid(row=0, column=0, columnspan=12, sticky='NW')

            self.phi_angles_val = [tk.StringVar() for _ in range(2)]

            self.phi_angles_entry = []

            for i in range(2):
                self.phi_angles_entry.append(
                    tk.Entry(self.phi_frame_entry, width=14, textvariable=self.phi_angles_val[i]))
                self.phi_angles_entry[i].grid(row=1 + i, column=0, sticky='NW', padx=3, pady=3)

        elif cb == '3':
            a = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{2} {a[1]} {a[2]}')
            self.parts_count_db['phi'] = 1

            self.phi_angles_entry = []
            self.phi_angles_val = [tk.StringVar() for _ in range(2)]

            self.phi_frame_entry = ttk.Frame(self.phi_frame_description)
            self.phi_frame_entry.grid(row=phi_row + 1, column=0, columnspan=12, sticky="NWSE")

            p = 'Мат.ожидание (МэВ)'
            M_label = tk.Label(self.phi_frame_entry, text=p, justify='left')
            M_label.grid(row=0, column=0, columnspan=12, sticky='NW')

            self.phi_angles_entry.append(
                tk.Entry(self.phi_frame_entry, width=14, textvariable=self.phi_angles_val[0]))
            self.phi_angles_entry[0].grid(row=1, column=0, sticky='NW', padx=3, pady=3)

            p = 'Дисперсия(корень) (МэВ)'
            D_label = tk.Label(self.phi_frame_entry, text=p, justify='left')
            D_label.grid(row=2, column=0, columnspan=12, sticky='NW')

            self.phi_angles_entry.append(
                tk.Entry(self.phi_frame_entry, width=14, textvariable=self.phi_angles_val[1]))
            self.phi_angles_entry[1].grid(row=3, column=0, sticky='NW', padx=3, pady=3)

    def __energy_entry_constructor(self, r, event):
        try:
            count = int(self.energy_levels_val.get())
            self.parts_count_db['energy'] = count

            a = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{a[0]} {a[1]} {count}')
        except:
            return

        phi_row = r

        # cf = ScrolledWidget(self.energy_frame_description, (300, 500))
        # cf.grid(row=3, columnspan=12, pady=5)

        self.energy_frame_entry = ttk.Frame(self.energy_frame_description)
        self.energy_frame_entry.grid(row=phi_row + 1, column=0, columnspan=12, sticky="NWSE")

        if self.energy_decode[self.energy_type_cobbobox.get()] == '2':
            self.parts_count_db['energy'] = 1
            p = 'Энергия(МэВ) от	до доля(не нормируется)'

            self.energy_angles_entry_2 = []
            self.energy_angles_val_2 = [tk.StringVar() for _ in range(count)]

            part_count_label = tk.Label(self.energy_frame_entry, text='Заполните ячейки', justify='center')
            part_count_label.grid(row=2 + count, column=3, padx=3, pady=3)


        else:
            p = 'Значения энергии(МэВ), доля(не нормируется)'

            part_count_label = tk.Label(self.energy_frame_entry, text='Заполните ячейки', justify='center')
            part_count_label.grid(row=2 + count, column=3, padx=3, pady=3)

        energy_label = tk.Label(self.energy_frame_entry, text=p, justify='left')
        energy_label.grid(row=0, column=0, columnspan=12, sticky='NW')

        self.energy_angles_val = [tk.StringVar() for _ in range(count)]
        self.energy_parts_val = [tk.StringVar() for _ in range(count)]

        self.energy_angles_entry = []
        self.energy_parts_entry = []

        if self.energy_decode[self.energy_type_cobbobox.get()] == '2':
            for i in range(count):
                self.energy_angles_entry.append(
                    tk.Entry(self.energy_frame_entry, width=14, textvariable=self.energy_angles_val[i]))
                self.energy_angles_entry[i].grid(row=1 + i, column=0, sticky='NW', padx=3, pady=3)

                self.energy_angles_entry_2.append(
                    tk.Entry(self.energy_frame_entry, width=14, textvariable=self.energy_angles_val_2[i]))
                self.energy_angles_entry_2[i].grid(row=1 + i, column=1, sticky='NW', padx=3, pady=3)

                self.energy_parts_entry.append(
                    tk.Entry(self.energy_frame_entry, width=14, textvariable=self.energy_parts_val[i]))
                self.energy_parts_entry[i].grid(row=1 + i, column=3, sticky='NW', padx=3, pady=3)

                self.energy_parts_val[i].trace('w',
                                               lambda name, index, mode: self.__part_callback(part_count_label, count,
                                                                                              self.energy_parts_val))

                self.__add_delete_button(self.energy_frame_entry, 1 + i, 4,
                                         [self.energy_angles_entry[i], self.energy_parts_entry[i],
                                          self.energy_angles_entry_2[i]], 'energy')

        else:
            for i in range(count):
                self.energy_angles_entry.append(
                    tk.Entry(self.energy_frame_entry, width=14, textvariable=self.energy_angles_val[i]))
                self.energy_angles_entry[i].grid(row=1 + i, column=0, sticky='NW', padx=3, pady=3)

                self.energy_parts_entry.append(
                    tk.Entry(self.energy_frame_entry, width=14, textvariable=self.energy_parts_val[i]))
                self.energy_parts_entry[i].grid(row=1 + i, column=3, sticky='NW', padx=3, pady=3)

                self.energy_parts_val[i].trace('w',
                                               lambda name, index, mode: self.__part_callback(part_count_label, count,
                                                                                              self.energy_parts_val))

                self.__add_delete_button(self.energy_frame_entry, 1 + i, 4,
                                         [self.energy_angles_entry[i], self.energy_parts_entry[i]], 'energy')

        self.__change_count_callback()

    def __theta_entry_constructor(self, r, event):
        try:
            count = int(self.theta_levels_val.get())
            self.parts_count_db['theta'] = count

            a = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{a[0]} {count} {a[2]}')

        except:
            return

        phi_row = r

        # cf = ScrolledWidget(self.theta_frame_description)
        # cf.grid(row=3, columnspan=12, pady=5)

        self.theta_frame_entry = ttk.Frame(self.theta_frame_description)
        self.theta_frame_entry.grid(row=phi_row + 1, column=0, columnspan=12, sticky="NWSE")

        p = 'Значения угла(градусы), доля(не нормируется)'
        theta_label = tk.Label(self.theta_frame_entry, text=p, justify='left')
        theta_label.grid(row=0, column=0, columnspan=12, sticky='NW')

        self.theta_angles_val = [tk.StringVar() for _ in range(count)]
        self.theta_parts_val = [tk.StringVar() for _ in range(count)]

        self.theta_angles_entry = []
        self.theta_parts_entry = []

        part_count_label = tk.Label(self.theta_frame_entry, text='Заполните ячейки', justify='center')
        part_count_label.grid(row=2 + count, column=1, padx=3, pady=3)

        for i in range(count):
            self.theta_angles_entry.append(
                tk.Entry(self.theta_frame_entry, width=14, textvariable=self.theta_angles_val[i]))
            self.theta_angles_entry[i].grid(row=1 + i, column=0, sticky='NW', padx=3, pady=3)

            self.theta_parts_entry.append(
                tk.Entry(self.theta_frame_entry, width=14, textvariable=self.theta_parts_val[i]))
            self.theta_parts_entry[i].grid(row=1 + i, column=1, sticky='NW', padx=3, pady=3)

            self.theta_parts_val[i].trace('w',
                                          lambda name, index, mode: self.__part_callback(part_count_label, count,
                                                                                         self.theta_parts_val))

            self.__add_delete_button(self.theta_frame_entry, 1 + i, 4,
                                     [self.theta_angles_entry[i], self.theta_parts_entry[i]], 'theta')

        self.__change_count_callback()

    def __phi_entry_constructor(self, r, event):
        try:
            count = int(self.phi_levels_val.get())
            self.parts_count_db['phi'] = count

            a = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{count} {a[1]} {a[2]}')
        except:
            return

        phi_row = r

        # cf = ScrolledWidget(self.phi_frame_description)
        # cf.grid(row=2, columnspan=12, pady=5)

        self.phi_frame_entry = ttk.Frame(self.phi_frame_description)
        self.phi_frame_entry.grid(row=phi_row + 1, column=0, columnspan=12, sticky="NWSE")

        p = 'Значения угла(градусы), доля(не нормируется)'
        phy_label = tk.Label(self.phi_frame_entry, text=p, justify='left')
        phy_label.grid(row=0, column=0, columnspan=12, sticky='NW')

        self.phi_angles_val = [tk.StringVar() for _ in range(count)]
        self.phi_parts_val = [tk.StringVar() for _ in range(count)]

        self.phi_angles_entry = []
        self.phi_parts_entry = []

        part_count_label = tk.Label(self.phi_frame_entry, text='Заполните ячейки', justify='center')
        part_count_label.grid(row=2 + count, column=1, padx=3, pady=3)

        for i in range(count):
            self.phi_angles_entry.append(tk.Entry(self.phi_frame_entry, width=14, textvariable=self.phi_angles_val[i]))
            self.phi_angles_entry[i].grid(row=1 + i, column=0, sticky='NW', padx=3, pady=3)

            self.phi_parts_entry.append(tk.Entry(self.phi_frame_entry, width=14, textvariable=self.phi_parts_val[i]))
            self.phi_parts_entry[i].grid(row=1 + i, column=1, sticky='NW', padx=3, pady=3)

            self.phi_parts_val[i].trace('w',
                                        lambda name, index, mode: self.__part_callback(part_count_label, count,
                                                                                       self.phi_parts_entry))

            self.__add_delete_button(self.phi_frame_entry, 1 + i, 4,
                                     [self.phi_angles_entry[i], self.phi_parts_entry[i]], 'phi')

        self.__change_count_callback()

    def data_load(self):
        self.sp_one_constructor()
        data_struct = SpOneReader(self.spectre_path)
        data_struct.start_read()

        self.spectre_note_val.set(data_struct.description)
        self.spectre_number_val.set(data_struct.sp_number)
        self.spectre_power_val.set(data_struct.sp_power)
        self.spectre_type_val.set('1')
        self.part_count_val.set(data_struct.sp_part_count)
        self.elem_count_val.set(f'{data_struct.phi_count} {data_struct.theta_count} {data_struct.energy_count}')

        '''PHI'''
        [self.phi_type_cobbobox.set(key) for key in self.phi_decode.keys() if
         self.phi_decode[key] == str(data_struct.phi_type)]
        self.__phi_constructor(None)

        if data_struct.phi_type == 0:
            self.phi_levels_val.set(str(data_struct.phi_count))

        self.__phi_entry_constructor(2, None)
        for i in range(data_struct.phi_count):
            self.phi_angles_val[i].set(str(data_struct.phi_angles[i]))
            if data_struct.phi_type == 0:
                self.phi_parts_val[i].set(str(data_struct.phi_parts[i]))

        if data_struct.phi_type == 0:
            self.phi_parts_val[-1].set(str(data_struct.phi_parts[-1]))

        '''Theta'''
        [self.theta_type_cobbobox.set(key) for key in self.theta_decode.keys() if
         self.theta_decode[key] == str(data_struct.theta_type)]
        self.__theta_constructor(None)

        if data_struct.theta_type == 0:
            self.theta_levels_val.set(str(data_struct.theta_count))

        self.__theta_entry_constructor(2, None)
        for i in range(data_struct.theta_count):
            self.theta_angles_val[i].set(str(data_struct.theta_angles[i]))
            if data_struct.theta_type == 0:
                self.theta_parts_val[i].set(str(data_struct.theta_parts[i]))

        '''Energy'''
        [self.energy_type_cobbobox.set(key) for key in self.energy_decode.keys() if
         self.energy_decode[key] == str(data_struct.energy_type)]
        self.__energy_constructor(None)

        if data_struct.energy_type == 0 or data_struct.energy_type == 2:
            self.energy_levels_val.set(str(data_struct.energy_count))

        self.__energy_entry_constructor(2, None)
        for i in range(data_struct.energy_count):
            if data_struct.energy_type == 0:
                self.energy_angles_val[i].set(str(data_struct.energy_angles[i]))
                self.energy_parts_val[i].set(str(data_struct.energy_parts[i]))
            elif data_struct.energy_type == 2:
                self.energy_angles_val[i].set(str(data_struct.energy_angles[i][0]))
                self.energy_angles_val_2[i].set(str(data_struct.energy_angles[i][1]))
                self.energy_parts_val[i].set(str(data_struct.energy_parts[i]))
            else:
                self.energy_angles_val[i].set(str(data_struct.energy_angles[i]))

    def destroy_widget(self):

        self.cf.canvas.grid_remove()
        self.cf.canvas.destroy()

        self.cf.grid_remove()
        self.cf.destroy()

    def __add_delete_button(self, parent, row, column, delete_items, count_type):

        button = tk.Button(parent, text='-',
                           command=lambda: self.__delete_entry(button, delete_items, count_type, row - 1))
        button.grid(row=row, column=column, sticky='W')

    def __delete_entry(self, item, delete_items, count_type, index):

        try:
            item.grid_remove()
            item.destroy()

            delete_items[0].grid_remove()
            delete_items[0].destroy()

            delete_items[1].grid_remove()
            delete_items[1].destroy()

            delete_items[2].grid_remove()
            delete_items[2].destroy()

        except:
            pass

        if count_type == 'energy':
            try:
                self.energy_parts_entry.pop(index)
                self.energy_angles_entry.pop(index)
                self.energy_angles_entry_2.pop(index)
                self.energy_parts_val.pop(index)
                self.energy_angles_val.pop(index)
                self.energy_angles_val_2.pop(index)
            except:
                pass
            self.energy_levels_val.set(str(len(self.energy_parts_entry)))

            counts = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{counts[0]} {counts[1]} {self.energy_levels_val.get()}')

        if count_type == 'phi':
            try:
                self.phi_parts_entry.pop(index)
                self.phi_angles_entry.pop(index)
                self.phi_parts_val.pop(index)
                self.phi_angles_val.pop(index)
                self.phi_parts_val[index].destroy()
                self.phi_angles_val[index].destroy()

            except:
                pass
            self.phi_levels_val.set(str(len(self.phi_parts_entry)))

            counts = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{self.phi_levels_val.get()} {counts[1]} {counts[2]}')

        if count_type == 'theta':
            try:
                self.theta_parts_entry.pop(index)
                self.theta_angles_entry.pop(index)
                self.theta_parts_val.pop(index)
                self.theta_angles_val.pop(index)
            except:
                pass
            self.theta_levels_val.set(str(len(self.theta_parts_entry)))

            counts = self.elem_count_val.get().split()
            self.elem_count_val.set(f'{counts[0]} {self.theta_levels_val.get()} {counts[2]}')

    def __change_count_callback(self, set=False):
        try:
            self.parts_count_db['starts'] = int(self.starts_count_val.get())
        except:
            return

        # counts = self.elem_count_val.get().split()
        try:
            a = self.parts_count_db['energy']

            b = self.parts_count_db['phi']

            c = self.parts_count_db['theta']

            starts = self.parts_count_db['starts']
        except:
            return

        # print(self.parts_count_db.items())

        self.part_count_val.set(f'{a * b * c * starts}')
        if set:
            self.elem_count_val.set(f'{b} {c} {a}')

    def __part_callback(self, label, count, array):
        sum = 0
        try:
            for i in range(count):
                sum += eval(array[i].get())
            label['text'] = 'сумма: {:.4g}'.format(sum)
        except:
            label['text'] = 'Заполните ячейки'

    def save(self):

        if self.check_data_in_entry() == -1:
            mb.showerror('Ошибка сохранения', 'Заполнены не все данные. Проверьте консоль вывода')
            return

        out = ''

        out += f'{self.spectre_note_val.get()}\n'
        out += 'Номер спектра\n'
        out += f'{self.spectre_number_val.get()}\n'
        out += 'Мощность спектра (шт/см**2/с)- для поверхностных, (шт/см**3/с)- для объемных\n'
        out += f'{self.spectre_power_val.get()}\n'
        out += 'Тип спектра (0-фиксированный, 1-разыгрывание, 2-список)\n'
        out += '1\n'
        out += 'Число частиц (запускаемых на каждом шаге)\n'
        out += f'{self.part_count_val.get()}\n'
        out += f'Количество элементов по fi, theta, энергии\n'
        out += f'{self.elem_count_val.get()}\n'
        out += f'Число частиц (сколько раз вызывается спектр)\n'
        out += f'{self.starts_count.get()}\n'

        # phi
        out += f'Тип спектра по fi (0-детерминированный,1-равномерный,3-нормальное распределение)\n'
        out += f'{self.phi_decode[self.phi_type_cobbobox.get()]}\n'

        if int(self.phi_decode[self.phi_type_cobbobox.get()]) == 0:
            out += 'Количество уровней по fi\n'
            out += f'{self.phi_levels_val.get()}\n'
            out += 'Значения угла(градусы), доля(не нормируется)\n'
            for i in range(len(self.phi_angles_val)):
                out += self.phi_angles_val[i].get() + '\t' + self.phi_parts_val[i].get() + '\n'

        elif int(self.phi_decode[self.phi_type_cobbobox.get()]) == 1:
            out += 'Значение (от до) (градусы)\n'
            for i in range(len(self.phi_angles_val)):
                out += f'{self.phi_angles_val[i].get()}\n'

        elif int(self.phi_decode[self.phi_type_cobbobox.get()]) == 3:
            out += 'Мат.ожидание (градусы)\n'
            out += f'{self.phi_angles_val[0].get()}\n'
            out += 'Дисперсия(корень) (градусы)\n'
            out += f'{self.phi_angles_val[1].get()}\n'

        # theta
        out += f'Тип спектра по theta (0-детерминированный,1-равномерный,-1 -равномерный по площади,3-нормальное распределение)\n'
        out += f'{self.theta_decode[self.theta_type_cobbobox.get()]}\n'

        if int(self.theta_decode[self.theta_type_cobbobox.get()]) == 0:
            out += 'Количество уровней по theta\n'
            out += f'{self.theta_levels_val.get()}\n'
            out += 'Значения угла(градусы), доля(не нормируется)\n'
            for i in range(len(self.theta_angles_val)):
                out += self.theta_angles_val[i].get() + '\t' + self.theta_parts_val[i].get() + '\n'


        elif int(self.theta_decode[self.theta_type_cobbobox.get()]) == 1 or int(
                self.theta_decode[self.theta_type_cobbobox.get()]) == -1:
            out += 'Значение (от до) (градусы)\n'
            for i in range(len(self.theta_angles_val)):
                out += f'{self.theta_angles_val[i].get()}\n'

        elif int(self.theta_decode[self.theta_type_cobbobox.get()]) == 3:
            out += 'Мат.ожидание (градусы)\n'
            out += f'{self.theta_angles_val[0].get()}\n'
            out += 'Дисперсия(корень) (градусы)\n'
            out += f'{self.theta_angles_val[1].get()}\n'

        # energy
        out += f'Тип спектра по энергии (0-детерминированный,1-равномерный,2-по распределению,3-нормальное распределение)\n'
        out += f'{self.energy_decode[self.energy_type_cobbobox.get()]}\n'

        if int(self.energy_decode[self.energy_type_cobbobox.get()]) == 0:
            out += 'Количество уровней по энергии\n'
            out += f'{self.energy_levels_val.get()}\n'
            out += 'Значения энергии(МэВ), доля(не нормируется)\n'
            for i in range(len(self.energy_angles_val)):
                out += self.energy_angles_val[i].get() + '\t' + self.energy_parts_val[i].get() + '\n'

        elif int(self.energy_decode[self.energy_type_cobbobox.get()]) == 2:
            out += 'Число энергий в спектре\n'
            out += f'{self.energy_levels_val.get()}\n'
            out += 'Энергия(МэВ) от	до доля(не нормируется)\n'
            for i in range(len(self.energy_angles_val)):
                out += self.energy_angles_val[i].get() + '\t' + self.energy_angles_val_2[i].get() + \
                       '\t' + self.energy_parts_val[i].get() + '\n'

        elif int(self.energy_decode[self.energy_type_cobbobox.get()]) == 1:
            out += 'Значение(от до) (МэВ)\n'
            for i in range(len(self.energy_angles_val)):
                out += f'{self.energy_angles_val[i].get()}\n'

        elif int(self.energy_decode[self.energy_type_cobbobox.get()]) == 3:
            out += 'Мат.ожидание (градусы)\n'
            out += f'{self.energy_angles_val[0].get()}\n'
            out += 'Дисперсия(корень) (градусы)\n'
            out += f'{self.energy_angles_val[1].get()}\n'

        # print(out)
        return out

    def check_data_in_entry(self):
        try:
            float(self.spectre_number_val.get())
        except:
            print('Нечитаемый символ/не задан номер спектра')
            return -1
        try:
            float(self.spectre_power_val.get())
        except:
            print('Нечитаемый символ/не задана мощность спетра')
            return -1

        return 1


class ScrolledWidget(tk.Frame):
    def __init__(self, parent, size=(300, 100)):
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, width=size[0], height=size[1])
        self.frame = tk.Frame(self.canvas, borderwidth=1)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.mw_scroll = self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both")
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

    def _on_mousewheel(self, event):
        if self.vsb.get() != (0., 1.):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def populate(self):
        '''Put in some fake data'''
        for row in range(100):
            tk.Label(self.frame, text="%s" % row, width=3, borderwidth="1",
                     relief="solid").grid(row=row, column=0)
            t = "this is the second column for row %s" % row
            tk.Label(self.frame, text=t).grid(row=row, column=1)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


if __name__ == '__main__':
    root = tk.Tk()

    root.geometry('1000x1000')

    sw = ScrolledWidget(root, (200, 200))
    sw.pack(fill='both')

    sw.populate()

    root.mainloop()
