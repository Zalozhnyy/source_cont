import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd

import os
import shutil
import pickle

from source_Dialogs import SelectSpectreToView
from source_Project_reader import DataParser
from source_SpectreConfigure import SpectreConfigure


class StandardizedSourceMainInterface(tk.Frame):
    """
    Класс, взаимодействующий с главным интерфейсом источников.

    В данном фрейме находятся все опции взаимодействия пользователя с интерфейсом выбора спектра,
    его редактирования, создания.

    На вход принимает базу данных, в которую будут отправлены новые выбранные значения.
    """

    def __init__(self, parent, path, data_object, name, first_key, second_key):
        super().__init__(parent)

        self.parent_widget = parent
        self.path = path

        self.pack()

        self.db = data_object
        self.db_name = name
        self.fk = first_key
        self.sk = second_key

        self.row = 1
        self.button_width = 20

        self.spectre_name_values = ['Файл не выбран']
        self.spectre_number_values = ['--']
        self.spectre_type_values = ['--']

        self._check_db_for_values()
        self._init_ui()

    def change_starts_list_values(self, name_list, number_list, type_list):

        self.spectre_name_values = name_list
        self.spectre_number_values = number_list
        self.spectre_type_values = type_list

    def _init_ui(self):
        e = self.db[self.db_name].get_last_level_data(self.fk, self.sk, 'energy_type')
        energy_type_label = tk.Label(self, text=e, justify='left')
        energy_type_label.grid(row=0, column=0, columnspan=2)

        spectre_name_label_description = tk.Label(self, text='Имя спектра', justify='center')
        spectre_number_label_description = tk.Label(self, text='Номер спектра', justify='center')
        spectre_type_label_description = tk.Label(self, text='Тип спектра', justify='center')

        spectre_name_label_description.grid(row=self.row, column=0, padx=3, pady=3)
        spectre_number_label_description.grid(row=self.row, column=1, padx=3, pady=3)
        spectre_type_label_description.grid(row=self.row, column=2, padx=3, pady=3)

        self.row += 1

        self.spectre_name_label = tk.Label(self, text='')
        self.spectre_number_label = tk.Label(self, text='')
        self.spectre_type_label = tk.Label(self, text='')

        self.spectre_name_label.grid(row=self.row, column=0, padx=3, pady=3, rowspan=10)
        self.spectre_number_label.grid(row=self.row, column=1, padx=3, pady=3, rowspan=10)
        self.spectre_type_label.grid(row=self.row, column=2, padx=3, pady=3, rowspan=10)

        self._init_buttons()

        self._set_spectre_data_to_interface()

    def _set_spectre_data_to_interface(self):
        name = '\n'.join(list(map(str, self.spectre_name_values)))
        number = '\n'.join(list(map(str, self.spectre_number_values)))
        sp_type = '\n'.join(list(map(str, self.spectre_type_values)))

        self.spectre_name_label['text'] = name
        self.spectre_number_label['text'] = number
        self.spectre_type_label['text'] = sp_type

    def _init_buttons(self):
        row = 1

        self.choice_spectres_button = tk.Button(self, text='Выбрать спектр/спектры', width=self.button_width,
                                                command=self._choice_file_button)
        self.choice_spectres_button.grid(row=row, column=3, padx=50, pady=3)
        row += 1

        self.flux_auto_search_button = tk.Button(self, text='Автоматич. поиск', width=self.button_width,
                                                 command=self._flux_auto_search_button)
        self.flux_auto_search_button.grid(row=row, column=3, padx=50, pady=3)
        row += 1

        self.configure_spectre_button = tk.Button(self, text='Редактировать', width=self.button_width,
                                                  command=self._configure_spectre_button)
        self.configure_spectre_button.grid(row=row, column=3, padx=50, pady=3)
        row += 1

        self.create_spectre_button = tk.Button(self, text='Создать', width=self.button_width,
                                               command=self._create_spectre_button)
        self.create_spectre_button.grid(row=row, column=3, padx=50, pady=3)
        row += 1

        self.delete_current_source_from_db_button = tk.Button(self, text='Отключить', width=self.button_width,
                                                              command=self._delete_current_source_from_db_button)
        self.delete_current_source_from_db_button.grid(row=row, column=3, padx=50, pady=3)
        row += 1

        self._buttons_state()

    def _choice_file_button(self):
        self.__choice_files()
        self._set_spectre_data_to_interface()

        if all([i != 'Тип одного из файлов не распознан,\nдобавление невозможно' for i in self.spectre_name_values]):
            self._set_data_to_data_structure(self.spectre_name_values, self.spectre_number_values)

        self.configure_spectre_button['state'] = 'normal'
        self.delete_current_source_from_db_button['state'] = 'normal'

    def _flux_auto_search_button(self):
        self.__flux_auto_search()
        self._set_spectre_data_to_interface()

        if self.spectre_name_values[0] != 'Опознано неправильное количество спектров.\nВоспользуйтесь ручным выбором':
            self._set_data_to_data_structure(self.spectre_name_values, self.spectre_number_values)

    def _configure_spectre_button(self):
        if len(self.spectre_name_values) > 1:
            a = SelectSpectreToView(self.spectre_name_values)
            self.wait_window(a)
            if a.lb_current is None:
                return
            choice = a.lb_current
            chosen_index = self.spectre_name_values.index(choice)
        else:
            choice = self.spectre_name_values[0]
            chosen_index = 0

        sp_path = os.path.join(self.path, choice)

        if not os.path.exists(sp_path):
            print('Выбранный файл не был найден в проекте')

        top_level_root = tk.Toplevel(self)
        top_level_root.grab_set()

        ex = SpectreConfigure(self.path, top_level_root)
        ex.grid(sticky='NWSE')

        ex.button_open_spectre['state'] = 'disabled'
        ex.button_create_spectre['state'] = 'disabled'
        ex.spetre_type_cobbobox['state'] = 'disabled'

        ex.open_spectre(use_chose_spectre=sp_path, use_constructor=True)

        try:
            ex.spectre_power['state'] = 'disabled'
            self.wait_window(top_level_root)

        except:
            pass

        file_name, number, sp_type = self.__read_spectre(sp_path)
        if file_name is None:
            return

        self.spectre_name_values[chosen_index] = file_name
        self.spectre_number_values[chosen_index] = number
        self.spectre_type_values[chosen_index] = sp_type

        self._set_spectre_data_to_interface()

    def _create_spectre_button(self):
        top_level_root = tk.Toplevel(self)
        top_level_root.grab_set()

        ex = SpectreConfigure(self.path, top_level_root)
        ex.grid(sticky='NWSE')

        self.wait_window(top_level_root)

        file_name, number, sp_type = self.__read_spectre(ex.spectre_path)
        if file_name is None:
            return

        self.spectre_name_values = [file_name]
        self.spectre_number_values = [number]
        self.spectre_type_values = [sp_type]

        self._set_spectre_data_to_interface()

    def _delete_current_source_from_db_button(self):

        self.db[self.db_name].insert_third_level(self.fk, self.sk, 'distribution', None)
        self.delete_current_source_from_db_button['state'] = 'disabled'

        self.spectre_name_values = ['Файл не выбран']
        self.spectre_number_values = ['--']
        self.spectre_type_values = ['--']
        self._set_spectre_data_to_interface()

    def __choice_files(self):
        files = fd.askopenfilenames(title=f'Выберите файлы спектров', initialdir=self.path)

        if files == '':
            return

        file_name, number, sp_type = [], [], []
        for i in files:
            a, b, c = self.__read_spectre(i)
            if a is None:
                self.spectre_name_values = ['Тип одного из файлов не распознан,\nдобавление невозможно']
                self.spectre_number_values = [' ']
                self.spectre_type_values = [' ']
                return

            if b == -1 and c == -1:  # Обработка если выбран JX или energy_distribution
                file_name.append(a)
                number.append('--')
                sp_type.append('--')

            else:
                file_name.append(a)
                number.append(b)
                sp_type.append(c)

        self.spectre_name_values = file_name
        self.spectre_number_values = number
        self.spectre_type_values = sp_type

    def __read_spectre(self, target):
        if not os.path.exists(target):
            print('Выбранный файл не существует')
            return None, None, None

        target = self.__copy_to_project(target)
        file_name = os.path.split(target)[-1]

        try:
            with open(os.path.join(self.path, file_name), 'r') as file:
                for j, line in enumerate(file):
                    if j == 0 and len(line.strip().split('\t')) == 4:
                        number = -1
                        return file_name, number, -1
                    if j == 2:
                        number = int(line.strip())
                    if j == 6:
                        type = int(line.strip())
                        break

                if len(file.readlines()) < 2:
                    print('Длина файла маленькая')
                    raise Exception

        except:
            print('Ошибка чтения выбранных файлов')
            return None, None, None

        return file_name, number, type

    def __copy_to_project(self, target):
        t = target
        in_project = os.path.normpath(os.path.split(t)[0])
        if os.path.normpath(self.path) == in_project:
            return target
        file_name = os.path.split(t)[-1]
        save_path = os.path.join(self.path, file_name)
        if file_name in os.listdir(self.path + '/'):
            ask = mb.askyesno(f'Копирование {file_name} в проект',
                              'Файл с таким названием уже есть в проекте. Перезаписать файл?\n'
                              'да - перезаписать\n'
                              'нет - переименовать')
            if ask is True:
                shutil.copyfile(t, save_path)
            elif ask is False:
                while file_name in os.listdir(self.path + '/'):
                    file_name = sd.askstring('Введите имя файла', 'Введите имя файла')
                    if file_name in os.listdir(self.path + '/'):
                        print('Файл уже находится в проекте. Выберите новое имя.')
                save_path = os.path.join(self.path, file_name)
                shutil.copyfile(t, save_path)
        else:
            shutil.copyfile(t, save_path)

        return save_path

    def _check_db_for_values(self):
        if self.db[self.db_name].get_last_level_data(self.fk, self.sk, 'energy_type') is not None:

            self.spectre_name_values = []
            self.spectre_number_values = []
            self.spectre_type_values = []

            if 'Current' in self.sk or 'Energy' in self.sk:
                db_value = self.db[self.db_name].get_last_level_data(self.fk, self.sk, 'distribution')
            else:
                db_value = self.db[self.db_name].get_last_level_data(self.fk, self.sk, 'spectre')

            if type(db_value) is list:
                for file in self.db[self.db_name].get_last_level_data(self.fk, self.sk, 'spectre'):
                    f_path = os.path.join(self.path, file)
                    try:
                        if not os.path.exists(f_path):
                            raise Exception

                        f, number, sp_type = self.__read_spectre(f_path)

                        if f is None:
                            raise Exception

                        self.spectre_name_values.append(f)
                        self.spectre_number_values.append(number)
                        self.spectre_type_values.append(sp_type)

                    except:
                        self.spectre_name_values.append('Файл не обнаружен в проекте')
                        self.spectre_number_values.append('')
                        self.spectre_type_values.append('')

            else:
                if db_value is None:
                    self.spectre_name_values = ['Файл не выбран']
                    self.spectre_number_values = ['--']
                    self.spectre_type_values = ['--']

                    return
                f_path = os.path.join(self.path, db_value)
                f, number, sp_type = self.__read_spectre(f_path)

                if f is None:
                    self.spectre_name_values.append('Файл не обнаружен в проекте')
                    self.spectre_number_values.append('')
                    self.spectre_type_values.append('')

                else:
                    self.spectre_name_values.append(f)
                    self.spectre_number_values.append(number)
                    self.spectre_type_values.append(sp_type)

    def _set_data_to_data_structure(self, spectre_file_name, spectre_number):

        if self.spectre_name_values != ['Файл не выбран'] and self.spectre_number_values == [
            '--'] and self.spectre_type_values == ['--']:  # Доставка в БД для Current Energy

            if 'Current' not in self.sk and 'Energy' not in self.sk:
                mb.showerror('Ошибка', 'Выбранный файл подходит для источников Current или Energy.\n'
                                       'Добавление невозможно.')

                self.spectre_name_values = ['Файл не выбран']
                self._set_spectre_data_to_interface()
                return
            self.db[self.db_name].insert_third_level(self.fk, self.sk, 'distribution', spectre_file_name)

        else:  # Доставка в БД для всех остальных источников
            self.db[self.db_name].insert_third_level(self.fk, self.sk, 'spectre', spectre_file_name)
            self.db[self.db_name].insert_third_level(self.fk, self.sk, 'spectre numbers', spectre_number)

    def __flux_auto_search(self):
        """Автоматический поиск спектров в проекте для FLUX'"""

        from_l = self.sk.split('_')[-2]
        to_l = self.sk.split('_')[-1]
        particle_number = self.db[self.db_name].get_share_data('particle number')

        spectres = DataParser(self.path + '/').get_spectre_for_flux(particle_number, from_l, to_l)

        if len(spectres) == 6:
            file_name_list = []
            number_list = []
            sp_type_name_list = []

            for sp in spectres:
                sp_path = os.path.join(self.path, sp)
                file_name, number, sp_type = self.__read_spectre(sp_path)
                if file_name is None:
                    return

                file_name_list.append(file_name)
                number_list.append(number)
                sp_type_name_list.append(sp_type)

            self.spectre_name_values = file_name_list
            self.spectre_number_values = number_list
            self.spectre_type_values = sp_type_name_list

        else:
            self.spectre_name_values = ['Опознано неправильное количество спектров.\nВоспользуйтесь ручным выбором']
            self.spectre_number_values = ['']
            self.spectre_type_values = ['']

    def _buttons_state(self):
        if 'Volume' in self.sk:
            self.delete_current_source_from_db_button.grid_remove()
            self.flux_auto_search_button.grid_remove()
            self.configure_spectre_button['state'] = 'disabled'
            if all([os.path.exists(os.path.join(self.path, i)) for i in self.spectre_name_values]):
                self.configure_spectre_button['state'] = 'normal'

        elif 'Flu' in self.sk:
            self.delete_current_source_from_db_button.grid_remove()

        elif 'Current' in self.sk:
            self.create_spectre_button.grid_remove()
            self.flux_auto_search_button.grid_remove()

            self.configure_spectre_button['state'] = 'disabled'
            if all([os.path.exists(os.path.join(self.path, i)) for i in self.spectre_name_values]):
                self.configure_spectre_button['state'] = 'normal'

        elif 'Energy' in self.sk:
            self.delete_current_source_from_db_button.grid_remove()
            self.create_spectre_button.grid_remove()
            self.flux_auto_search_button.grid_remove()

            self.configure_spectre_button['state'] = 'disabled'
            if all([os.path.exists(os.path.join(self.path, i)) for i in self.spectre_name_values]):
                self.configure_spectre_button['state'] = 'normal'

        elif 'Boundaries' in self.sk:
            self.delete_current_source_from_db_button.grid_remove()
            self.create_spectre_button.grid_remove()
            self.flux_auto_search_button.grid_remove()

            self.configure_spectre_button['state'] = 'disabled'
            if all([os.path.exists(os.path.join(self.path, i)) for i in self.spectre_name_values]):
                self.configure_spectre_button['state'] = 'normal'

        else:
            print('чиво наделили? не знаем такого источника')


if __name__ == '__main__':
    root = tk.Tk()
    path = r'C:\Work\Test_projects\wpala'

    with open(os.path.join(path, 'Sources.pkl'), 'rb') as f:
        load_db = pickle.load(f)

    a = StandardizedSourceMainInterface(root, path, load_db, 'Influence 1', 'Электрон_X', 'Flu_e_1_1_0')

    a.pack()

    root.mainloop()
