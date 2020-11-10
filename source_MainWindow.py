import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd

import pickle

from loguru import logger

from source_MW_interface_classes import StandardizedSourceMainInterface
from source_utility import *
from source_Project_reader import DataParser, SubtaskDecoder
from source_Save_for_remp import Save_remp
from source_Main_frame import FrameGen
from source_Dialogs import SelectParticleDialog, DeleteGSourceDialog, SelectLagInterface, MarpleElectronicsInterface
from source_PE_SOURCE import PeSource
from remp_parameters_tests import main_test as remp_files_test


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
        self.__obj_structure[self.obj_name].update({'Energy': {}})

    def __insert_share_data(self):
        self.__obj_structure['share_data'].update({'amplitude': None,
                                                   'count': None,
                                                   'time': [],
                                                   'func': [],
                                                   'lag': None,
                                                   'time_full': None,
                                                   'func_full': None,
                                                   'tf_break': None,
                                                   'integrate': True})

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

    def get_second_level_keys(self, first_key):
        return self.__obj_structure[self.obj_name][first_key].keys()

    def get_share_data(self, key):
        return self.__obj_structure['share_data'][key]

    def get_dict_object(self):
        return self.__obj_structure


@logger.catch()
class MainWindow(tk.Frame):
    def __init__(self, parent, path=None, projectfilename=None):
        super().__init__(parent)
        self.parent = parent
        self.path = None

        self.parent.protocol("WM_DELETE_WINDOW", self.onExit)

        self.prj_path = None

        self.notebook = None
        self.tabs_dict = {}
        self.tree = []
        self.global_tree_db = {}

        self.toolbar()

        self.global_count_gsources = 0

        self.remp_source_exist = False

        self._marple = None
        self._micro_electronics = None

        self._save_flag = False

        self.lag = None

        try:
            if projectfilename is not None:
                if os.path.exists(projectfilename):
                    self.prj_path = projectfilename
                    self.path = os.path.split(self.prj_path)[0]
                    self.check_project()
            else:
                raise Exception
        except Exception:
            self.path = path

    def from_project_reader(self):

        # self.tok_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('TOK')))
        self.pl_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PL')))
        self.lay_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('LAY')))
        self.par_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PAR')))

        # self.TOK = DataParcer(self.tok_dir).tok_decoder()
        if os.path.exists(self.pl_dir):
            self.PL_surf, self.PL_vol, self.PL_bound, self.layer_numbers = DataParser(self.pl_dir).pl_decoder()
            if self.PL_surf is None:
                mb.showerror('ERROR', 'Нарушена структура файла PL')
                return
        else:
            self.PL_surf, self.PL_vol, self.PL_bound, self.layer_numbers = None, None, None, None

        if os.path.exists(self.lay_dir):
            self.LAY = DataParser(self.lay_dir).lay_decoder()
            if self.LAY is None:
                mb.showerror('ERROR', 'Нарушена структура файла LAY')
                return
        else:
            self.LAY = DataParser('').return_empty_array((1, 3))

        if os.path.exists(self.par_dir):
            self.PAR = DataParser(self.par_dir).par_decoder()
            if self.PAR is None:
                mb.showerror('ERROR', 'Нарушена структура файла PAR')
                return
        else:
            self.PAR = None

        if (self.LAY is not None) and (self.layer_numbers is not None):
            if self.LAY.shape[0] != self.layer_numbers.shape[0]:
                mb.showerror('ERROR', 'Не совпадает количество слоёв в файле PL и LAY.\n'
                                      'Запустите интерфейс редактирования файлов LAY/PL для исправления данной ошибки.')
                return -1
        return 0

    def toolbar(self):
        self.parent.title("Sources")
        self.menubar = tk.Menu(self.parent, postcommand=self.update)
        self.parent.config(menu=self.menubar)

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Файл", menu=self.filemenu)
        self.recent_pr_menu = tk.Menu(self.filemenu, tearoff=0)

        self.filemenu.add_command(label="Открыть проект", command=self.browse_folder)

        funcs = [(lambda k: lambda: self.browse_from_recent(k))(key) for key in get_recent_projects().keys()]
        for key, f in zip(get_recent_projects().keys(), funcs):
            self.recent_pr_menu.add_command(label=f'{key}', command=f)

        self.filemenu.add_cascade(label="Недавние проекты", menu=self.recent_pr_menu)

        self.filemenu.add_command(label="Сохранение для РЭМП", command=self.save, state='disabled')

        self.filemenu.add_command(label="Открыть папку с проектом", command=self.open_folder, state='disabled')

        self.filemenu.add_command(label="Изменить параметр задержки", command=self._configure_lag, state='disabled')

        self.filemenu.add_command(label="Exit", command=self.onExit)

        self.menubar.add_command(label='Добавить воздействие',
                                 command=self.__add_source_button, state='disabled')
        self.menubar.add_command(label='Удалить воздействие', command=self.__tree_view_deconstructor, state='disabled')

        # self.menubar.add_command(label='Справка')
        # self.menubar.add_command(label='test', command=self.test)

        self.marple_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Задача обтекания", menu=self.marple_menu, state='disabled')

        self.marple_menu.add_command(label="Добавить/Изменить задачу обтекания", command=self.__add_marple,
                                     state='normal')
        self.marple_menu.add_command(label="Удалить  задачу обтекания", command=self.__delete_marple, state='disabled')

        self.menubar.add_command(label="Добавить спектр переноса", state='disabled', command=self.start_pechs)

    def _create_micro_electronics_menubar(self):

        self.electronics_menu = tk.Menu(self.menubar, tearoff=0)

        self.menubar.add_cascade(label="Микроэлектроника", menu=self.electronics_menu, state='disabled')

        self.electronics_menu.add_command(label="Добавить файлы микроэлектроники", command=self.__add_microel,
                                          state='normal')
        self.electronics_menu.add_command(label="Удалить  файлы микроэлектроники", command=self.__delete_microel,
                                          state='disabled')

    def _activate_micro_electronics_menubar(self):
        microele_index = self.menubar.index('Микроэлектроника')
        self.menubar.entryconfigure(microele_index, state='normal')

    def menubar_activate(self):
        add_index = self.menubar.index('Добавить воздействие')
        del_index = self.menubar.index('Удалить воздействие')

        open_folder_index = self.filemenu.index('Открыть папку с проектом')
        save_for_remp_index = self.filemenu.index('Сохранение для РЭМП')
        configure_lag_index = self.filemenu.index('Изменить параметр задержки')

        self.filemenu.entryconfigure(open_folder_index, state='normal')
        self.filemenu.entryconfigure(save_for_remp_index, state='normal')
        self.filemenu.entryconfigure(configure_lag_index, state='normal')

        self.menubar.entryconfigure(add_index, state='normal')
        self.menubar.entryconfigure(del_index, state='normal')

        marple_index = self.menubar.index('Задача обтекания')
        self.menubar.entryconfigure(marple_index, state='normal')

        pechs_index = self.menubar.index('Добавить спектр переноса')
        self.menubar.entryconfigure(pechs_index, state='normal')

    def start_pechs(self):
        ex = PeSource(self.path, self.parent)
        ex.main_calculation()

    def check_saved_ds(self, db, saved_db):
        same = True
        for key in saved_db.keys():
            if db[key].get_dict_object() != saved_db[key].get_dict_object():
                same = False
                return same
        return same

    def set_lag(self):
        sub = SubtaskDecoder(self.path)

        if sub.subtask_path is not None:
            x, y, z = sub.get_subtask_koord()
            self.lag = f'1 {x} {y} {z}'
            print('Параметр задержки взята из файла подзадачи')

        else:
            ask = mb.askyesno('Файл подзадачи не найден',
                              'Параметры задержки не найдены в файле подзадачи.\n'
                              'Активировать меню выбора параметров задержки?\n\n'
                              'Да  - запустить меню редактора\n'
                              'Нет - параметр задержки отсутствует')

            if ask is True:
                ex = SelectLagInterface(self.path)
                self.wait_window(ex)

                x, y, z = ex.vector_data
                self.lag = f'1 {x} {y} {z}'

                if any([i is None for i in [x, y, z]]):
                    self.lag = f'0'

            elif ask is False:
                self.lag = f'0'

        for name in self.global_tree_db.keys():
            self.global_tree_db[name].insert_share_data('lag', self.lag)

    def _configure_lag(self):

        for name in self.global_tree_db.keys():
            self.lag = self.global_tree_db[name].get_share_data('lag')
            break

        try:
            if self.lag is None:
                raise Exception

            a = list(map(float, self.lag.strip().split()[1:]))

        except:
            a = []

        ex = SelectLagInterface(self.path, a)

        if self.lag == '0':
            ex._enable_var.set(0)
        else:
            ex._enable_var.set(1)

        ex.en_change()

        self.wait_window(ex)

        x, y, z = ex.vector_data
        self.lag = f'1 {x} {y} {z}'

        if any([i is None for i in [x, y, z]]):
            self.lag = f'0'

        for name in self.global_tree_db.keys():
            self.global_tree_db[name].insert_share_data('lag', self.lag)

    def onExit(self):
        if len(self.global_tree_db) == 0:
            self.parent.quit()
            self.parent.destroy()
            return

        if 'Sources.pkl' in os.listdir(self.path):
            with open(os.path.join(self.path, 'Sources.pkl'), 'rb') as f:
                load_db = pickle.load(f)

            if load_db.keys() == self.global_tree_db.keys() and not self._save_flag:
                if self.check_saved_ds(load_db, self.global_tree_db) is True:
                    self.parent.quit()
                    self.parent.destroy()
                    return

        ask = mb.askyesno('Сохранение', 'Сохранить файл?')

        if ask is True:
            ex = Save_remp(self._marple, self._micro_electronics, self.global_tree_db, self.path)

            if ex.saved is False:
                ask_exit = mb.askyesno('Сохранение', 'Сохранение невозможно, т.к. не заданы все параметры.\n'
                                                     'Выйти без сохранения?')
                if ask_exit is True:
                    self.parent.quit()
                    self.parent.destroy()
                    return

                elif ask_exit is False:
                    return

            elif ex.saved is True:
                self.parent.quit()
                self.parent.destroy()
                return

        elif ask is False:
            self.parent.quit()
            self.parent.destroy()
            return

    def browse_from_recent(self, path):
        self.prj_path = path

        test_complete, error_messages = remp_files_test(self.prj_path)

        test_passed = True
        for item, value in test_complete.items():
            if not value:
                test_passed = False
                print(error_messages[item])
                mb.showerror('ERROR', error_messages[item])

        if not test_passed:
            return

        self.path = os.path.dirname(self.prj_path)
        self.check_project()

    def browse_folder(self):
        self.prj_path = fd.askopenfilename(title='Укажите путь к проекту REMP', initialdir=f'{os.getcwd()}',
                                           filetypes=[('PRJ files', '.PRJ')])
        if self.prj_path == '' or self.prj_path is None:
            return None

        test_complete, error_messages = remp_files_test(self.prj_path)

        test_passed = True
        for item, value in test_complete.items():
            if value is False:
                test_passed = False
                print(error_messages[item])
                mb.showerror('ERROR', error_messages[item])

        if not test_passed:
            return
        self.path = os.path.dirname(self.prj_path)
        self.check_project()

    def check_folder(self):

        try:
            with open(self.prj_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(self.prj_path, 'r',
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

    @logger.catch()
    def check_project(self):
        if self.path is None:
            return

        try:
            self.reset()
        except:
            pass

        self.file_dict = self.check_folder()

        set_recent_projects(self.prj_path, get_recent_projects())

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid(sticky='NWSE')

        if self.from_project_reader() != 0:
            return
        self.parent.title(f'Source - открыт проект {os.path.normpath(self.prj_path)}')

        try:
            for i in self.PAR.keys():
                if self.PAR[i]['type'] == 7 or self.PAR[i]['type'] == 8:
                    self._create_micro_electronics_menubar()
                    break
        except:
            pass

        if 'remp_sources' in os.listdir(self.path):

            ask = mb.askyesno('Обнаружен rems source', 'Обнаружен файл remp source\nЗагрузить данные?')

            if ask is True:
                if not os.path.exists(os.path.join(self.path, 'Sources.pkl')):
                    print('Загрузка невозможна. Файл Sources.pkl не найден')
                    mb.showerror('load error', 'Загрузка невозможна. Файл Sources.pkl не найден')
                    self.menubar_activate()
                    return

                self.remp_source_exist = True

                with open(os.path.join(self.path, 'Sources.pkl'), 'rb') as f:
                    self.global_tree_db = pickle.load(f)

                for i in self.global_tree_db.items():
                    """Удаляем источники, которых нет в текущих файлах проекта, но есть в загрузке"""
                    self.tree_db_delete_old(i[1])

                    try:
                        part_number = self.global_tree_db[i[0]].get_share_data('particle number')
                    except KeyError:
                        part_number = None
                    self.tree_view_constructor(load=True, ask_name=False, load_data=(i[0], part_number))

                self._marple, self._micro_electronics = DataParser(self.path).load_marple_data_from_remp_source()

            elif ask is False:
                self.set_lag()
        else:
            self.set_lag()

        self.menubar_activate()

    def reset(self):
        if self.path is None:
            return
        self.notebook.destroy()
        self.notebook = None
        self.tabs_dict = {}
        self.tree = []
        self.global_tree_db = {}
        self.global_count_gsources = 0

    def open_folder(self):
        if self.path is None:
            return
        os.startfile(self.path)

    def tree_db_delete_old(self, obj):
        try:
            part_number = obj.get_share_data('particle number')
        except KeyError:
            part_number = None

        # удаление из базы данных несуществующих частиц
        for f_key in obj.get_first_level_keys():
            if f_key not in self.PAR.keys() and f_key != 'Current' and f_key != 'Energy':
                obj.delete_first_level(f_key)
                continue

        if part_number is None:
            return

        db_s_keys = []

        for f_key in obj.get_first_level_keys():
            for s_key in obj.get_second_level_keys(f_key):
                db_s_keys.append(s_key)

        for key in db_s_keys:
            if 'Current' in key:
                cur_lay = int(key.split('_')[-1])
                if self.LAY[cur_lay, 1] == 0:
                    obj.delete_second_level(key)
            if 'Energy' in key:
                cur_lay = int(key.split('_')[-1])
                if self.LAY[cur_lay, 2] == 0:
                    obj.delete_second_level(key)
            if 'Flu' in key:
                from_l = int(key.split('_')[-2])
                to_l = int(key.split('_')[-1])
                if self.PL_surf[part_number][to_l, from_l] == 0:
                    obj.delete_second_level(key)
            if 'Volume78' in key:
                vol_lay = int(key.split('_')[-1])
                if self.PL_vol[part_number][vol_lay] == 0:
                    obj.delete_second_level(key)
            if 'Volume' in key:
                vol_lay = int(key.split('_')[-1])
                if self.PL_vol[part_number][vol_lay] == 0:
                    obj.delete_second_level(key)
            if 'Boundaries' in key:
                boundaries_decode = {0: 'X', 1: 'Y', 2: 'Z', 3: '-X', 4: '-Y', 5: '-Z'}
                bo_lay_k = key.split('_')[-1]
                for i in boundaries_decode.items():
                    if i[1] == bo_lay_k:
                        bo_lay = i[0]
                        break
                if self.PL_bound[part_number][bo_lay] == 0:
                    obj.delete_second_level(key)

    def tree_db_insert(self, obj_name):
        obj = TreeDataStructure(obj_name)

        create_list = ['x', 'y', 'z']
        obj.insert_share_data('lag', self.lag)
        obj.insert_share_data('influence number', str(self.global_count_gsources))

        for i in range(self.LAY.shape[0]):
            if self.LAY[i, 1] == 1:
                for axis in create_list:
                    energy_type = f'Ток по оси {axis} слой {self.layer_numbers[i]}'
                    name = f'Current_{axis}_layer_{self.layer_numbers[i]}'
                    if name in obj.get_second_level_keys('Current'):
                        continue

                    obj.insert_second_level('Current', f'{name}', {})

                    obj.insert_third_level('Current', f'{name}', 'name', name)
                    obj.insert_third_level('Current', f'{name}', 'energy_type', energy_type)

                    current_file = DataParser(self.path).get_distribution_for_current_and_energy(
                        obj.get_share_data('influence number')
                        , i,
                        f'j{axis.lower()}')

                    obj.insert_third_level('Current', f'{name}', 'distribution', current_file)

            if self.LAY[i, 2] == 1:
                energy_type = 'Energy'
                name = f'Energy_layer_{self.layer_numbers[i]}'
                obj.insert_second_level('Energy', f'{name}', {})

                obj.insert_third_level('Energy', f'{name}', 'name', name)
                obj.insert_third_level('Energy', f'{name}', 'energy_type', energy_type)

                current_file = DataParser(self.path).get_distribution_for_current_and_energy(
                    obj.get_share_data('influence number'), i, f'en')
                obj.insert_third_level('Energy', f'{name}', 'distribution', current_file)

        return obj

    def tree_db_insert_particle(self, obj_name, particle, load=False):
        obj = obj_name

        boundaries_decode = {0: 'X', 1: 'Y', 2: 'Z', 3: '-X', 4: '-Y', 5: '-Z'}
        boundaries_decode_f = {'X': 'xmax_part', 'Y': 'ymax_part', 'Z': 'zmax_part',
                               '-X': 'xmin_part', '-Y': 'ymin_part', '-Z': 'zmin_part', }

        distr_list = DataParser(self.path + '/').distribution_reader()
        b_list = DataParser(self.path + '/').get_spectre_for_bound()

        number = self.PAR[particle]['number']
        type = self.PAR[particle]['type']

        obj.insert_share_data('particle number', self.PAR[particle]['number'])

        if load:
            if particle not in obj.get_first_level_keys():
                obj.insert_first_level(f'{particle}')
            create_list = ['x', 'y', 'z']

            for i in range(self.LAY.shape[0]):
                if self.LAY[i, 1] == 1:
                    for axis in create_list:
                        energy_type = f'Ток по оси {axis} слой {self.layer_numbers[i]}'
                        name = f'Current_{axis}_layer_{self.layer_numbers[i]}'
                        if name in obj.get_second_level_keys('Current'):
                            continue

                        obj.insert_second_level('Current', f'{name}', {})

                        obj.insert_third_level('Current', f'{name}', 'name', name)
                        obj.insert_third_level('Current', f'{name}', 'energy_type', energy_type)

                        current_file = DataParser(self.path).get_distribution_for_current_and_energy(number, i,
                                                                                                     f'j{axis.lower()}')
                        obj.insert_third_level('Current', f'{name}', 'distribution', current_file)

                if self.LAY[i, 2] == 1:
                    energy_type = 'Energy'
                    name = f'Energy_layer_{self.layer_numbers[i]}'
                    if name in obj.get_second_level_keys('Energy'):
                        continue

                    obj.insert_second_level('Energy', f'{name}', {})

                    obj.insert_third_level('Energy', f'{name}', 'name', name)
                    obj.insert_third_level('Energy', f'{name}', 'energy_type', energy_type)

                    current_file = DataParser(self.path).get_distribution_for_current_and_energy(number, i, f'en')
                    obj.insert_third_level('Energy', f'{name}', 'distribution', current_file)

        ar = self.PL_surf.get(number)

        for i in range(ar.shape[0]):  # surfCE
            for j in range(0, ar.shape[1]):
                if ar[i, j] != 0:
                    energy_type = f'Источник частиц №{number} из {self.layer_numbers[j]}-го слоя в {self.layer_numbers[i]}-й'
                    name = f'Flu_e_{number}_{self.layer_numbers[j]}_{self.layer_numbers[i]}'

                    if name in obj.get_second_level_keys(particle):
                        continue
                    obj.insert_second_level(f'{particle}', f'{name}', {})

                    obj.insert_third_level(f'{particle}', f'{name}', 'energy_type', energy_type)
                    obj.insert_third_level(f'{particle}', f'{name}', 'name', name)
                    obj.insert_third_level(f'{particle}', f'{name}', 'spectre', None)
                    obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers', None)

                    from_l = name.split('_')[-2]
                    to_l = name.split('_')[-1]
                    spectres = DataParser(self.path + '/').get_spectre_for_flux(number, from_l, to_l)

                    if len(spectres) == 6:
                        obj.insert_third_level(particle, name, 'spectre', [i for i in spectres.keys()])
                        obj.insert_third_level(particle, name, 'spectre numbers', [i for i in spectres.values()])

                    # if load:
                    #     try:
                    #         spectre = [i for i in self.rs_data[number][name]['spectre'].split(' ')]
                    #         obj.insert_third_level(f'{particle}', f'{name}', 'spectre', spectre)
                    #
                    #         spectre_number = [i for i in self.rs_data[number][name]['spectre number'].split(' ')]
                    #         obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers', spectre_number)
                    #
                    #     except:
                    #         print(
                    #             f'Загрузка данных в {particle} {name} произошла с ошибкой или нет данных в remp sources')
                    #         if len(spectres) == 6:
                    #             obj.insert_third_level(particle, name, 'spectre', [i for i in spectres.keys()])
                    #             obj.insert_third_level(particle, name, 'spectre numbers',
                    #                                    [i for i in spectres.values()])
                    #         else:
                    #             obj.insert_third_level(particle, name, 'spectre', None)
                    #             obj.insert_third_level(particle, name, 'spectre numbers', None)

        for i in range(len(self.PL_vol[number])):  # volume
            if self.PL_vol[number][i] != 0 and type != 7 and type != 8:
                energy_type = f'Объёмный источник частиц №{number} слой №{self.layer_numbers[i]}'
                name = f'Volume_{number}_{self.layer_numbers[i]}'

                if name in obj.get_second_level_keys(particle):
                    continue

                obj.insert_second_level(f'{particle}', f'{name}', {})

                obj.insert_third_level(f'{particle}', f'{name}', 'energy_type', energy_type)
                obj.insert_third_level(f'{particle}', f'{name}', 'name', name)
                obj.insert_third_level(f'{particle}', f'{name}', 'spectre', None)
                obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers', None)

                # if load:
                #     try:
                #         obj.insert_third_level(f'{particle}', f'{name}', 'spectre',
                #                                self.rs_data[number][name]['spectre'])
                #         obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers',
                #                                self.rs_data[number][name]['spectre number'])
                #     except:
                #         print(f'Загрузка данных в {particle} {name} произошла с ошибкой или нет данных в remp sources')
                #         obj.insert_third_level(particle, name, 'spectre', None)
                #         obj.insert_third_level(particle, name, 'spectre numbers', None)

        for i in range(len(self.PL_vol[number])):  # volume78
            if self.PL_vol[number][i] != 0 and (type == 7 or type == 8):
                energy_type = f'Объёмный источник частиц №{number} слой №{self.layer_numbers[i]}'
                name = f'Volume78_{number}_{self.layer_numbers[i]}'

                if name in obj.get_second_level_keys(particle):
                    continue

                obj.insert_second_level(f'{particle}', f'{name}', {})

                obj.insert_third_level(f'{particle}', f'{name}', 'energy_type', energy_type)
                obj.insert_third_level(f'{particle}', f'{name}', 'name', name)
                obj.insert_third_level(f'{particle}', f'{name}', 'spectre', None)
                obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers', None)

                # if load:
                #     try:
                #         obj.insert_third_level(f'{particle}', f'{name}', 'spectre',
                #                                self.rs_data[number][name]['spectre'])
                #         obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers',
                #                                self.rs_data[number][name]['spectre number'])
                #     except:
                #         print(f'Загрузка данных в {particle} {name} произошла с ошибкой или нет данных в remp sources')
                #         obj.insert_third_level(particle, name, 'spectre', None)
                #         obj.insert_third_level(particle, name, 'spectre numbers', None)

        for i in range(len(self.PL_bound[number])):
            if self.PL_bound[number][i] != 0:
                energy_type = 'Boundaries'
                name = f'{energy_type}_{number}_{boundaries_decode[i]}'

                if name in obj.get_second_level_keys(particle):
                    continue

                obj.insert_second_level(f'{particle}', f'{name}', {})

                obj.insert_third_level(f'{particle}', f'{name}', 'energy_type', energy_type)
                obj.insert_third_level(f'{particle}', f'{name}', 'name', name)
                obj.insert_third_level(particle, name, 'spectre', None)
                obj.insert_third_level(particle, name, 'spectre numbers', None)

                for item in b_list.items():
                    predict_file_name = boundaries_decode_f[name.split('_')[-1]]
                    if predict_file_name in item[0]:
                        if item[1]['particle number'] == number:
                            file = item[0]
                            sp_number = item[1]['number']

                            obj.insert_third_level(particle, name, 'spectre', file)
                            obj.insert_third_level(particle, name, 'spectre numbers', sp_number)

    @logger.catch()
    def tree_view_constructor(self, ask_name=True, load=False, load_data=None):
        if self.path is None:
            mb.showerror('Path', 'Сначала выберите проект')
            return
        self.global_count_gsources += 1

        if ask_name is True:
            while True:
                name = sd.askstring('Назовите воздействие', 'Введите название воздействия (Английский язык)\n'
                                                            'Ok - название по умолчанию')
                if name == '':
                    name = f'Influence {self.global_count_gsources}'
                if name is None:
                    return
                if rusian_words_analysis(name) == 1:
                    break
                else:
                    mb.showerror('Название воздействия', 'В названии найден русский символ.\n'
                                                         'Назовите воздействие на английском языке')

        else:
            name = load_data[0]
        if not load:
            try:
                if name in self.global_tree_db.keys():
                    print('Данное имя занято другим воздействием')
                    return
            except:
                pass

        ind = len(self.tabs_dict)

        fr = tk.Frame()
        fr_tree = tk.Frame(fr)
        fr_tree.grid(row=0, column=0, rowspan=100, columnspan=5, sticky='NWSE')

        self.tree.append(ttk.Treeview(fr_tree, height=36))

        self.tree[ind].column("#0", width=300)
        self.tree[ind].heading("#0", text="Источники")
        self.tree[ind].grid(row=0, column=0, rowspan=200, columnspan=4, sticky='NWSE')

        self.tree[ind].bind("<<TreeviewSelect>>",
                            lambda _,
                                   name=name,
                                   sv=len(self.tabs_dict):
                            self.__tree_select_react(sv, name, _))

        source = self.tree[ind].insert('', 0, text=f'{name}', open=True)

        if load is False:
            self.global_tree_db.update({name: self.tree_db_insert(name)})
            fr_data = FrameGen(fr, self.path, self.global_tree_db[name], (self.notebook, self.parent))
            fr_data.configure(text=self.global_tree_db[name].obj_name + f'  № {self.global_count_gsources}')
            fr_data._notebooks()

        elif load is True:
            # self.global_tree_db.update({name: self.tree_db_insert(name)})

            part_name = None
            for i in self.PAR.keys():
                if self.PAR[i]['number'] == load_data[1]:
                    part_name = i
                    if self.PAR[i]['type'] == 7 or self.PAR[i]['type'] == 8:
                        self._activate_micro_electronics_menubar()
                    break

            if part_name is not None:  # костыль для загрузки в структуры воздействий без частиц
                self.tree_db_insert_particle(self.global_tree_db[name], part_name, True)
                source_keys = self.global_tree_db[name].get_second_level_keys(part_name)
                self.particle_tree_constr(part_name, source_keys, source, ind)

            fr_data = FrameGen(fr, self.path, self.global_tree_db[name], (self.notebook, self.parent))
            fr_data.configure(text=self.global_tree_db[name].obj_name + f'  № {self.global_count_gsources}')
            if self.global_tree_db[name].get_share_data('count') is not None:
                fr_data.cell_numeric = len(self.global_tree_db[name].get_share_data('time_full'))
                fr_data._notebooks()
                fr_data.load_data()

        fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='WN')
        # self.main_frame_exist = True

        for index, s_type in enumerate(self.global_tree_db[name].get_first_level_keys()):
            source_keys = self.global_tree_db[name].get_second_level_keys(s_type)
            if len(source_keys) == 0:
                continue
            if any(['Energy' in s_key for s_key in source_keys]):
                lb = 'Энерговыделение'
                self.__energy_tree_view_section = self.tree[ind].insert(source, index, text=lb, open=True)

                for i, s_key in enumerate(source_keys):
                    self.tree[ind].insert(self.__energy_tree_view_section, i, text=f'{s_key}', open=True)

            elif any(['Current' in s_key for s_key in source_keys]):
                lb = 'Сторонний ток'
                self.__current_tree_view_section = self.tree[ind].insert(source, index, text=lb, open=True)

                for i, s_key in enumerate(source_keys):
                    self.tree[ind].insert(self.__current_tree_view_section, i, text=f'{s_key}', open=True)

        self.tree[ind].bind("<Button-3>", lambda _,
                                                 index=ind,
                                                 name=name: self._left_button_menu(name, index, _))

        self.notebook.add(fr, text=f'{name}')
        self.tabs_dict.update({name: [len(self.tabs_dict), fr, True]})

    def particle_tree_constr(self, particle, keys, main_tree, index):
        ind = index
        s_type = particle
        source_keys = keys
        source = main_tree

        jj = 0
        lb = s_type.split()[-1]
        part = self.tree[ind].insert(source, 2, text=lb, open=True)
        if any(['Boundaries' in s_key for s_key in source_keys]):
            jj += 1
            boundary_source = self.tree[ind].insert(part, jj, text='С границ', open=True)
        if any(['Flu' in s_key for s_key in source_keys]):
            jj += 1
            surface_source = self.tree[ind].insert(part, jj, text='Поверхностные', open=True)
        if any(['Volume78' in s_key for s_key in source_keys]) or any(['Volume' in s_key for s_key in source_keys]):
            jj += 1
            volume_source = self.tree[ind].insert(part, jj, text='Объёмные', open=True)

        for i, s_key in enumerate(source_keys):
            if 'Flu' in s_key:
                self.tree[ind].insert(surface_source, i, text=f'{s_key}', open=True)

            elif 'Volume78' in s_key:
                self.tree[ind].insert(volume_source, i, text=f'{s_key}', open=True)

            elif 'Volume' in s_key:
                self.tree[ind].insert(volume_source, i, text=f'{s_key}', open=True)

            elif 'Boundaries' in s_key:
                self.tree[ind].insert(boundary_source, i, text=f'{s_key}', open=True)

        self.update()
        w = self.notebook.winfo_width()
        h = self.notebook.winfo_height()
        if w > 500:
            self.parent.geometry(f'{w}x{h}')

    def __tree_select_react(self, index, name, e):
        # print([self.tree[-1].item(x) for x in self.tree[-1].selection()])

        # data_frame = self.tabs_dict[name][-1].winfo_children()[-1]

        db_object = self.global_tree_db[name]
        s_list = []
        for i in db_object.get_first_level_keys():
            for j in db_object.get_second_level_keys(i):
                s_list.append(j)

        for x in self.tree[index].selection():
            # print(self.tree[index].item(x))
            # time function frame creation
            if self.tree[index].item(x)['text'] in self.global_tree_db.keys():
                if self.tabs_dict[name][2] is False:
                    self.__destroy_data_frame(name)
                    fr_data = FrameGen(self.tabs_dict[name][1], self.path, self.global_tree_db[name],
                                       (self.notebook, self.parent))
                    if self.global_tree_db[name].get_share_data('count') is not None:
                        fr_data.cell_numeric = len(self.global_tree_db[name].get_share_data('time_full'))
                        fr_data._notebooks()
                        fr_data.load_data()
                    else:
                        fr_data._notebooks()
                        fr_data.set_amplitude()

                    self.tabs_dict[name][2] = True
                    fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='WN')

            elif self.tree[index].item(x)['text'] in s_list:
                self.__destroy_data_frame(name)
                self.tabs_dict[name][2] = False

                fr_data = self.__create_data_frame(name)

                # find first level key
                first_key = None
                second_key = None
                for f_key in db_object.get_first_level_keys():
                    for s_key in db_object.get_second_level_keys(f_key):
                        if s_key == self.tree[index].item(x)['text']:
                            en_type = db_object.get_last_level_data(f_key, s_key, 'energy_type')
                            first_key, second_key = f_key, s_key
                            break

                ex = StandardizedSourceMainInterface(fr_data,
                                                     self.path,
                                                     self.global_tree_db,
                                                     name,
                                                     first_key,
                                                     second_key)

                fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='NWSE')

            else:
                self.__destroy_data_frame(name)
                self.tabs_dict[name][2] = False

    def add_part(self, index, name, id):

        if self.PAR is None:
            print('Файл .PAR не инициализирован')
            mb.showerror('error', 'Файл .PAR не инициализирован')
            return

        part_list = [i for i in self.PAR.keys()]

        for gsource in self.global_tree_db.keys():
            for i in self.global_tree_db[gsource].get_first_level_keys():
                if any([j == i for j in part_list]):
                    # ask = mb.askyesno('Внимание', f'Частица уже используется в "{gsource}"\n'
                    #                               f'Добавить частицу {new_particle} в "{name}"?')
                    print(f'Частица {i} уже используется')
                    part_list.pop(part_list.index(i))

        if len(part_list) == 0:
            mb.showerror('Ошибка', 'Нет доступных частиц')
            return

        a = SelectParticleDialog(part_list)
        self.wait_window(a)
        new_particle = a.lb_current
        if new_particle is None:
            return

        if self.PAR[new_particle]['type'] == 7 or self.PAR[new_particle]['type'] == 8:
            self._activate_micro_electronics_menubar()

        source = self.tree[index].get_children()[0]

        if new_particle not in self.global_tree_db[name].get_first_level_keys():

            self.global_tree_db[name].insert_first_level(new_particle)

            self.tree_db_insert_particle(self.global_tree_db[name], new_particle)

            source_keys = self.global_tree_db[name].get_second_level_keys(new_particle)

            self.particle_tree_constr(new_particle, source_keys, source, index)


        else:
            print('Объект уже существует')

    def _left_button_menu(self, name, index, event):

        iid = self.tree[index].identify_row(event.y)
        if iid:
            particle_list = []
            sources_list = []
            for key in self.global_tree_db[name].get_first_level_keys():
                if 'Current' not in key and 'Energy' not in key:
                    particle_list.append(key)
                for item in self.global_tree_db[name].get_second_level_keys(key):
                    sources_list.append(item)

            influence = name

            if self.tree[index].item(iid)['text'] == influence:
                self.contextMenu = tk.Menu(tearoff=0)

                self.contextMenu.add_command(label="Добавить частицу",
                                             command=lambda: self.add_part(index, name, iid),
                                             state='normal')

                self.contextMenu.add_command(label="Восстановить источники токов",
                                             command=lambda: self.__restore_currents(influence, index))

                self.contextMenu.add_command(label="Восстановить источники энерговыделения",
                                             command=lambda: self.__restore_energy_distribution(influence, index))

                self.contextMenu.add_command(label="Удалить воздействие",
                                             command=lambda: self.__tree_view_deconstructor(influence))

                self.tree[index].selection_set(iid)
                self.contextMenu.post(event.x_root, event.y_root)

            elif 'Current' in self.tree[index].item(iid)['text'] or 'Energy' in self.tree[index].item(iid)['text']:
                self.contextMenu = tk.Menu(tearoff=0)

                self.contextMenu.add_command(label="Удалить", command=lambda: self.delete_particle(index, name, iid),
                                             state='normal')

                self.tree[index].selection_set(iid)
                self.contextMenu.post(event.x_root, event.y_root)

            elif any([i in self.tree[index].item(iid)['text'] for i in particle_list]):
                self.contextMenu = tk.Menu(tearoff=0)

                self.contextMenu.add_command(label="Удалить", command=lambda: self.delete_particle(index, name, iid),
                                             state='normal')

                self.tree[index].selection_set(iid)
                self.contextMenu.post(event.x_root, event.y_root)

            else:
                pass

    def delete_particle(self, index, name, id):
        first_list = []
        second_list = []
        for key in self.global_tree_db[name].get_first_level_keys():
            first_list.append(key.split()[-1])
            for item in self.global_tree_db[name].get_second_level_keys(key):
                second_list.append(item)

        if self.tree[index].item(id)['text'] in first_list:
            for i in self.global_tree_db[name].get_first_level_keys():
                if self.tree[index].item(id)['text'] in i:
                    f_key = i
                    break
            try:
                self.global_tree_db[name].delete_first_level(f_key)
            except:
                print('The object can not be deleted')
                return
            self.tree[index].delete(id)

        elif self.tree[index].item(id)['text'] in second_list:
            s_key = self.tree[index].item(id)['text']
            self.global_tree_db[name].delete_second_level(s_key)
            self.tree[index].delete(id)

        else:
            print('The object can not be deleted')

    def __tree_view_deconstructor(self, selection=None):
        if selection is None:
            data = [i for i in self.global_tree_db.keys()]

            a = DeleteGSourceDialog(data)
            self.wait_window(a)
            delete_gsource = a.lb_current
            if delete_gsource is None:
                return

        elif selection is not None:
            delete_gsource = selection

        else:
            return

        self.notebook.forget(self.tabs_dict[delete_gsource][0])
        self.tree.pop(self.tabs_dict[delete_gsource][0])
        self.tabs_dict.pop(delete_gsource)
        self.global_tree_db.pop(delete_gsource)

        for item in self.tabs_dict.items():
            if item[1][0] > len(self.tabs_dict) - 1:
                item[1][0] -= 1

        for item in self.tabs_dict.items():
            index = item[1][0]

            self.tree[index].bind("<<TreeviewSelect>>",
                                  lambda _,
                                         name=item[0],
                                         sv=index:
                                  self.__tree_select_react(sv, name, _))

            self.tree[index].bind("<Button-3>", lambda _,
                                                       index=index,
                                                       name=item[0]: self._left_button_menu(name, index, _))

    @logger.catch()
    def save(self):
        ex = Save_remp(self._marple, self._micro_electronics, self.global_tree_db, self.path)

    def __restore_currents(self, object_name, index):

        obj = self.global_tree_db[object_name]
        create_list = ['x', 'y', 'z']

        for i in range(self.LAY.shape[0]):
            if self.LAY[i, 1] == 1:
                for axis in create_list:
                    energy_type = f'Ток по оси {axis} слой {self.layer_numbers[i]}'
                    name = f'Current_{axis}_layer_{self.layer_numbers[i]}'
                    d = f'J{axis.upper()}_{self.layer_numbers[i]}'

                    if name not in obj.get_second_level_keys('Current'):
                        obj.insert_second_level('Current', f'{name}', {})

                        obj.insert_third_level('Current', f'{name}', 'name', name)
                        obj.insert_third_level('Current', f'{name}', 'energy_type', energy_type)
                        obj.insert_third_level('Current', f'{name}', 'distribution', None)

                        self.tree[index].insert(self.__current_tree_view_section, i, text=f'{name}', open=True)

    def __restore_energy_distribution(self, object_name, index):

        obj = self.global_tree_db[object_name]

        for i in range(self.LAY.shape[0]):
            if self.LAY[i, 2] == 1:
                energy_type = 'Energy'
                name = f'Energy_layer_{self.layer_numbers[i]}'
                if name not in obj.get_second_level_keys('Energy'):
                    obj.insert_second_level('Energy', f'{name}', {})

                    obj.insert_third_level('Energy', f'{name}', 'name', name)
                    obj.insert_third_level('Energy', f'{name}', 'energy_type', energy_type)
                    obj.insert_third_level('Energy', f'{name}', 'distribution', None)

                    self.tree[index].insert(self.__energy_tree_view_section, i, text=f'{name}', open=True)

    def __add_source_button(self):
        # if len(self.global_tree_db) >= len(self.PAR):
        #     ask = mb.askyesno('Внимание', 'Количество частиц больше количества воздействий.\nСоздать новую чатицу?')
        #     if ask is False:
        #         return
        self.tree_view_constructor()

    def __destroy_data_frame(self, name):
        if len(self.tabs_dict[name][1].winfo_children()) < 2:
            return
        d_frame = self.tabs_dict[name][1].winfo_children()[-1]
        d_frame.grid_forget()
        d_frame.destroy()

    def __create_data_frame(self, name):
        fr_data = ttk.Frame(self.tabs_dict[name][1])
        fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='WN')

        return fr_data

    def __add_marple(self):
        if self._marple is not None and all([i is not None for i in self._marple.values()]):

            tup = tuple(self._marple.values())
            ex = MarpleElectronicsInterface(self.path,
                                            'Проводимость',
                                            'Степень ионизации',
                                            'Создание источника обтекания',
                                            tup)

        else:
            ex = MarpleElectronicsInterface(self.path,
                                            'Проводимость',
                                            'Степень ионизации',
                                            'Создание источника обтекания')
        self.wait_window(ex)

        ion = ex.first_item
        sigma = ex.second_item

        if ion is None or sigma is None:
            return

        # self.marple_menu.entryconfigure(0, state='disabled')
        self.marple_menu.entryconfigure(1, state='normal')

        self._marple = {'ion': ion, 'sigma': sigma}
        self._save_flag = True

        mb.showinfo('Задача обтекания', 'Задача обтекания будет добавлена в remp source при сохранении проекта')

    def __delete_marple(self):
        self.marple_menu.entryconfigure(0, state='normal')
        self.marple_menu.entryconfigure(1, state='disabled')

        mb.showinfo('Задача обтекания', 'Задача обтекания не будет сохранёна в remp source')

        self._marple = None
        self._save_flag = True

    def __add_microel(self):

        if self._micro_electronics is not None and all([i is not None for i in self._micro_electronics.values()]):

            tup = tuple(self._micro_electronics.values())
            ex = MarpleElectronicsInterface(self.path,
                                            'Рабочее поле в изделии микроэлектроники',
                                            'Собственная концентрация электронов проводимости\nи дырок волентной зоны',
                                            'Задание параметров для изделий микроэлектроники',
                                            tup)

        else:
            ex = MarpleElectronicsInterface(self.path,
                                            'Рабочее поле в изделии микроэлектроники',
                                            'Собственная концентрация электронов проводимости\nи дырок волентной зоны',
                                            'Задание параметров для изделий микроэлектроники', )
        self.wait_window(ex)

        field = ex.field78_path
        density = ex.density78_path

        if field is None or density is None:
            return

        # self.electronics_menu.entryconfigure(0, state='disabled')
        self.electronics_menu.entryconfigure(1, state='normal')

        self._micro_electronics = {'field78': field, 'density78': density}
        self._save_flag = True

        mb.showinfo('Микроэлектроника', 'Микроэлектроника будет добавлена в remp source при сохранении проекта')

    def __delete_microel(self):
        self.electronics_menu.entryconfigure(0, state='normal')
        self.electronics_menu.entryconfigure(1, state='disabled')

        mb.showinfo('Marple', 'Marple не будет сохранён в remp source')

        self._micro_electronics = None
        self._save_flag = True
