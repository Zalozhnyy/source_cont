import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd
import numpy as np
import os
import locale
import shutil
from scipy import integrate

from source_utility import *
from source_Project_reader import DataParser
from source_Save_for_remp import Save_remp
from source_Main_frame import FrameGen
from source_SpectreConfigure import SpectreConfigure
from source_Dialogs import SelectParticleDialog, DeleteGSourceDialog, SelectSpectreToView, MarpleInterface


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
                                                   'lag': None})

    def insert_share_data(self, key, value):
        # if key in self.__obj_structure['share_data'].keys():
        #     print(f'Ключ {key} был перезаписан')
        self.__obj_structure['share_data'].update({key: value})

        # print(self.__obj_structure['share_data'].values())

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


class MainWindow(tk.Frame):
    def __init__(self, parent, path=None, projectfilename=None):
        super().__init__(parent)
        self.parent = parent

        self.parent.protocol("WM_DELETE_WINDOW", self.onExit)

        self.prj_path = None

        self.notebook = None
        self.tabs_dict = {}
        self.tree = []
        self.global_tree_db = {}

        self.toolbar()

        self.global_count_gsources = 0

        self.main_frame_exist = False
        self.remp_source_exist = False

        self.marple = None

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
        self.PL_surf, self.PL_vol, self.PL_bound = DataParser(self.pl_dir).pl_decoder()
        self.LAY = DataParser(self.lay_dir).lay_decoder()
        self.PAR = DataParser(self.par_dir).par_decoder()

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

        # self.filemenu.add_command(label="Сохранить (output dicts)", command=lambda: timef_global_save(self.path))
        self.filemenu.add_command(label="Сохранение для РЭМП", command=self.save, state='disabled')

        self.filemenu.add_command(label="Открыть папку с проектом", command=self.open_folder, state='disabled')
        # self.filemenu.add_command(label="Очистить папку time functions", command=lambda: tf_global_del(self.path))
        # self.filemenu.add_command(label='Перезагрузка', command=self.reset)
        self.filemenu.add_command(label="Exit", command=self.onExit)

        self.menubar.add_command(label='Добавить воздействие',
                                 command=self.__add_source_button, state='disabled')
        self.menubar.add_command(label='Удалить воздействие', command=self.__tree_view_deconstructor, state='disabled')
        # self.menubar.add_command(label='Справка')
        # self.menubar.add_command(label='test', command=self.test)

        self.marple_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Marple", menu=self.marple_menu, state='disabled')

        self.marple_menu.add_command(label="Добавить Marple", command=self.__add_marple, state='normal')
        self.marple_menu.add_command(label="Удалить  Marple", command=self.__delete_marple, state='disabled')

    def menubar_activate(self):
        add_index = self.menubar.index('Добавить воздействие')
        del_index = self.menubar.index('Удалить воздействие')

        open_folder_index = self.filemenu.index('Открыть папку с проектом')
        save_for_remp_index = self.filemenu.index('Сохранение для РЭМП')

        self.menubar.entryconfigure(open_folder_index, state='normal')
        self.menubar.entryconfigure(save_for_remp_index, state='normal')

        self.filemenu.entryconfigure(add_index, state='normal')
        self.filemenu.entryconfigure(del_index, state='normal')

        marple_index = self.menubar.index('Marple')
        self.menubar.entryconfigure(marple_index, state='normal')

    def onExit(self):
        self.parent.quit()
        self.parent.destroy()

    def browse_from_recent(self, path):
        self.prj_path = path
        self.path = os.path.split(self.prj_path)[0]
        self.check_project()

    def browse_folder(self):
        self.prj_path = fd.askopenfilename(title='Укажите путь к проекту REMP', initialdir=f'{os.getcwd()}',
                                           filetypes=[('PRJ files', '.PRJ')])
        if self.prj_path == '' or self.prj_path is None:
            return None

        self.path = os.path.split(self.prj_path)[0]
        self.check_project()

    def folder_creator(self):
        dir = self.path

        if not os.path.exists(rf'{dir}/time functions'):
            os.mkdir(f'{dir}/time functions')
        if not os.path.exists(f'{dir}/time functions/user configuration'):
            os.mkdir(os.path.join(f'{dir}/time functions/user configuration'))
        if not os.path.exists(f'{dir}/time functions/output dicts'):
            os.mkdir(os.path.join(f'{dir}/time functions/output dicts'))

        if not os.path.exists(f'{dir}/time functions/Gursa'):
            os.mkdir(os.path.join(f'{dir}/time functions/Gursa'))

        if not os.path.exists(f'{dir}/time functions/TOK'):
            os.mkdir(os.path.join(f'{dir}/time functions/TOK'))

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

    def check_project(self):
        if self.path is None:
            return

        try:
            self.reset()
        except:
            pass

        self.file_dict = self.check_folder()
        if self.file_dict is None:
            mb.showerror('Project error', f'Файл .PRJ  не найден. Указана неправильная директория\n{self.path}')
            return
        set_recent_projects(self.prj_path, get_recent_projects())

        # self.folder_creator()  # создаём папку time functions
        # self.initial()

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid(sticky='NWSE')

        self.from_project_reader()
        self.lag = DataParser(self.path).pech_check()
        self.parent.title(f'Source - открыт проект {os.path.normpath(self.prj_path)}')

        if 'remp_sources' in os.listdir(self.path):

            ask = mb.askyesno('Обнаружен rems source', 'Обнаружен файл remp source\nЗагрузить данные из remp source?')

            if ask is True:

                self.rs_data = DataParser(os.path.join(self.path, 'remp_sources')).remp_source_decoder()
                self.remp_source_exist = True

                for p_number in self.rs_data.keys():
                    load_name = self.rs_data[p_number]['influence name']
                    part_number = self.rs_data[p_number]['particle number']

                    self.tree_view_constructor(load=True, ask_name=False, load_data=(load_name, part_number))

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

    def tree_db_insert(self, obj_name):
        obj = TreeDataStructure(obj_name)

        create_list = ['x', 'y', 'z']
        obj.insert_share_data('lag', self.lag)
        obj.insert_share_data('influence number', str(self.global_count_gsources))

        for i in range(self.LAY.shape[0]):
            if self.LAY[i, 1] == 1:
                for axis in create_list:
                    energy_type = f'Ток по оси {axis} слой {i}'
                    name = f'Current_{axis}_layer_{i}'
                    d = f'J{axis.upper()}_{i}'
                    obj.insert_second_level('Current', f'{name}', {})

                    obj.insert_third_level('Current', f'{name}', 'name', name)
                    obj.insert_third_level('Current', f'{name}', 'energy_type', energy_type)
                    # obj.insert_third_level('Current', f'{name}', 'spectre', None)
                    # obj.insert_third_level('Current', f'{name}', 'spectre numbers', None)
                    # obj.insert_third_level('Current', f'{name}', 'distribution', distr_list[distr_list.index(d)])
                    obj.insert_third_level('Current', f'{name}', 'distribution', None)

            if self.LAY[i, 2] == 1:
                energy_type = 'Energy'
                name = f'{energy_type}_layer_{i}'
                obj.insert_second_level('Energy', f'{name}', {})

                obj.insert_third_level('Energy', f'{name}', 'name', name)
                obj.insert_third_level('Energy', f'{name}', 'energy_type', energy_type)
                obj.insert_third_level('Energy', f'{name}', 'distribution', None)

        # if self.TOK[2] == 1:
        #     number = self.PAR[part_list[0]]['number']
        #
        #     energy_type = f'Gursa'
        #     name = f'Gursa_{number}'
        #
        #     obj.insert_second_level(f'{part_list[0]}', f'{name}', {})
        #
        #     obj.insert_third_level(f'{part_list[0]}', f'{name}', 'energy_type', energy_type)
        #     obj.insert_third_level(f'{part_list[0]}', f'{name}', 'name', name)
        #     obj.insert_third_level(f'{part_list[0]}', f'{name}', 'spectre', None)
        #     obj.insert_third_level(f'{part_list[0]}', f'{name}', 'spectre numbers', None)

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

            for i in self.rs_data[number].keys():
                if i == 'particle number' or i == 'influence name':
                    continue
                obj.insert_share_data('count', self.rs_data[number][i]['count'])
                time = self.rs_data[number][i]['time']
                obj.insert_share_data('time', time)
                func = self.rs_data[number][i]['func']
                obj.insert_share_data('func', func)
                obj.insert_share_data('amplitude',
                                      self.rs_data[number][i]['amplitude'] * integrate.trapz(
                                          x=np.array(time, dtype=float),
                                          y=np.array(func, dtype=float)))

            for i in range(self.LAY.shape[0]):
                if self.LAY[i, 1] == 1:
                    for axis in ['x', 'y', 'z']:
                        energy_type = 'Current'
                        name = f'{energy_type}_{axis}_layer_{i}'
                        try:
                            f = self.rs_data[number][name]['distribution']
                            if f in os.listdir(self.path):
                                obj.insert_third_level('Current', f'{name}', 'distribution', f)
                            else:
                                print(f'Файл {f} для источника {name} не обнаружен в проекте')
                                raise Exception
                        except:
                            obj.insert_third_level('Current', f'{name}', 'distribution', None)

                if self.LAY[i, 2] == 1:
                    energy_type = 'Energy'
                    name = f'{energy_type}_layer_{i}'

                    try:
                        f = self.rs_data[number][name]['distribution']
                        if f in os.listdir(self.path):
                            obj.insert_third_level('Energy', f'{name}', 'distribution', f)
                        else:
                            print(f'Файл {f} для источника {name} не обнаружен в проекте')
                            raise Exception
                    except:
                        obj.insert_third_level('Energy', f'{name}', 'distribution', None)

        ar = self.PL_surf.get(number)

        for i in range(ar.shape[0]):  # surfCE
            for j in range(0, ar.shape[1]):
                if ar[i, j] != 0:
                    energy_type = f'Источник частиц №{number} из {j}-го слоя в {i}-й'
                    name = f'Flu_e_{number}_{j}{i}'

                    obj.insert_second_level(f'{particle}', f'{name}', {})

                    obj.insert_third_level(f'{particle}', f'{name}', 'energy_type', energy_type)
                    obj.insert_third_level(f'{particle}', f'{name}', 'name', name)
                    obj.insert_third_level(f'{particle}', f'{name}', 'spectre', None)
                    obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers', None)

                    from_l = name.split('_')[-1][0]
                    to_l = name.split('_')[-1][1]
                    spectres = DataParser(self.path + '/').get_spectre_for_flux(number, from_l, to_l)

                    if len(spectres) == 6:
                        obj.insert_third_level(particle, name, 'spectre', [i for i in spectres.keys()])
                        obj.insert_third_level(particle, name, 'spectre numbers', [i for i in spectres.values()])

                    if load:
                        try:
                            spectre = [i for i in self.rs_data[number][name]['spectre'].split(' ')]
                            obj.insert_third_level(f'{particle}', f'{name}', 'spectre', spectre)

                            spectre_number = [i for i in self.rs_data[number][name]['spectre number'].split(' ')]
                            obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers', spectre_number)

                        except:
                            print(
                                f'Загрузка данных в {particle} {name} произошла с ошибкой или нет данных в remp sources')
                            if len(spectres) == 6:
                                obj.insert_third_level(particle, name, 'spectre', [i for i in spectres.keys()])
                                obj.insert_third_level(particle, name, 'spectre numbers',
                                                       [i for i in spectres.values()])
                            else:
                                obj.insert_third_level(particle, name, 'spectre', None)
                                obj.insert_third_level(particle, name, 'spectre numbers', None)

        for i in range(len(self.PL_vol[number])):  # volume
            if self.PL_vol[number][i] != 0 and type != 7 and type != 8:
                energy_type = f'Объёмный источник частиц №{number} слой №{i}'
                name = f'Volume_{number}_{i}'

                obj.insert_second_level(f'{particle}', f'{name}', {})

                obj.insert_third_level(f'{particle}', f'{name}', 'energy_type', energy_type)
                obj.insert_third_level(f'{particle}', f'{name}', 'name', name)
                obj.insert_third_level(f'{particle}', f'{name}', 'spectre', None)
                obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers', None)

                if load:
                    try:
                        obj.insert_third_level(f'{particle}', f'{name}', 'spectre',
                                               self.rs_data[number][name]['spectre'])
                        obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers',
                                               self.rs_data[number][name]['spectre number'])
                    except:
                        print(f'Загрузка данных в {particle} {name} произошла с ошибкой или нет данных в remp sources')
                        obj.insert_third_level(particle, name, 'spectre', None)
                        obj.insert_third_level(particle, name, 'spectre numbers', None)

        for i in self.PL_vol[number]:  # volume78
            if i != 0 and (type == 7 or type == 8):
                energy_type = f'Объёмный источник частиц №{number} слой №{i}'
                name = f'Volume78_{number}_{i}'

                obj.insert_second_level(f'{particle}', f'{name}', {})

                obj.insert_third_level(f'{particle}', f'{name}', 'energy_type', energy_type)
                obj.insert_third_level(f'{particle}', f'{name}', 'name', name)
                obj.insert_third_level(f'{particle}', f'{name}', 'spectre', None)
                obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers', None)

                if load:
                    try:
                        obj.insert_third_level(f'{particle}', f'{name}', 'spectre',
                                               self.rs_data[number][name]['spectre'])
                        obj.insert_third_level(f'{particle}', f'{name}', 'spectre numbers',
                                               self.rs_data[number][name]['spectre number'])
                    except:
                        print(f'Загрузка данных в {particle} {name} произошла с ошибкой или нет данных в remp sources')
                        obj.insert_third_level(particle, name, 'spectre', None)
                        obj.insert_third_level(particle, name, 'spectre numbers', None)

        for i in range(len(self.PL_bound[number])):
            if self.PL_bound[number][i] != 0:
                energy_type = 'Boundaries'
                name = f'{energy_type}_{number}_{boundaries_decode[i]}'

                obj.insert_second_level(f'{particle}', f'{name}', {})

                obj.insert_third_level(f'{particle}', f'{name}', 'energy_type', energy_type)
                obj.insert_third_level(f'{particle}', f'{name}', 'name', name)
                obj.insert_third_level(particle, name, 'spectre', None)
                obj.insert_third_level(particle, name, 'spectre numbers', None)

                try:
                    for j in boundaries_decode_f.items():
                        if j[0] == boundaries_decode[i]:
                            file = j[1]
                            sp_number = b_list[file]
                            break

                    obj.insert_third_level(particle, name, 'spectre', file)
                    obj.insert_third_level(particle, name, 'spectre numbers', sp_number)

                except:
                    obj.insert_third_level(particle, name, 'spectre', None)
                    obj.insert_third_level(particle, name, 'spectre numbers', None)

                if load:
                    try:
                        sp = self.rs_data[number][name]['spectre']
                        obj.insert_third_level(particle, name, 'spectre', sp)

                        sp_n = self.rs_data[number][name]['spectre number']
                        obj.insert_third_level(particle, name, 'spectre numbers', sp_n)
                    except:
                        print(f'Загрузка данных в {particle} {name} произошла с ошибкой или нет данных в remp sources')
                        obj.insert_third_level(particle, name, 'spectre', None)
                        obj.insert_third_level(particle, name, 'spectre numbers', None)

    def tree_view_constructor(self, ask_name=True, load=False, load_data=None):
        if self.path is None:
            mb.showerror('Path', 'Сначала выберите проект')
            return
        self.global_count_gsources += 1

        if ask_name:
            name = sd.askstring('Назовите воздействие', 'Введите название воздействия\nОтмена - название по умолчанию')
            if name == '':
                name = f'Воздействие {self.global_count_gsources}'
            if name is None:
                return

        else:
            name = load_data[0]

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
                            self.__tree_select_react(sv, name, _), "+")

        source = self.tree[ind].insert('', 0, text=f'{name}', open=True)

        if load is False:
            self.global_tree_db.update({name: self.tree_db_insert(name)})
            fr_data = FrameGen(fr, self.path, self.global_tree_db[name])
            fr_data.configure(text=self.global_tree_db[name].obj_name + f'  № {self.global_count_gsources}')
            fr_data._notebooks()

        elif load is True:
            self.global_tree_db.update({name: self.tree_db_insert(name)})

            for i in self.PAR.keys():
                if self.PAR[i]['number'] == load_data[1]:
                    part_name = i
                    break

            self.tree_db_insert_particle(self.global_tree_db[name], part_name, load=True)
            source_keys = self.global_tree_db[name].get_second_level_keys(part_name)
            self.particle_tree_constr(part_name, source_keys, source, ind)

            fr_data = FrameGen(fr, self.path, self.global_tree_db[name])
            fr_data.configure(text=self.global_tree_db[name].obj_name + f'  № {self.global_count_gsources}')
            if self.global_tree_db[name].get_share_data('count') is not None:
                fr_data.cell_numeric = self.global_tree_db[name].get_share_data('count')
                fr_data._notebooks()
                fr_data.load_data()

        fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='WN')
        self.main_frame_exist = True

        for index, s_type in enumerate(self.global_tree_db[name].get_first_level_keys()):
            source_keys = self.global_tree_db[name].get_second_level_keys(s_type)
            if len(source_keys) == 0:
                continue
            if any(['Energy' in s_key for s_key in source_keys]):
                lb = 'Энерговыделение'
                part = self.tree[ind].insert(source, index, text=lb, open=True)

                for i, s_key in enumerate(source_keys):
                    self.tree[ind].insert(part, i, text=f'{s_key}', open=True)

            elif any(['Current' in s_key for s_key in source_keys]):
                lb = 'Сторонний ток'
                part = self.tree[ind].insert(source, index, text=lb, open=True)

                for i, s_key in enumerate(source_keys):
                    self.tree[ind].insert(part, i, text=f'{s_key}', open=True)

        self.tree[ind].bind("<Button-3>", lambda _,
                                                 index=ind,
                                                 name=name: self.popup(name, index, _))

        self.notebook.add(fr, text=f'{name}')
        self.tabs_dict.update({name: [len(self.tabs_dict), fr]})

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
                if self.main_frame_exist is False:
                    self.__destroy_data_frame(name)
                    fr_data = FrameGen(self.tabs_dict[name][-1], self.path, self.global_tree_db[name])
                    if self.global_tree_db[name].get_share_data('count') is not None:
                        fr_data.cell_numeric = self.global_tree_db[name].get_share_data('count')
                        fr_data._notebooks()
                        fr_data.load_data()
                    else:
                        fr_data._notebooks()
                        fr_data.set_amplitude()

                    self.main_frame_exist = True
                    fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='WN')

            elif self.tree[index].item(x)['text'] in s_list:
                self.__destroy_data_frame(name)
                self.main_frame_exist = False

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

                if 'Volume' in self.tree[index].item(x)['text']:
                    self.regular_source_interface(fr_data, name, first_key, second_key)

                elif 'Volume78' in self.tree[index].item(x)['text']:
                    self.regular_source_interface(fr_data, name, first_key, second_key)

                elif 'Flu' in self.tree[index].item(x)['text']:
                    self.flu_source_interface(fr_data, name, first_key, second_key)

                elif 'Current' in self.tree[index].item(x)['text']:
                    self.current_source_interface(fr_data, name, first_key, second_key)

                elif 'Energy' in self.tree[index].item(x)['text']:
                    self.current_source_interface(fr_data, name, first_key, second_key)

                elif 'Boundaries' in self.tree[index].item(x)['text']:
                    self.boundaries_interface(fr_data, name, first_key, second_key)

                fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='NWSE')

            else:
                self.__destroy_data_frame(name)
                self.main_frame_exist = False

    def regular_source_interface(self, parent_widget, name, first_key, second_key):
        fr_data = parent_widget

        e = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'energy_type')
        energy_type_label = tk.Label(fr_data, text=e)
        energy_type_label.grid(row=0, column=0, columnspan=4, sticky='W')

        SP_number = tk.Label(fr_data, text=f'Номер спектра: Файл не выбран')
        SP_number.grid(row=1, column=0, sticky='W', columnspan=4)

        SP_path = tk.Label(fr_data, text=f'Путь к спектру: Файл не выбран            ')
        SP_path.grid(row=2, column=0, sticky='W', columnspan=4)

        choice_sp = tk.Button(fr_data, text='Выбрать файл', width=13,
                              command=lambda: self.__choice_file(SP_path, SP_number, name, first_key, second_key,
                                                                 'спектр', conf_sp))
        choice_sp.grid(row=1, column=5, sticky='E', padx=20, pady=3)

        conf_sp = tk.Button(fr_data, text='Редактировать', width=13, state='disabled',
                            command=lambda: self.__spectre_configure(SP_path, SP_number, name, first_key, second_key,
                                                                     configure=True))
        conf_sp.grid(row=2, column=5, sticky='E', padx=20, pady=3)

        create_sp = tk.Button(fr_data, text='Создать спектр', width=13,
                              command=lambda: self.__spectre_configure(SP_path, SP_number, name, first_key, second_key,
                                                                       create=True))
        create_sp.grid(row=3, column=5, sticky='E', padx=20, pady=3)

        d_text = 'Подсказка:\nВыберите один файл:\n' \
                 'тип 0, тип 1, тип 5\n' \
                 'Для типов 0, 1 и 5 доступно создание'

        description_label = tk.Label(fr_data, text=d_text, justify='left')
        description_label.grid(row=1, column=6, columnspan=3, rowspan=5, padx=10)

        try:
            if self.global_tree_db[name].get_last_level_data(first_key, second_key,
                                                             "spectre numbers") is None:
                raise Exception

            number = self.global_tree_db[name].get_last_level_data(first_key, second_key, "spectre numbers")
            sp_name = self.global_tree_db[name].get_last_level_data(first_key, second_key, "spectre")
            SP_number['text'] = f'Номер спектра: {number}'
            SP_path['text'] = f'Путь к спектру: {sp_name}'
            conf_sp['state'] = 'normal'

        except:
            pass

    def flu_source_interface(self, parent_widget, name, first_key, second_key):

        fr_data = parent_widget

        e = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'energy_type')
        en_type = tk.Label(fr_data, text=f'{e}')
        en_type.grid(row=0, column=0, columnspan=3, sticky='NW')
        spectres_label = tk.Label(fr_data)
        spectres_label.grid(row=1, column=0, columnspan=3, rowspan=15, sticky='NW')

        manual_conf_button = tk.Button(fr_data, text='Выбрать вручную', width=15,
                                       command=lambda: self.__choice_files(spectres_label, name, first_key, second_key,
                                                                           '.spc  тип(0 или 1 или 3)', one_file=False))
        manual_conf_button.grid(row=1, column=4, sticky='E', padx=10)

        auto_conf_button = tk.Button(fr_data, text='Автом. поиск', width=15,
                                     command=lambda: self.__flux_auto_search(name, first_key, second_key,
                                                                             spectres_label))
        auto_conf_button.grid(row=2, column=4, sticky='E', padx=10, pady=3)

        open_notepad = tk.Button(fr_data, text='Редактировать', width=15,
                                 command=lambda: self.__open_notepad(name, first_key, second_key, spectres_label,
                                                                     False))
        open_notepad.grid(row=3, column=4, sticky='E', padx=10, pady=3)

        d_text = 'Подсказка:\nВыберите от 1го до 6ти файлов типа 3'

        description_label = tk.Label(fr_data, text=d_text)
        description_label.grid(row=1, column=5, columnspan=3, rowspan=5, padx=10)

        spectre = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre')
        spectre_number = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre numbers')

        if (spectre is None) or (spectre_number is None):
            t = 'Опознано неправильное количество спектров.\nВыберите спектры вручную.'

        else:
            t = 'Список спектров:\n'

            for i in range(len(spectre)):
                t += '№ ' + str(spectre_number[i]) + '   ' + str(spectre[i]) + '\n'

        spectres_label['text'] = t

    def boundaries_interface(self, parent_widget, name, first_key, second_key):

        fr_data = parent_widget

        e = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'energy_type')
        en_type = tk.Label(fr_data, text=f'{e}')
        en_type.grid(row=0, column=0, columnspan=3, sticky='NW')
        spectres_label = tk.Label(fr_data)
        spectres_label.grid(row=1, column=0, columnspan=3, rowspan=8, sticky='N')

        manual_conf_button = tk.Button(fr_data, text='Выбрать вручную', width=15,
                                       command=lambda: self.__choice_files(spectres_label, name, first_key, second_key,
                                                                           'xmax_part', buttons=open_notepad))
        manual_conf_button.grid(row=1, column=4, sticky='E', padx=10)

        open_notepad = tk.Button(fr_data, text='Просмотр', width=15, state='disabled',
                                 command=lambda: self.__open_notepad(name, first_key, second_key, spectres_label, True))
        open_notepad.grid(row=2, column=4, sticky='E', padx=10, pady=3)

        d_text = 'Подсказка:\nВыберите файл (спектр) типа 4'

        description_label = tk.Label(fr_data, text=d_text)
        description_label.grid(row=1, column=5, columnspan=3, rowspan=5, padx=10)

        t = 'Список файлов:\n'

        try:
            file = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre')
            number = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre numbers')

            if (file is None) or (number is None):
                raise Exception

            t += file + '  №' + str(number) + '\n'

        except:
            t += 'Файлы не найдены, выберите вручную'

        if self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre') is not None:
            open_notepad['state'] = 'normal'

        spectres_label['text'] = t

    def current_source_interface(self, parent_widget, name, first_key, second_key):
        fr_data = parent_widget
        e = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'energy_type')
        en_type = tk.Label(fr_data, text=f'{e}')
        en_type.grid(row=0, column=0, columnspan=3)

        open_notepad = tk.Button(fr_data, text='Просмотр', width=15, state='disabled',
                                 command=lambda: self.__open_notepad_distribution(name, first_key, second_key))
        open_notepad.grid(row=2, column=4, sticky='E', padx=10, pady=3)

        disable = tk.Button(fr_data, text='Отключить', width=15, state='disabled',
                            command=lambda: self.__delete_distribution(distr_label, name, first_key,
                                                                       second_key, (open_notepad, disable)))
        disable.grid(row=3, column=4, sticky='E', padx=10, pady=3)

        d_text = 'Подсказка:\nВыберите файл типа:\n - "energy distribution" для энерговыделения (Energy)\n' \
                 ' - "JX/JY/JZ" для токов (Current)\n\n' \
                 'Отключить - отключает сохранение данного источника'

        description_label = tk.Label(fr_data, text=d_text, justify='left')
        description_label.grid(row=1, column=5, columnspan=3, rowspan=5, padx=10)

        try:
            d = self.global_tree_db[name].get_last_level_data(first_key, second_key, "distribution")
        except:
            d = ''

        distr_label = tk.Label(fr_data, text=f'Список файлов:\n  {d}')
        distr_label.grid(row=1, column=0, sticky='W', columnspan=4)
        choice_distr_button = tk.Button(fr_data, text='Выбрать файл', width=15,
                                        command=lambda: self.__choice_distribution(distr_label, name, first_key,
                                                                                   second_key, (open_notepad, disable)))
        choice_distr_button.grid(row=1, column=4, sticky='E', columnspan=1, padx=10)

        if d != '' and d is not None:
            disable['state'] = 'normal'
            open_notepad['state'] = 'normal'

    def add_part(self, index, name, id):

        a = SelectParticleDialog([i for i in self.PAR.keys()])
        self.wait_window(a)
        new_particle = a.lb_current
        if new_particle is None:
            return

        for gsource in self.global_tree_db.keys():
            for i in self.global_tree_db[gsource].get_first_level_keys():
                if new_particle == i:
                    ask = mb.askyesno('Внимание', f'Частица уже используется в "{gsource}"\n'
                                                  f'Добавить частицу {new_particle} в "{name}"?')
                    if ask is False:
                        return

        source = self.tree[index].get_children()[0]

        if new_particle not in self.global_tree_db[name].get_first_level_keys():

            self.global_tree_db[name].insert_first_level(new_particle)

            self.tree_db_insert_particle(self.global_tree_db[name], new_particle)

            source_keys = self.global_tree_db[name].get_second_level_keys(new_particle)

            self.particle_tree_constr(new_particle, source_keys, source, index)



        else:
            print('Объект уже существует')

    def popup(self, name, index, event):

        iid = self.tree[index].identify_row(event.y)
        if iid:
            first_list = []
            second_list = []
            for key in self.global_tree_db[name].get_first_level_keys():
                first_list.append(key.split()[-1])
                for item in self.global_tree_db[name].get_second_level_keys(key):
                    second_list.append(item)

            # mouse pointer over item
            self.contextMenu = tk.Menu(tearoff=0)
            if self.tree[index].item(iid)['text'] in first_list:
                self.contextMenu.add_command(label="Удалить", command=lambda: self.delete_particle(index, name, iid))
                self.tree[index].selection_set(iid)
            else:
                if self.tree[index].item(iid)['text'] == name:
                    self.contextMenu.add_command(label="Добавить частицу",
                                                 command=lambda: self.add_part(index, name, iid),
                                                 state='normal')

                self.contextMenu.add_command(label="Удалить", command=lambda: self.delete_particle(index, name, iid),
                                             state='disabled')
                self.tree[index].selection_set(iid)

            self.contextMenu.post(event.x_root, event.y_root)
        else:
            # mouse pointer not over item
            # occurs when items do not fill frame
            # no action required
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
            self.global_tree_db[name].delete_first_level(f_key)
            self.tree[index].delete(id)

        elif self.tree[index].item(id)['text'] in second_list:
            s_key = self.tree[index].item(id)['text']
            self.global_tree_db[name].delete_second_level(s_key)
            self.tree[index].delete(id)

        else:
            print('The object can not be deleted')

    def __tree_view_deconstructor(self):
        data = [i for i in self.global_tree_db.keys()]

        a = DeleteGSourceDialog(data)
        self.wait_window(a)
        delete_gsource = a.lb_current
        if delete_gsource is None:
            return

        self.notebook.forget(self.tabs_dict[delete_gsource][0])
        self.tree.pop(self.tabs_dict[delete_gsource][0])
        self.tabs_dict.pop(delete_gsource)
        self.global_tree_db.pop(delete_gsource)

    def test(self):
        add_index = self.menubar.index('Добавить воздействие')
        del_index = self.menubar.index('Удалить воздействие')

        self.menubar.entryconfigure(add_index, state='disabled')
        self.menubar.entryconfigure(del_index, state='disabled')

    def save(self):
        Save_remp(self.marple,self.global_tree_db, self.path)

    def __flux_auto_search(self, name, first_key, second_key, label):
        obj = self.global_tree_db[name]

        from_l = second_key.split('_')[-1][0]
        to_l = second_key.split('_')[-1][1]
        number = self.PAR[first_key]['number']
        spectres = DataParser(self.path + '/').get_spectre_for_flux(number, from_l, to_l)

        if len(spectres) == 6:
            obj.insert_third_level(first_key, second_key, 'spectre', [i for i in spectres.keys()])
            obj.insert_third_level(first_key, second_key, 'spectre numbers', [i for i in spectres.values()])

            spectre = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre')
            spectre_number = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre numbers')

            t = 'Список спектров:\n'

            for i in range(len(spectre)):
                t += '№ ' + str(spectre_number[i]) + '   ' + str(spectre[i]) + '\n'

        else:
            t = 'Опознано неправильное количество спектров.\nВоспользуйтесь ручным выбором'

        label['text'] = t

    def __add_source_button(self):
        if len(self.global_tree_db) >= len(self.PAR):
            ask = mb.askyesno('Внимание', 'Количество частиц больше количества воздействий.\nСоздать новую чатицу?')
            if ask is False:
                return
        self.tree_view_constructor()

    def __destroy_data_frame(self, name):
        if len(self.tabs_dict[name][-1].winfo_children()) < 2:
            return
        d_frame = self.tabs_dict[name][-1].winfo_children()[-1]
        d_frame.grid_forget()
        d_frame.destroy()

    def __create_data_frame(self, name):
        fr_data = ttk.Frame(self.tabs_dict[name][-1])
        fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='WN')

        return fr_data

    def __create_timefunc_constructor(self):

        self.spectre_number_data, self.spectre_path = SpectreConfigure().open_spectre(False)
        # print(self.spectre_number_data)

    def __spectre_configure(self, name_label, num_label, name, first_key, second_key, create=False, configure=False):

        if configure:
            sp_path = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre')
            sp_path = os.path.join(self.path, sp_path)
            ex = SpectreConfigure(self.path, self.parent)

            ex.button_open_spectre['state'] = 'disabled'
            ex.button_create_spectre['state'] = 'disabled'
            ex.open_spectre(use_chose_spectre=sp_path, use_constructor=True)

            try:
                self.wait_window(ex)
            except:
                pass

            file_name, number, sp_type = self.__read_spectre(sp_path)
            if file_name is None:
                return

            name_label['text'] = f'Путь к файлу:  {file_name}'
            num_label['text'] = f'Номер спектра:  {number}'

        if create:
            ex = SpectreConfigure(self.path, self.parent)

            self.wait_window(ex)

            file_name, number, sp_type = self.__read_spectre(ex.spectre_path)
            if file_name is None:
                return

            name_label['text'] = f'Путь к файлу:  {file_name}'
            num_label['text'] = f'Номер спектра:  {number}'

    def __choice_distribution(self, label, name, first_key, second_key, buttons):
        distribution_file = fd.askopenfilename(title=f'Выберите файл distribution для {second_key}',
                                               initialdir=self.path,
                                               filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))

        if distribution_file == '':
            return

        distribution_file = self.__copy_to_project(distribution_file)

        t = os.path.basename(distribution_file)
        label['text'] = f'Список файлов:\n  {t}'

        self.global_tree_db[name].insert_third_level(first_key, second_key, 'distribution', t)

        buttons[0]['state'] = 'normal'
        buttons[1]['state'] = 'normal'

    def __delete_distribution(self, label, name, first_key, second_key, buttons):

        label['text'] = f'Список файлов:\n  {None}'

        self.global_tree_db[name].insert_third_level(first_key, second_key, 'distribution', None)

        buttons[0]['state'] = 'disabled'
        buttons[1]['state'] = 'disabled'

    def __choice_files(self, label, name, first_key, second_key, format, one_file=True, buttons=None):

        if one_file:
            file = fd.askopenfilename(title=f'Выберите файлы формата {format}', initialdir=self.path)

            if file == '':
                return

            file_name, number, sp_type = self.__read_spectre(file)
            if file_name is None:
                t = 'Тип файла не распознан, добавление невозможно'
                label['text'] = t
                self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre', None)
                self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre numbers', None)
                return

            number = str(number)
            t = '№ ' + str(number) + '   ' + file_name + '\n'

        else:

            files = fd.askopenfilenames(title=f'Выберите файлы формата {format}', initialdir=self.path)

            if files == '':
                return

            file_name, number, sp_type = [], [], []
            for i in files:
                a, b, c = self.__read_spectre(i)
                if a is None:
                    t = 'Тип файла не распознан, добавление невозможно'
                    label['text'] = t
                    self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre', None)
                    self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre numbers', None)

                    return

                file_name.append(a)
                number.append(str(b))
                sp_type.append(c)

                t = ''
                for i in range(len(number)):
                    t += '№ ' + str(number[i]) + '   ' + file_name[i] + '\n'

        self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre', file_name)
        self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre numbers', number)

        label['text'] = 'Список файлов:\n' + t

        if buttons is not None:
            buttons['state'] = 'normal'

    def __choice_file(self, name_label, num_label, name, first_key, second_key, format, buttons):

        file = fd.askopenfilename(title=f'Выберите файлы формата {format}', initialdir=self.path)

        if file == '':
            name_label['text'] = 'Файл не опознан. Выберите файл правильного формата.'
            return

        file_name, number, sp_type = self.__read_spectre(file)
        if file_name is None:
            return

        self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre', file_name)
        self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre numbers', number)

        name_label['text'] = f'Путь к файлу:  {file_name}'
        num_label['text'] = f'Номер спектра:  {number}'

        buttons['state'] = 'normal'

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

    def __open_notepad(self, name, first_key, second_key, label, one_file):
        d = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre')
        if d is None:
            return

        if one_file is False:

            a = SelectSpectreToView(d)

            self.wait_window(a)

            choice = a.lb_current
            if choice is None:
                return

        elif one_file is True:
            choice = d

        f = os.path.join(self.path, choice)
        osCommandString = f"notepad.exe {f}"
        os.system(osCommandString)

        files = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'spectre')

        if type(files) is list:
            files = [os.path.join(self.path, i) for i in files]

            file_name, number, sp_type = [], [], []
            for i in files:
                a, b, c = self.__read_spectre(i)
                if a is None:
                    return

                file_name.append(a)
                number.append(str(b))
                sp_type.append(c)

            t = ''
            for i in range(len(number)):
                t += '№ ' + str(number[i]) + '   ' + file_name[i] + '\n'

        else:
            file = os.path.join(self.path, files)
            file_name, number, sp_type = self.__read_spectre(file)
            if file_name is None:
                return

            t = '№ ' + str(number) + '   ' + file_name + '\n'

        self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre', file_name)
        self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre numbers', number)

        label['text'] = 'Список файлов:\n' + t

    def __open_notepad_distribution(self, name, first_key, second_key):

        choice = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'distribution')

        f = os.path.join(self.path, choice)
        osCommandString = f"notepad.exe {f}"
        os.system(osCommandString)

    def __read_spectre(self, target):

        if not os.path.exists(target):
            print('Выбранный файл не существует')
            return None, None, None

        target = self.__copy_to_project(target)
        file_name = os.path.split(target)[-1]

        try:
            with open(os.path.join(self.path, file_name), 'r') as file:
                for j, line in enumerate(file):
                    if j == 2:
                        number = int(line.strip())
                    if j == 6:
                        type = int(line.strip())
                        break

                if len(file.readlines()) < 2:
                    raise Exception

        except:
            print('Ошибка чтения выбранных файлов')
            return None, None, None

        return file_name, number, type

    def __add_marple(self):
        ex = MarpleInterface(self.path)
        self.wait_window(ex)

        ion = ex.ion_path
        sigma = ex.sigma_path

        if ion is None or sigma is None:
            return

        self.marple_menu.entryconfigure(0, state='disabled')
        self.marple_menu.entryconfigure(1, state='normal')

        self.marple = {'ion': ion, 'sigma': sigma}
        mb.showinfo('Marple', 'Marple будет сохранён в remp source')

    def __delete_marple(self):
        self.marple_menu.entryconfigure(0, state='normal')
        self.marple_menu.entryconfigure(1, state='disabled')

        mb.showinfo('Marple', 'Marple не будет сохранён в remp source')

        self.marple = None
