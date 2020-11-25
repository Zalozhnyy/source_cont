import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import locale
import re


class TreeDataStructure:
    def __init__(self, obj_name, part_list=[]):
        self.obj_name = obj_name

        self.particle_list = part_list
        self.__obj_structure = {self.obj_name: {}, 'share_data': {}}

        self.__insert_first_level()
        self.__insert_share_data()

    def __insert_first_level(self):
        for i in self.particle_list:
            self.__obj_structure[self.obj_name].update({f'{i}': {}})

        self.__obj_structure[self.obj_name].update({'Current': {}})
        self.__obj_structure[self.obj_name].update({'Sigma': {}})

    def __insert_share_data(self):
        self.__obj_structure['share_data'].update({'amplitude': None,
                                                   'count': None,
                                                   'time': [],
                                                   'func': [],
                                                   'lag': None,
                                                   'time_full': None,
                                                   'func_full': None,
                                                   'tf_break': None,
                                                   'integrate': True,
                                                   'particle number': set()})

    def insert_share_data(self, key, value):
        self.__obj_structure['share_data'].update({key: value})

    def insert_first_level(self, key):
        self.__obj_structure[self.obj_name].update({key: {}})

    def insert_second_level(self, first_level_key, key, val):
        self.__obj_structure[self.obj_name][first_level_key].update({key: val})

    def insert_third_level(self, first_level_key, second_level_key, key, val):
        self.__obj_structure[self.obj_name][first_level_key][second_level_key].update({key: val})

    def delete_first_level(self, first_level_key):
        self.__obj_structure[self.obj_name].pop(first_level_key)

    def delete_second_level(self, second_level_key):
        for items in self.__obj_structure[self.obj_name].items():
            for key in items[-1].keys():
                if key == second_level_key:
                    self.__obj_structure[self.obj_name][items[0]].pop(key)
                    return

    def get_last_level_data(self, first_level_key, second_level_key, third_level_key):
        return self.__obj_structure[self.obj_name][first_level_key][second_level_key][third_level_key]

    def get_first_level_keys(self):
        return self.__obj_structure[self.obj_name].keys()

    def get_first_level_value(self, key):
        return self.__obj_structure[self.obj_name][key]

    def get_second_level_keys(self, first_key):
        return self.__obj_structure[self.obj_name][first_key].keys()

    def get_share_data(self, key):
        return self.__obj_structure['share_data'][key]

    def get_dict_object(self):
        return self.__obj_structure

    def replace_legacy_energy_to_sigma(self, value):
        self.__obj_structure[self.obj_name].update({'Sigma': value})


def check_folder(path):
    prj_name = []
    for f in os.listdir(path):
        if f.endswith(".PRJ") or f.endswith(".prj"):
            prj_name.append(f)
    if len(prj_name) == 0:
        return

    try:
        with open(os.path.join(path, rf'{prj_name[0]}'), 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        with open(os.path.join(path, rf'{prj_name[0]}'), 'r',
                  encoding=locale.getpreferredencoding()) as file:
            lines = file.readlines()

    out = {}
    for i in range(len(lines)):
        if '<Grd name>' in lines[i]:
            out.setdefault('GRD', lines[i + 1].strip())
        if '<Tok name>' in lines[i]:
            out.setdefault('TOK', lines[i + 1].strip())
        if '<Layers name>' in lines[i]:
            out.setdefault('LAY', lines[i + 1].strip())
        if '<Particles-Layers name>' in lines[i]:
            out.setdefault('PL', lines[i + 1].strip())
        if '<Particles name>' in lines[i]:
            out.setdefault('PAR', lines[i + 1].strip())

    return out


def tf_global_del(path):
    dir = os.path.join(path, 'time functions')
    ask = mb.askyesno('Очистка папки', 'Вы уверены, что хотите удалить все time функции?')
    if ask is True:

        for files in os.walk(dir):
            for file in files[2]:
                if file.endswith('.tf') or file.endswith('.txt'):
                    path = os.path.join(files[0], file)
                    os.remove(path)


def file_dialog(title=None, initialdir=None, filetypes=None):
    directory = fd.askopenfilename(title=title, initialdir=initialdir, filetypes=filetypes)
    if os.path.exists(directory):
        return directory


def save_for_remp_form(source_type=None, source_name=None, layer_index=None, amplitude=None,
                       time_for_dict=None, particle_index=None, func_for_dict=None,
                       lag_and_koord=None, distribution=None, spectre=None,
                       external_field_component=None):
    out = {'source_type': source_type,
           'source_name': source_name,
           'external_field_component': external_field_component,
           'layer_index': layer_index,
           'particle_index': particle_index,
           'amplitude': amplitude,
           'time_function': [len(time_for_dict),
                             time_for_dict,
                             func_for_dict],
           'lag (1 - PLANE, 2 - SPHERE), parameters': lag_and_koord,
           'distribution': distribution,
           'spectre': spectre}

    return out


class Calculations:

    def linear_dif(self, y1, x1, y2, x2):
        self.k = (y2 - y1) / (x2 - x1)
        self.b = y1 - (y2 - y1) * x1 / (x2 - x1)
        return self.k, self.b

    def solve(self, x, k, b):
        self.f = k * x + b
        return self.f


def open_button():
    filename = fd.askdirectory(title='Укажите путь к проекту REMP', initialdir=f'{os.getcwd()}/entry_data')
    if filename == '':
        return None
    return filename


def set_recent_projects(path, path_dict):
    unic_path = {}
    try:
        with open('sources_properties.ini', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for i in lines:
            unic_path.update({i.strip(): ''})
    except:
        pass

    unic_path.update({path: ''})

    for i in path_dict.keys():
        unic_path.update({i.strip(): ''})

    with open('sources_properties.ini', 'w', encoding='utf-8') as file:
        for i, key in enumerate(unic_path.keys()):
            file.write(key + '\n')


def get_recent_projects():
    out = {}
    try:
        with open('sources_properties.ini', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for i in lines:
            if os.path.exists(i.strip()):
                out.update({i.strip(): ''})
    except:
        pass
    return out


def rusian_words_analysis(word):
    r = re.compile("[а-яА-Я]")
    words = [word]
    russian = [w for w in filter(r.findall, words)]

    if len(russian) == 0:
        return 1
    elif len(russian) != 0:
        return -1


def permission_denied_test():
    try:
        test_file = os.path.join(os.path.dirname(__file__), 'permission_denied_test')

        with open(test_file, 'w') as file:
            file.write('test string')

    except PermissionError:
        mb.showerror('Предупреждение', 'Программа не имеет доступа к файловой системе.\n'
                                       'Запустите программу от имени администратора')

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


# source_list = []
# gursa_dict = {}
# source_number = 1
#
# time_func_dict = {}
#
# remp_sourses_dict = {}
# specters_dict = {}
#
# dict_for_recent_pr = {}
# recent_path = ''
# path_for_remp_save = ''

# if __name__ == '__main__':
#     test = tk.Tk()
#
#     tk.Button(test, text='123', command=lambda: file_dialog(title='Выберите файл spectr',
#                                                             initialdir=f'{}/pechs/spectr',
#                                                             filetypes=(
#                                                                 ("all files", "*.*"), ("txt files", "*.txt*")))).pack()
#
#     test.mainloop()


if __name__ == '__main__':
    a = rusian_words_analysis('asdas')
    print(a)
