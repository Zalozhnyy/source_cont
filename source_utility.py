import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import locale
import re
import tempfile
import pickle

import numpy as np

from loguru import logger
from source_Project_reader import DataParser


class TreeDataStructure:
    def __init__(self, obj_name: str, part_list: list = []):
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
        self.__obj_structure['share_data'].update({'amplitude': 0,
                                                   'count': None,
                                                   'time': [],
                                                   'func': [],
                                                   'lag': None,
                                                   'time_full': None,
                                                   'func_full': None,
                                                   'tf_break': None,
                                                   'integrate': True,
                                                   'particle number': set(),
                                                   'influence number': None})

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


class PreviousProjectLoader:
    """
    Класс предназначен для сопоставления данных из загрузки и проектных данных.
    Осуществляет удаление из БД несуществующих в преокте абстракций.
    """

    @logger.catch()
    def __init__(self, path: str, project_data: list):
        self.loaded_flag = False
        self.path = path

        self.global_tree_db = {}
        self._marple, self._micro_electronics = {}, {}
        self.PAR, self.LAY, self.PL_surf, self.PL_vol, self.PL_bound, self.layer_numbers = project_data

    def __reform_flux_spectres(self, obj: TreeDataStructure):

        for f_key in obj.get_first_level_keys():
            for s_key in obj.get_second_level_keys(f_key):
                if 'Flu' in s_key:
                    sp_old = obj.get_last_level_data(f_key, s_key, 'spectre')
                    num_old = obj.get_last_level_data(f_key, s_key, 'spectre numbers')

                    obj.insert_third_level(f_key, s_key, 'spectre',
                                           [sp for sp in sp_old if DataParser(self.path).spc_non_empty(sp)])
                    obj.insert_third_level(f_key, s_key, 'spectre numbers',
                                           [num for sp, num in zip(sp_old, num_old) if
                                            DataParser(self.path).spc_non_empty(sp)])

    def get_db_and_lag(self):
        lag = self.global_tree_db[list(self.global_tree_db.keys())[0]].get_share_data('lag')
        return self.global_tree_db, lag

    def __delete_particles(self, db):
        delete_part_list = set()

        for f_key in db.get_first_level_keys():
            if 'Sigma' not in f_key and 'Current' not in f_key and 'Energy' not in f_key:
                part = db.get_share_data('particle number')

                if type(part) is set:
                    part = list(part)

                if type(part) is list:
                    for part_number in part:
                        if all([part_number != self.PAR[k]['number'] for k in self.PAR.keys()]):
                            delete_part_list.add(f_key)

                # условие нужно для подержки старых версий баз данных, после сохранения они переходят в новый формат
                elif type(part) is int:
                    if all([part != self.PAR[k]['number'] for k in self.PAR.keys()]):
                        delete_part_list.add(f_key)

        for dk in delete_part_list:
            db.delete_first_level(dk)

    def start_reading(self, tests=False):
        if not os.path.exists(os.path.join(self.path, 'Sources.pkl')):
            print('Загрузка невозможна. Файл Sources.pkl не найден')
            mb.showerror('load error', 'Загрузка невозможна. Файл Sources.pkl не найден')
            return

        try:
            with open(os.path.join(self.path, 'Sources.pkl'), 'rb') as f:
                self.global_tree_db = pickle.load(f)
        except Exception:
            mb.showerror('Error',
                         'Ошибка при попытке прочитать бинарный файл сохранения. Загрузка невозможна.')
            return

        for i in self.global_tree_db.items():
            self.__delete_particles(i[1])

        for i in self.global_tree_db.items():
            """Удаляем источники, которых нет в текущих файлах проекта, но есть в загрузке"""
            self.__tree_db_delete_old(i[1])
            if not tests:
                self.__reform_flux_spectres(i[1])

        self._marple, self._micro_electronics = DataParser(self.path).load_marple_data_from_remp_source()
        self.loaded_flag = True

    def __tree_db_delete_old(self, obj):
        try:
            part_number_tuple = obj.get_share_data('particle number')
        except KeyError:
            part_number_tuple = None

        # удаление из базы данных несуществующих частиц
        delete_part_list = set()

        """удаление источников energy для совместимости старых source.pkl удалить при добавлении источника energy"""
        for f_key in obj.get_first_level_keys():
            if f_key == 'Energy':
                delete_part_list.add(f_key)

        if len(delete_part_list) != 0:
            for f_key in delete_part_list:
                if len(obj.get_second_level_keys(f_key)) == 0:
                    obj.replace_legacy_energy_to_sigma({})
                else:
                    for key2 in obj.get_second_level_keys(f_key):
                        name = obj.get_last_level_data(f_key, key2, 'name').replace('Energy', 'Sigma')
                        energy_type = 'Sigma'
                        distribution = obj.get_last_level_data(f_key, key2, 'name')

                        insert_dict = {name: {
                            'name': name,
                            'energy_type': energy_type,
                            'distribution': distribution
                        }
                        }

                        obj.replace_legacy_energy_to_sigma(insert_dict)

        if part_number_tuple is None and len(delete_part_list) == 0:
            return

        db_s_keys = set()

        for f_key in obj.get_first_level_keys():
            for s_key in obj.get_second_level_keys(f_key):
                db_s_keys.add(s_key)

        for f_key in obj.get_first_level_keys():
            if self.PAR is None:
                continue
            if f_key not in self.PAR.keys() and f_key != 'Current' and f_key != 'Sigma':
                delete_part_list.add(f_key)

        for f_key in delete_part_list:
            obj.delete_first_level(f_key)

        for key in db_s_keys:
            if 'Current' in key:
                cur_lay = np.where(self.layer_numbers == int(key.split('_')[-1]))
                self.__delete_source_safely((lambda: self.LAY[cur_lay, 1] == 0), obj, key)
            if 'Sigma' in key:
                cur_lay = np.where(self.layer_numbers == int(key.split('_')[-1]))
                self.__delete_source_safely(lambda: (self.LAY[cur_lay, 2] == 0), obj, key)
            if 'Flu' in key:
                from_l = np.where(self.layer_numbers == int(key.split('_')[-2]))
                to_l = np.where(self.layer_numbers == int(key.split('_')[-1]))
                part_number = int(key.split('_')[-3])
                self.__delete_source_safely(lambda: (self.PL_surf[part_number][to_l, from_l] == 0), obj, key)
            if 'Volume78' == key.split('_')[0]:
                vol_lay = np.where(self.layer_numbers == int(key.split('_')[-1]))
                part_number = int(key.split('_')[-2])
                self.__delete_source_safely(lambda: (self.PL_vol[part_number][vol_lay] == 0), obj, key)
            if 'Volume' == key.split('_')[0]:
                vol_lay = np.where(self.layer_numbers == int(key.split('_')[-1]))
                part_number = int(key.split('_')[-2])
                self.__delete_source_safely(lambda: self.PL_vol[part_number][vol_lay] == 0, obj, key)
            if 'Boundaries' in key:
                boundaries_decode = {0: 'X', 1: 'Y', 2: 'Z', 3: '-X', 4: '-Y', 5: '-Z'}
                bo_lay_k = key.split('_')[-1]
                part_number = int(key.split('_')[-2])
                for i in boundaries_decode.items():
                    if i[1] == bo_lay_k:
                        bo_lay = i[0]
                        break
                self.__delete_source_safely(lambda: (self.PL_bound[part_number][bo_lay] == 0), obj, key)

        delete_f_level_set = set()
        for f_key in obj.get_first_level_keys():  # удаляем пустые сущности частиц
            if len(obj.get_first_level_value(f_key)) == 0 and f_key != 'Current' and f_key != 'Sigma':
                delete_f_level_set.add(f_key)

        for f_key in delete_f_level_set:
            obj.delete_first_level(f_key)

    def __delete_source_safely(self, statment, data_object, key):
        try:
            if statment():
                data_object.delete_second_level(key)

        except Exception as e:
            print(e)
            print(f'Ошибка удаления источника {key}')


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
    p = os.path.join(tempfile.gettempdir(), 'sources_properties.ini')
    p = os.path.normpath(p)

    try:
        with open(p, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for i in lines:
            unic_path.update({i.strip(): ''})
    except Exception:
        pass

    unic_path.update({path: ''})

    for i in path_dict.keys():
        unic_path.update({i.strip(): ''})

    with open(p, 'w', encoding='utf-8') as file:
        for i, key in enumerate(unic_path.keys()):
            file.write(key + '\n')


def get_recent_projects():
    out = {}

    p = os.path.normpath(os.path.join(tempfile.gettempdir(), 'sources_properties.ini'))
    try:
        with open(p, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for i in lines:
            if os.path.exists(i.strip()):
                out.update({i.strip(): ''})
    except Exception:
        pass
    return out


def russian_words_analysis(word):
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


if __name__ == '__main__':
    get_recent_projects()
