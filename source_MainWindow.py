import pickle
from tkinter import simpledialog as sd
from tkinter import ttk
from typing import List, Dict
from collections import namedtuple

import numpy as np
from loguru import logger

from remp_parameters_tests import main_test as remp_files_test
from source_Dialogs import SelectParticleDialog, DeleteGSourceDialog, SelectLagInterface, MarpleElectronicsInterface
from source_MW_interface_classes import StandardizedSourceMainInterface
from source_Main_frame import FrameGen
from source_PE_SOURCE import PeSource
from source_Project_reader import DataParser, SubtaskDecoder
from source_Save_for_remp import Save_remp
from source_utility import *


@logger.catch()
class MainWindow(tk.Frame):
    def __init__(self, parent, path=None, projectfilename=None):
        super().__init__(parent)
        self.parent = parent
        self.path = None

        self.parent.protocol("WM_DELETE_WINDOW", self.__onExit)

        self.prj_path: str

        self.notebook: ttk.Notebook
        self.tabs_dict: Dict[int, List[int, tk.Frame, bool]] = {}
        self.tree: List[ttk.Treeview] = []
        self.global_tree_db: Dict[str, TreeDataStructure] = {}
        self._influence_numbers = set()

        self.__toolbar()

        self._marple = None
        self._micro_electronics = None

        self._save_flag: bool = False

        self.lag = None

        try:
            if projectfilename is not None:
                if os.path.exists(projectfilename):
                    self.prj_path = projectfilename
                    self.path = os.path.split(self.prj_path)[0]
                    self.__check_project()
            else:
                raise Exception
        except Exception:
            self.path = path

    def __set_influence_number(self):
        i = 1
        while True:
            if not self._influence_numbers.__contains__(i):
                self._influence_numbers.add(i)
                break
            else:
                i += 1

        return i

    def __from_project_reader(self):

        # self.tok_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('TOK')))
        self.pl_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PL')))
        self.lay_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('LAY')))
        self.par_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PAR')))
        self.grd_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('GRD')))

        self._time_grid_data = DataParser(self.grd_dir).grid_parcer()

        # self.TOK = DataParcer(self.tok_dir).tok_decoder()
        if self.pl_dir is not None and os.path.exists(self.pl_dir):
            self.PL_surf, self.PL_vol, self.PL_bound, self.layer_numbers = DataParser(self.pl_dir).pl_decoder()
            if self.PL_surf is None:
                mb.showerror('ERROR', 'Нарушена структура файла PL')
                return
        else:
            self.PL_surf, self.PL_vol, self.PL_bound, self.layer_numbers = None, None, None, None

        if os.path.exists(self.lay_dir):
            self.LAY, self.PPN = DataParser(self.lay_dir).lay_decoder()
            if self.layer_numbers is None:
                self.layer_numbers = self.LAY[:, 0]
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

    def __toolbar(self):
        self.parent.title("Sources")
        self.menubar = tk.Menu(self.parent, postcommand=self.update)
        self.parent.config(menu=self.menubar)

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Файл", menu=self.filemenu)
        self.recent_pr_menu = tk.Menu(self.filemenu, tearoff=0)

        self.filemenu.add_command(label="Открыть проект", command=self.__browse_folder)

        funcs = [(lambda k: lambda: self.__browse_from_recent(k))(key) for key in get_recent_projects().keys()]
        for key, f in zip(get_recent_projects().keys(), funcs):
            self.recent_pr_menu.add_command(label=f'{key}', command=f)

        self.filemenu.add_cascade(label="Недавние проекты", menu=self.recent_pr_menu)

        self.filemenu.add_command(label="Сохранение для РЭМП", command=self.__save, state='disabled')

        self.filemenu.add_command(label="Открыть папку с проектом", command=self.__open_folder, state='disabled')

        self.filemenu.add_command(label="Направление воздействия", command=self.__configure_lag, state='disabled')

        self.filemenu.add_command(label="Exit", command=self.__onExit)

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

        self.menubar.add_command(label="Добавить спектр переноса", state='disabled', command=self.__start_pechs)

        # self._create_micro_electronics_menubar()

    def __create_micro_electronics_menubar(self):

        self.electronics_menu = tk.Menu(self.menubar, tearoff=0)

        self.menubar.add_cascade(label="Микроэлектроника", menu=self.electronics_menu, state='disabled')

        self.electronics_menu.add_command(label="Добавить файлы микроэлектроники", command=self.__add_microel,
                                          state='normal')
        self.electronics_menu.add_command(label="Удалить  файлы микроэлектроники", command=self.__delete_microel,
                                          state='disabled')

    def __activate_micro_electronics_menubar(self, state='normal'):
        microele_index = self.menubar.index('Микроэлектроника')
        self.menubar.entryconfigure(microele_index, state=state)

    def __menubar_activate(self):
        add_index = self.menubar.index('Добавить воздействие')
        del_index = self.menubar.index('Удалить воздействие')

        open_folder_index = self.filemenu.index('Открыть папку с проектом')
        save_for_remp_index = self.filemenu.index('Сохранение для РЭМП')
        configure_lag_index = self.filemenu.index('Направление воздействия')

        self.filemenu.entryconfigure(open_folder_index, state='normal')
        self.filemenu.entryconfigure(save_for_remp_index, state='normal')
        self.filemenu.entryconfigure(configure_lag_index, state='normal')

        self.menubar.entryconfigure(add_index, state='normal')
        self.menubar.entryconfigure(del_index, state='normal')

        marple_index = self.menubar.index('Задача обтекания')
        self.menubar.entryconfigure(marple_index, state='normal')

        pechs_index = self.menubar.index('Добавить спектр переноса')
        self.menubar.entryconfigure(pechs_index, state='normal')

    def __start_pechs(self):
        ex = PeSource(self.path, self.parent)
        ex.main_calculation()

    def __check_saved_ds(self, db, saved_db):
        same = True
        for key in saved_db.keys():
            if db[key].get_dict_object() != saved_db[key].get_dict_object():
                same = False
                return same
        return same

    def __set_lag(self):
        sub = SubtaskDecoder(self.path)

        if sub.subtask_path is not None:
            x, y, z = sub.get_subtask_koord()
            self.lag = f'1 {x} {y} {z}'
            print('Параметр задержки взята из файла подзадачи')

        else:
            ask = mb.askyesno('Файл подзадачи не найден',
                              'Направление воздействия не найдено в файле подзадачи.\n'
                              'Активировать меню выбора направления воздействия?\n\n'
                              'Да  - запустить меню редактора\n'
                              'Нет - игнорировать направление воздействия')

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

    def __configure_lag(self):

        # for name in self.global_tree_db.keys():
        #     self.lag = self.global_tree_db[name].get_share_data('lag')
        #     break

        try:
            if self.lag is None:
                raise Exception

            a = list(map(float, self.lag.strip().split()[1:]))

        except Exception:
            a = []

        ex = SelectLagInterface(self.path, a)

        if self.lag == '0':
            ex._enable_var.set(0)
        else:
            ex._enable_var.set(1)

        ex.en_change()

        self.wait_window(ex)

        x, y, z = ex.vector_data

        if any([i is None for i in [x, y, z]]):
            self.lag = f'0'
        else:
            self.lag = f'1 {x} {y} {z}'

        for name in self.global_tree_db.keys():
            self.global_tree_db[name].insert_share_data('lag', self.lag)

    def __save_check_flags(self, ask):
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

    def __onExit(self):
        if len(self.global_tree_db) == 0:
            self.parent.quit()
            self.parent.destroy()
            return

        if 'Sources.pkl' in os.listdir(self.path):
            try:
                with open(os.path.join(self.path, 'Sources.pkl'), 'rb') as f:
                    load_db = pickle.load(f)
            except Exception:
                mb.showerror('Error', 'Ошибка при попытке прочитать бинарный файл сохранения. Сохраните проект зново')
                ask1 = mb.askyesno('Сохранение', 'Ошибка при попытке прочитать бинарный файл сохранения.'
                                                 'Сохранить проект заново?')
                self.__save_check_flags(ask1)
                return

            if load_db.keys() == self.global_tree_db.keys() and not self._save_flag:
                if self.__check_saved_ds(load_db, self.global_tree_db) is True:
                    self.parent.quit()
                    self.parent.destroy()
                    return

        ask = mb.askyesno('Сохранение', 'Сохранить файл?')
        self.__save_check_flags(ask)

    def __browse_from_recent(self, path):
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
        self.__check_project()

    def __browse_folder(self):
        """Инициализирует страт приложения"""
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
        self.__check_project()

    def __check_folder(self):

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

    def __reset(self):
        if self.path is None:
            return
        self.notebook.destroy()
        self.notebook = None
        self.tabs_dict = {}
        self.tree = []
        self.global_tree_db = {}
        self._influence_numbers.clear()

    @logger.catch()
    def __check_project(self):
        """
        Логика по созданию пустого окна и загрузке файла Source.pkl (ранее сохраненный remp_sources).
        """
        if self.path is None:
            return

        try:
            self.__reset()
        except Exception:
            pass

        self.file_dict = self.__check_folder()

        set_recent_projects(self.prj_path, get_recent_projects())

        log_path = os.path.join(self.path, 'sources_debug.log')
        logger.add(log_path, format="{time} {level} {message}",
                   level='ERROR', rotation='10MB', compression='zip')

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid(sticky='NWSE')

        if self.__from_project_reader() != 0:
            return
        self.parent.title(f'Source - открыт проект {os.path.normpath(self.prj_path)}')
        # self._activate_micro_electronics_menubar(state='disabled')

        load_lag = True

        if 'remp_sources' in os.listdir(self.path):
            ask = mb.askyesno('Обнаружен rems source', 'Обнаружен файл remp source\nЗагрузить данные?')
            if ask is True:
                l = PreviousProjectLoader(self.path,
                                          [self.PAR, self.LAY, self.PL_surf, self.PL_vol, self.PL_bound,
                                           self.layer_numbers])
                if l.loaded_flag:  # load successfully
                    self.global_tree_db, self.lag = l.get_db_and_lag()
                    load_lag = False
                    self.__construct_loaded_data()
        if load_lag:
            self.__set_lag()

        self.__menubar_activate()

    def __construct_loaded_data(self):
        for i in self.global_tree_db.items():
            try:
                part_number_tuple = self.global_tree_db[i[0]].get_share_data('particle number')

                if type(part_number_tuple) is not set:
                    part_number_tuple = {part_number_tuple}
                    self.global_tree_db[i[0]].insert_share_data('particle number', part_number_tuple)

            except KeyError:
                part_number_tuple = None

            load_data = namedtuple('load_data', [
                'influence_name',
                'particle_numbers',
                'particle_names'
            ])
            self.__tree_view_constructor(load=True, ask_name=False, load_data=(i[0], part_number_tuple))

    def __open_folder(self):
        if self.path is None:
            return
        os.startfile(self.path)

    def __tree_db_insert(self, obj_name, number):
        obj = TreeDataStructure(obj_name)

        create_list = ['x', 'y', 'z']
        obj.insert_share_data('lag', self.lag)
        obj.insert_share_data('influence number', str(number))

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
                        obj.get_share_data('influence number'),
                        self.layer_numbers[i],
                        f'j{axis.lower()}')

                    obj.insert_third_level('Current', f'{name}', 'distribution', current_file)

            if self.LAY[i, 2] == 1:
                energy_type = 'Sigma'
                name = f'Sigma_layer_{self.layer_numbers[i]}'
                obj.insert_second_level('Sigma', f'{name}', {})

                obj.insert_third_level('Sigma', f'{name}', 'name', name)
                obj.insert_third_level('Sigma', f'{name}', 'energy_type', energy_type)

                current_file = DataParser(self.path).get_distribution_for_current_and_energy(
                    obj.get_share_data('influence number'),
                    self.layer_numbers[i],
                    f'en')
                obj.insert_third_level('Sigma', f'{name}', 'distribution', current_file)

        return obj

    def __tree_db_insert_particle(self, obj_name, particle, load=False):
        obj = obj_name

        boundaries_decode = {0: 'X', 1: 'Y', 2: 'Z', 3: '-X', 4: '-Y', 5: '-Z'}
        boundaries_decode_f = {'X': 'xmax_part', 'Y': 'ymax_part', 'Z': 'zmax_part',
                               '-X': 'xmin_part', '-Y': 'ymin_part', '-Z': 'zmin_part', }

        distr_list = DataParser(self.path + '/').distribution_reader()
        b_list = DataParser(self.path + '/').get_spectre_for_bound()

        number = self.PAR[particle]['number']
        type = self.PAR[particle]['type']
        influence_number = int(obj.get_share_data('influence number'))

        obj.insert_share_data('particle number', {*obj.get_share_data('particle number'), self.PAR[particle]['number']})

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

                        current_file = DataParser(self.path).get_distribution_for_current_and_energy(influence_number,
                                                                                                     self.layer_numbers[
                                                                                                         i],
                                                                                                     f'j{axis.lower()}')
                        obj.insert_third_level('Current', f'{name}', 'distribution', current_file)

                if self.LAY[i, 2] == 1:
                    energy_type = 'Sigma'
                    name = f'Sigma_layer_{self.layer_numbers[i]}'
                    if name in obj.get_second_level_keys('Sigma'):
                        continue

                    obj.insert_second_level('Sigma', f'{name}', {})

                    obj.insert_third_level('Sigma', f'{name}', 'name', name)
                    obj.insert_third_level('Sigma', f'{name}', 'energy_type', energy_type)

                    current_file = DataParser(self.path).get_distribution_for_current_and_energy(influence_number,
                                                                                                 self.layer_numbers[i],
                                                                                                 f'en')
                    obj.insert_third_level('Sigma', f'{name}', 'distribution', current_file)

        ar = self.PL_surf.get(number)

        assert ar is not None

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

                distr = DataParser(self.path).get_distribution_for_current_and_energy(influence_number,
                                                                                      self.layer_numbers[i],
                                                                                      'en')
                sp, sp_number = self.__find_spectre78_in_project(type, self.layer_numbers[i])

                obj.insert_third_level(f'{particle}', f'{name}', 'spectre', [sp])
                obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers', [sp_number])
                obj.insert_third_level(f'{particle}', f'{name}', 'distribution', [distr])

                if distr is None:
                    print(f'Автоматичеки не найдено распределение для {name}')

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

                            obj.insert_third_level(particle, name, 'spectre', [file])
                            obj.insert_third_level(particle, name, 'spectre numbers', [sp_number])

    @logger.catch()
    def __tree_view_constructor(self, ask_name=True, load=False, load_data=None):
        influence_number = self.__set_influence_number()

        if ask_name is True:
            while True:
                name = sd.askstring('Назовите воздействие', 'Введите название воздействия (Английский язык)\n'
                                                            'Ok - название по умолчанию')
                if name == '':
                    name = f'Influence {influence_number}'
                if name is None:
                    return
                if russian_words_analysis(name) == 1:
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
            except Exception:
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
        microele_flag_activate = False

        if load is False:
            self.global_tree_db.update({name: self.__tree_db_insert(name, influence_number)})
            fr_data = FrameGen(fr, self.path, self.global_tree_db[name], (self.notebook, self.parent),
                               self._time_grid_data)
            fr_data.configure(text=self.global_tree_db[name].obj_name + f'  № {influence_number}')
            fr_data._notebooks()

        elif load is True:

            part_name = None
            load_particles = [load_data[1]] if load_data[1] is None else load_data[1]
            for particle_from_load in load_particles:
                for i in self.PAR.keys():
                    if self.PAR[i]['number'] == particle_from_load:
                        part_name = i

                        if self.PAR[i]['type'] == 7 or self.PAR[i]['type'] == 8:
                            microele_flag_activate = True  # для активаци меню микроэлектроники, которое сейчас отключено
                        break

                if part_name is not None and part_name in self.global_tree_db[
                    name].get_first_level_keys():  # костыль для загрузки в структуры воздействий без частиц
                    self.__tree_db_insert_particle(self.global_tree_db[name], part_name, True)
                    source_keys = self.global_tree_db[name].get_second_level_keys(part_name)
                    self.__particle_tree_constr(part_name, source_keys, source, ind)

            fr_data = FrameGen(fr, self.path, self.global_tree_db[name], (self.notebook, self.parent),
                               self._time_grid_data)
            fr_data.configure(text=self.global_tree_db[name].obj_name + f'  № {influence_number}')

            if self.global_tree_db[name].get_share_data('count') is not None:
                fr_data.cell_numeric = len(self.global_tree_db[name].get_share_data('time_full'))
                fr_data._notebooks()
                fr_data.load_data()

        for index, s_type in enumerate(self.global_tree_db[name].get_first_level_keys()):
            source_keys = self.global_tree_db[name].get_second_level_keys(s_type)
            if len(source_keys) == 0:
                continue
            if any(['Sigma' in s_key for s_key in source_keys]):
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
                                                 name=name: self.__left_button_menu(name, index, _))

        self.notebook.add(fr, text=f'{name}')
        self.tabs_dict.update({name: [len(self.tabs_dict), fr, True]})

    def __particle_tree_constr(self, particle, keys, main_tree, index):
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
                                       (self.notebook, self.parent), self._time_grid_data)
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

    def __add_part(self, index, name, id):

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

        # if self.PAR[new_particle]['type'] == 7 or self.PAR[new_particle]['type'] == 8:
        #     self._activate_micro_electronics_menubar()

        source = self.tree[index].get_children()[0]

        if new_particle not in self.global_tree_db[name].get_first_level_keys():

            self.global_tree_db[name].insert_first_level(new_particle)

            self.__tree_db_insert_particle(self.global_tree_db[name], new_particle)

            source_keys = self.global_tree_db[name].get_second_level_keys(new_particle)

            self.__particle_tree_constr(new_particle, source_keys, source, index)


        else:
            print('Объект уже существует')

    def __check_all_particles_is_used(self):
        if self.PAR is None:
            return True

        part_list = [i for i in self.PAR.keys()]
        for gsource in self.global_tree_db.keys():
            for i in self.global_tree_db[gsource].get_first_level_keys():
                if any([j == i for j in part_list]):
                    part_list.pop(part_list.index(i))
        return True if len(part_list) == 0 else False

    def __left_button_menu(self, name, index, event):

        iid = self.tree[index].identify_row(event.y)
        if iid:
            particle_list = []
            sources_list = []
            for key in self.global_tree_db[name].get_first_level_keys():
                if 'Current' not in key and 'Sigma' not in key:
                    particle_list.append(key)
                for item in self.global_tree_db[name].get_second_level_keys(key):
                    sources_list.append(item)

            influence = name

            if self.tree[index].item(iid)['text'] == influence:
                self.contextMenu = tk.Menu(tearoff=0)

                self.contextMenu.add_command(label="Добавить частицу",
                                             command=lambda: self.__add_part(index, name, iid),
                                             state='normal')

                if any([self.LAY[i, 1] == 1 for i in range(self.LAY.shape[0])]):
                    self.contextMenu.add_command(label="Восстановить источники токов",
                                                 command=lambda: self.__restore_currents(influence, index),
                                                 state='normal')
                else:
                    self.contextMenu.add_command(label="Восстановить источники токов",
                                                 command=lambda: self.__restore_currents(influence, index),
                                                 state='disabled')

                if any([self.LAY[i, 2] == 1 for i in range(self.LAY.shape[0])]):
                    self.contextMenu.add_command(label="Восстановить источники энерговыделения",
                                                 command=lambda: self.__restore_energy_distribution(influence, index),
                                                 state='normal')
                else:
                    self.contextMenu.add_command(label="Восстановить источники энерговыделения",
                                                 command=lambda: self.__restore_energy_distribution(influence, index),
                                                 state='disabled')

                self.contextMenu.add_command(label="Удалить воздействие",
                                             command=lambda: self.__tree_view_deconstructor(influence))

                self.tree[index].selection_set(iid)
                self.contextMenu.post(event.x_root, event.y_root)

            elif 'Current' in self.tree[index].item(iid)['text'] or 'Sigma' in self.tree[index].item(iid)['text']:
                self.contextMenu = tk.Menu(tearoff=0)

                self.contextMenu.add_command(label="Удалить", command=lambda: self.__delete_particle(index, name, iid),
                                             state='normal')

                self.tree[index].selection_set(iid)
                self.contextMenu.post(event.x_root, event.y_root)

            elif any([i in self.tree[index].item(iid)['text'] for i in particle_list]):
                self.contextMenu = tk.Menu(tearoff=0)

                self.contextMenu.add_command(label="Удалить", command=lambda: self.__delete_particle(index, name, iid),
                                             state='normal')

                self.tree[index].selection_set(iid)
                self.contextMenu.post(event.x_root, event.y_root)

            else:
                pass

    def __delete_particle(self, index, name, id):
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
                    try:
                        self.global_tree_db[name].delete_first_level(f_key)
                    except Exception:
                        print('The object can not be deleted')
                        return
                    finally:
                        break

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
        self._influence_numbers.remove(int(self.global_tree_db[delete_gsource].get_share_data('influence number')))

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
                                                       name=item[0]: self.__left_button_menu(name, index, _))

    @logger.catch()
    def __save(self):
        if not self.__check_all_particles_is_used():
            ask = mb.askyesno('Внимание', f'Обнаружены неиспользуемые частицы.\n'
                                          'Использование данного проектра в расчете приведет к ошибке!\n'
                                          'Сохранить?')
            if not ask:
                return
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

                        try:
                            self.tree[index].insert(self.__current_tree_view_section, i, text=f'{name}', open=True)
                        except AttributeError:
                            print('Не отрисован сторонний ток')

    def __restore_energy_distribution(self, object_name, index):

        obj = self.global_tree_db[object_name]

        for i in range(self.LAY.shape[0]):
            if self.LAY[i, 2] == 1:
                energy_type = 'Sigma'
                name = f'Sigma_layer_{self.layer_numbers[i]}'
                if name not in obj.get_second_level_keys('Sigma'):
                    obj.insert_second_level('Sigma', f'{name}', {})

                    obj.insert_third_level('Sigma', f'{name}', 'name', name)
                    obj.insert_third_level('Sigma', f'{name}', 'energy_type', energy_type)
                    obj.insert_third_level('Sigma', f'{name}', 'distribution', None)

                    self.tree[index].insert(self.__energy_tree_view_section, i, text=f'{name}', open=True)

    def __add_source_button(self):
        # if len(self.global_tree_db) >= len(self.PAR):
        #     ask = mb.askyesno('Внимание', 'Количество частиц больше количества воздействий.\nСоздать новую чатицу?')
        #     if ask is False:
        #         return
        self.__tree_view_constructor()
        self.notebook.select(self.notebook.tabs()[-1])

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

        field = ex.first_item
        density = ex.second_item

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

    def __find_spectre78_in_project(self, part_type, lay_number):
        ppn = self.PPN[lay_number]['ppn']

        if part_type == 7 and ppn in (2, 4, 5):
            sp = 'micr_1'
            number = self.__get_sp_number(sp)
            if number is None:
                sp, number = None, None

        elif part_type == 7 and ppn in (3,):
            sp = 'micr_3'
            number = self.__get_sp_number(sp)
            if number is None:
                sp, number = None, None

        elif part_type == 8 and ppn in (2, 4, 5):
            sp = 'micr_2'
            number = self.__get_sp_number(sp)
            if number is None:
                sp, number = None, None

        elif part_type == 8 and ppn in (3,):
            mb.showerror('Ошибка', 'Переход в диоксид запрещён!')
            sp, number = None, None

        else:
            sp, number = None, None

        return sp, number

    def __get_sp_number(self, fname):
        try:
            with open(os.path.join(self.path, fname), 'r') as file:
                lines = file.readlines()

                number = int(lines[2].strip())
        except Exception:
            number = None
            print(f'Спектр {fname} не найден в проекте')
        return number


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

        self.__start_reading()

    def get_db_and_lag(self):
        lag = self.global_tree_db[list(self.global_tree_db.keys())[0]].get_share_data('lag')
        return self.global_tree_db, lag

    def __delete_particles(self, db):
        delete_part_list = set()

        for f_key in db.get_first_level_keys():
            if 'Sigma' not in f_key and 'Current' not in f_key and 'Energy' not in f_key:
                part = db.get_share_data('particle number')

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

    def __start_reading(self):
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
