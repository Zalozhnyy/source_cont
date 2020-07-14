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

from utility import *
from Project_reader import DataParcer
from Save_for_remp import Save_remp
from Main_frame import FrameGen
from SpectreConfigure import SpectreConfigure
from Dialogs import SelectParticleDialog, DeleteGSourceDialog


# TODO Правка метода current source interface

class TreeDataStructure:
    def __init__(self, part_list, obj_name):
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


class Exampleframe(ttk.LabelFrame):
    def __init__(self, parent, text):
        super().__init__(parent)

        self.configure(text=text)

        tk.Label(self, text=text).grid()


class MainWindow(tk.Frame):
    def __init__(self, parent, path=None, projectfilename=None):
        super().__init__(parent)
        self.parent = parent

        self.notebook = None
        self.tabs_dict = {}
        self.tree = []
        self.global_tree_db = {}

        self.toolbar()

        self.global_count_gsources = 0

        self.main_frame_exist = False

        try:
            if projectfilename is not None:
                if os.path.exists(projectfilename):
                    self.path = os.path.dirname(projectfilename)
                    self.check_project()
            else:
                raise Exception
        except Exception:
            self.path = path

    def from_project_reader(self):

        self.tok_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('TOK')))
        self.pl_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PL')))
        self.lay_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('LAY')))
        self.par_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PAR')))

        self.TOK = DataParcer(self.tok_dir).tok_decoder()
        self.PL = DataParcer(self.pl_dir).pl_decoder()
        self.LAY = DataParcer(self.lay_dir).lay_decoder()
        self.PAR = DataParcer(self.par_dir).par_decoder()

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
        self.filemenu.add_command(label="Сохранение для РЭМП", command=self.save)

        self.filemenu.add_command(label="Открыть папку с проектом", command=self.open_folder)
        # self.filemenu.add_command(label="Очистить папку time functions", command=lambda: tf_global_del(self.path))
        # self.filemenu.add_command(label='Перезагрузка', command=self.reset)
        self.filemenu.add_command(label="Exit", command=self.onExit)

        self.menubar.add_command(label='Добавить воздействие',
                                 command=lambda: self.tree_view_constructor(empty=True), state='disabled')
        self.menubar.add_command(label='Удалить воздействие', command=self.__tree_view_deconstructor, state='disabled')
        self.menubar.add_command(label='Справка')
        self.menubar.add_command(label='test', command=self.test)

    def onExit(self):
        self.parent.quit()
        self.parent.destroy()

    def browse_from_recent(self, path):
        self.path = path
        self.check_project()

    def browse_folder(self):
        self.path = fd.askdirectory(title='Укажите путь к проекту REMP', initialdir=f'{os.getcwd()}/entry_data')
        if self.path == '' or self.path is None:
            return None

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
        prj_name = []
        path = self.path
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
        set_recent_projects(self.path, get_recent_projects())

        # self.folder_creator()  # создаём папку time functions
        # self.initial()

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid(sticky='NWSE')

        self.from_project_reader()
        self.lag = DataParcer(self.path).pech_check()

        if 'remp_sources' in os.listdir(self.path):
            self.rs_data = DataParcer(os.path.join(self.path, 'remp_sources')).remp_source_decoder()
            ind_part_list = [i for i in self.rs_data.keys()]
            ind_part_list = sorted(ind_part_list)
            part_list = [self.PAR[2][self.PAR[1].index(i)] for i in ind_part_list]

            for gsource in part_list:
                self.tree_view_constructor(gsource_name=gsource, ask_name=False, initial=True, rs=True)
            return

        for gsource in self.PAR[2]:
            self.tree_view_constructor(gsource_name=gsource, ask_name=False, initial=True)

    def reset(self):
        if self.path is None:
            return
        self.notebook.destroy()
        self.notebook = None
        self.tabs_dict = {}
        self.tree = []
        self.global_tree_db = {}


    def open_folder(self):
        if self.path is None:
            return
        os.startfile(self.path)

    def tree_db_insert(self, part_list, obj_name, par_empty=False):
        # !!!!!!difference add in method add_part_insert_db!!!!!!!
        obj = TreeDataStructure(part_list, obj_name)

        obj.insert_share_data('lag', self.lag)

        create_list = ['x', 'y', 'z']
        distr_list = DataParcer(self.path + '/').distribution_reader()

        for i in range(self.LAY.shape[0]):
            if self.LAY[i, 1] == 1:
                energy_type = 'Current'
                for axis in create_list:
                    name = f'{energy_type}_{axis}_layer_{i}'
                    d = f'J{axis.upper()}_{i}'
                    obj.insert_second_level('Current', f'{name}', {})

                    obj.insert_third_level('Current', f'{name}', 'name', name)
                    obj.insert_third_level('Current', f'{name}', 'energy_type', energy_type)
                    # obj.insert_third_level('Current', f'{name}', 'spectre', None)
                    # obj.insert_third_level('Current', f'{name}', 'spectre numbers', None)
                    # obj.insert_third_level('Current', f'{name}', 'distribution', distr_list[distr_list.index(d)])
                    obj.insert_third_level('Current', f'{name}', 'distribution', None)

            if self.LAY[i, 2] == 1:
                energy_type = 'Sigma'
                name = f'{energy_type}_layer_{i}'
                obj.insert_second_level('Sigma', f'{name}', {})

                obj.insert_third_level('Sigma', f'{name}', 'name', name)
                obj.insert_third_level('Sigma', f'{name}', 'energy_type', energy_type)

        if self.TOK[2] == 1:
            index = self.PAR[2].index(part_list[0])
            number = self.PAR[1][index]

            energy_type = f'Gursa'
            name = f'Gursa_{number}'

            obj.insert_second_level(f'{part_list[0]}', f'{name}', {})

            obj.insert_third_level(f'{part_list[0]}', f'{name}', 'energy_type', energy_type)
            obj.insert_third_level(f'{part_list[0]}', f'{name}', 'name', name)
            obj.insert_third_level(f'{part_list[0]}', f'{name}', 'spectre', None)
            obj.insert_third_level(f'{part_list[0]}', f'{name}', 'spectre numbers', None)

        if par_empty is False:
            index = self.PAR[2].index(part_list[0])
            number = self.PAR[1][index]
            ar = self.PL.get(number)
            for i in range(ar.shape[0]):
                for j in range(1, ar.shape[1]):
                    if ar[i, j] == 1:
                        energy_type = f'Источник частиц №{number} из {j}-го слоя в {i}-й'
                        name = f'Flu_e_{number}_{j}{i}'

                        obj.insert_second_level(f'{part_list[0]}', f'{name}', {})

                        obj.insert_third_level(f'{part_list[0]}', f'{name}', 'energy_type', energy_type)
                        obj.insert_third_level(f'{part_list[0]}', f'{name}', 'name', name)
                        obj.insert_third_level(f'{part_list[0]}', f'{name}', 'spectre', None)

                        from_l = name.split('_')[-1][0]
                        to_l = name.split('_')[-1][1]
                        spectres = DataParcer(self.path + '/').get_spectre_for_flux(number, from_l, to_l)
                        obj.insert_third_level(part_list[0], name, 'spectre',
                                               [i for i in spectres.keys()])
                        obj.insert_third_level(part_list[0], name, 'spectre numbers',
                                               [i for i in spectres.values()])

        obj.insert_share_data('influence_number', f'{self.global_count_gsources}')

        print(obj.get_first_level_keys())

        return obj

    def tree_db_load_from_rs(self, part_list, obj_name, ):
        obj = TreeDataStructure(part_list, obj_name)

        index = self.PAR[2].index(part_list[0])
        number = self.PAR[1][index]
        for i in self.rs_data[number].keys():
            obj.insert_share_data('count', self.rs_data[number][i]['count'])
            time = self.rs_data[number][i]['time']
            obj.insert_share_data('time', time)
            func = self.rs_data[number][i]['func']
            obj.insert_share_data('func', func)
            obj.insert_share_data('amplitude',
                                  self.rs_data[number][i]['amplitude'] * integrate.trapz(x=np.array(time, dtype=float),
                                                                                         y=np.array(func, dtype=float)))
        obj.insert_share_data('lag', self.lag)

        create_list = ['x', 'y', 'z']

        for i in range(self.LAY.shape[0]):
            if self.LAY[i, 1] == 1:
                energy_type = 'Current'
                for axis in create_list:
                    name = f'{energy_type}_{axis}_layer_{i}'
                    obj.insert_second_level('Current', f'{name}', {})

                    obj.insert_third_level('Current', f'{name}', 'name', name)
                    obj.insert_third_level('Current', f'{name}', 'energy_type', energy_type)

                    try:
                        obj.insert_third_level('Current', f'{name}', 'distribution', self.rs_data[number][name]['distribution'])
                    except:
                        obj.insert_third_level('Current', f'{name}', 'distribution', None)

                    # obj.insert_third_level('Current', f'{name}', 'spectre', None)
                    # obj.insert_third_level('Current', f'{name}', 'spectre numbers', None)

            if self.LAY[i, 2] == 1:
                energy_type = 'Sigma'
                name = f'{energy_type}_layer_{i}'
                obj.insert_second_level('Sigma', f'{name}', {})

                obj.insert_third_level('Sigma', f'{name}', 'name', name)
                obj.insert_third_level('Sigma', f'{name}', 'energy_type', energy_type)

        if self.TOK[2] == 1:
            index = self.PAR[2].index(part_list[0])
            number = self.PAR[1][index]

            energy_type = f'Gursa'
            name = f'Gursa_{number}'

            obj.insert_second_level(f'{part_list[0]}', f'{name}', {})

            obj.insert_third_level(f'{part_list[0]}', f'{name}', 'energy_type', energy_type)
            obj.insert_third_level(f'{part_list[0]}', f'{name}', 'name', name)
            obj.insert_third_level(f'{part_list[0]}', f'{name}', 'spectre', self.rs_data[number][name]['spectre'])
            obj.insert_third_level(f'{part_list[0]}', f'{name}', 'spectre numbers',
                                   self.rs_data[number][name]['spectre number'])

        index = self.PAR[2].index(part_list[0])
        number = self.PAR[1][index]
        ar = self.PL.get(number)
        for i in range(ar.shape[0]):
            for j in range(1, ar.shape[1]):
                if ar[i, j] == 1:
                    energy_type = f'Источник частиц №{number} из {j}-го слоя в {i}-й'
                    name = f'Flu_e_{number}_{j}{i}'

                    obj.insert_second_level(f'{part_list[0]}', f'{name}', {})

                    obj.insert_third_level(f'{part_list[0]}', f'{name}', 'energy_type', energy_type)
                    obj.insert_third_level(f'{part_list[0]}', f'{name}', 'name', name)
                    obj.insert_third_level(f'{part_list[0]}', f'{name}', 'spectre', None)

                    from_l = name.split('_')[-1][0]
                    to_l = name.split('_')[-1][1]
                    spectres = DataParcer(self.path + '/').get_spectre_for_flux(number, from_l, to_l)
                    obj.insert_third_level(part_list[0], name, 'spectre',
                                           [i for i in spectres.keys()])
                    obj.insert_third_level(part_list[0], name, 'spectre numbers',
                                           [i for i in spectres.values()])

        obj.insert_share_data('influence_number', f'{self.global_count_gsources}')

        print(obj.get_first_level_keys())

        return obj

    # def initial(self):
    #     try:
    #         self.notebook.destroy()
    #     except:
    #         pass
    #
    #     self.clear_global_dicts()
    #
    #     self.notebook = ttk.Notebook(self.parent)
    #     self.notebook.grid()
    #
    #     tok_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('TOK')))
    #     pl_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PL')))
    #     lay_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('LAY')))
    #     par_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PAR')))
    #
    #     TOK = DataParcer(tok_dir).tok_decoder()
    #     PL = DataParcer(pl_dir).pl_decoder()
    #     LAY = DataParcer(lay_dir).lay_decoder()
    #     PAR = DataParcer(par_dir).par_decoder()
    #
    #     if np.any(LAY[:, 1:] == 1):
    #         # Класс рассчте Current,Sigma
    #         u_tab = UnitedLayers(parent=self.parent, path=self.path, name='Current and Sigma',
    #                              energy_type='Current and Sigma')
    #
    #         u_tab.lay_dir = lay_dir
    #         u_tab.pl_dir = pl_dir
    #
    #         self.notebook.add(u_tab, text=f"Current and Sigma")
    #         u_tab.notebooks()
    #
    #     for key in PL.keys():
    #         ar = PL.get(key)
    #         for i in range(ar.shape[0]):
    #             for j in range(1, ar.shape[1]):
    #                 if ar[i, j] == 1:
    #                     energy_type = f'Источник электронов №{key} из {j}го в {i}й'
    #                     name = f'Flu_e_{key}_{j}{i}'
    #                     tab = FluTab(self.parent, self.path, name, f'{energy_type}')
    #                     self.notebook.add(tab, text=f"{tab.name}")
    #                     tab.notebooks()
    #
    #         # if ar[:, 0].any() == 1:
    #         #     mb.showinfo('ERROR', 'Частицы в нулевом слое!')
    #
    #     # if TOK[0] == 1:
    #     #     energy_type = 'Начальное поле'
    #     #     tab = InitialField(self.parent, self.path, 'Initial_field', f'{energy_type}')
    #     #     self.notebook.add(tab, text=f"{tab.name}")
    #     #     tab.notebooks()
    #     #
    #     # if TOK[1] == 1:
    #     #     energy_type = 'Внешнее поле'
    #     #
    #     #     tab = ExternalField(self.parent, self.path, 'External_field', f'{energy_type}')
    #     #     self.notebook.add(tab, text=f"{tab.name}")
    #     #     tab.notebooks()
    #
    #     if TOK[2] == 1:
    #         part_count = PAR[0]
    #         part_numbers = PAR[1]
    #         part_num_name = PAR[2]
    #
    #         for i in range(part_count):
    #             energy_type = part_num_name[i]
    #             tab = Gursa(self.parent, self.path, f'Gursa_{part_num_name[i].split()[-1]}', energy_type)
    #             self.notebook.add(tab, text=f"{tab.name}")
    #             tab.notebooks()
    #
    #     if TOK[2] == 0:
    #         energy_type = 'Koshi'
    #
    #         tab = Koshi(self.parent, self.path, 'PECHS', f'{energy_type}')
    #         self.notebook.add(tab, text=f"{tab.name}")
    #         tab.koshi_nb()
    #
    #     plane_check = False  # затычка перед нормальной проверкой на наличие в проекте
    #     if plane_check is True:
    #         tab = PlaneWave(self.parent, self.path, 'PlaneWave', 'Плоская волна')
    #         self.notebook.add(tab, text=f"{tab.name}")
    #         tab.notebooks()

    def tree_view_constructor(self, gsource_name=None, ask_name=True, initial=False, empty=False, rs=False):
        if self.path is None:
            mb.showerror('Path', 'Сначала выберите проект')
            return
        self.global_count_gsources += 1

        if ask_name:
            name = sd.askstring('Назовите воздействие', 'Введите название поздействия\nОтмена - название по умолчанию')
            if name == '' or name is None:
                name = f'Воздействие {self.global_count_gsources}'

        if initial:
            name = f'Воздействие №{self.global_count_gsources} "{gsource_name}"'

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

        if empty is True:
            self.global_tree_db.update({name: self.tree_db_insert([], name, par_empty=True)})
            fr_data = FrameGen(fr, self.path, self.global_tree_db[name])
            fr_data._notebooks()

        elif rs is True:
            self.global_tree_db.update({name: self.tree_db_load_from_rs([gsource_name], name)})
            fr_data = FrameGen(fr, self.path, self.global_tree_db[name])
            fr_data.cell_numeric = self.global_tree_db[name].get_share_data('count')
            fr_data._notebooks()
            fr_data.load_data()

        else:
            self.global_tree_db.update({name: self.tree_db_insert([gsource_name], name)})
            fr_data = FrameGen(fr, self.path, self.global_tree_db[name])
            fr_data._notebooks()
        fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='WN')
        self.main_frame_exist = True

        for index, s_type in enumerate(self.global_tree_db[name].get_first_level_keys()):
            if s_type == 'Sigma':
                lb = 'Энерговыделение'
                part = self.tree[ind].insert(source, index, text=lb, open=True)

                source_keys = self.global_tree_db[name].get_second_level_keys(s_type)
                for i, s_key in enumerate(source_keys):
                    self.tree[ind].insert(part, i, text=f'{s_key}', open=True)

            elif s_type == 'Current':
                lb = 'Сторонний ток'
                part = self.tree[ind].insert(source, index, text=lb, open=True)

                source_keys = self.global_tree_db[name].get_second_level_keys(s_type)
                for i, s_key in enumerate(source_keys):
                    self.tree[ind].insert(part, i, text=f'{s_key}', open=True)

            else:
                lb = s_type.split()[-1]
                part = self.tree[ind].insert(source, index, text=lb, open=True)
                boundary_source = self.tree[ind].insert(part, 0, text='С границ', open=True)
                surface_source = self.tree[ind].insert(part, 1, text='Поверхностные', open=True)
                volume_source = self.tree[ind].insert(part, 2, text='Объёмные', open=True)

                source_keys = self.global_tree_db[name].get_second_level_keys(s_type)
                for i, s_key in enumerate(source_keys):
                    if 'Flu' in s_key:
                        self.tree[ind].insert(surface_source, i, text=f'{s_key}', open=True)

                    elif 'Gursa' in s_key:
                        self.tree[ind].insert(volume_source, i, text=f'{s_key}', open=True)

        self.tree[ind].bind("<Button-3>", lambda _,
                                                 index=ind,
                                                 name=name: self.popup(name, index, _))

        self.notebook.add(fr, text=f'{name}')
        self.tabs_dict.update({name: [len(self.tabs_dict), fr]})

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

                if 'Gursa' in self.tree[index].item(x)['text']:
                    self.regular_source_interface(fr_data, name, first_key, second_key)

                elif 'Flu' in self.tree[index].item(x)['text']:
                    self.flu_source_interface(fr_data, name, first_key, second_key)

                elif 'Current' in self.tree[index].item(x)['text']:
                    self.current_source_interface(fr_data, name, first_key, second_key)

                fr_data.grid(row=0, column=10, rowspan=100, columnspan=50, sticky='WN')

            else:
                self.__destroy_data_frame(name)
                self.main_frame_exist = False

    def regular_source_interface(self, parent_widget, name, first_key, second_key):
        fr_data = parent_widget
        e = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'energy_type')
        energy_type_label = tk.Label(fr_data, text=e)
        energy_type_label.grid(row=0, column=0, columnspan=4, sticky='W')
        self.SP_number = tk.Label(fr_data, text=f'Номер спектра: Файл не выбран')
        self.SP_number.grid(row=1, column=0, sticky='W', columnspan=4)
        self.SP_path = tk.Label(fr_data, text=f'Путь к спектру: Файл не выбран            ')
        self.SP_path.grid(row=2, column=0, sticky='W', columnspan=4)

        choice_sp = tk.Button(fr_data, text='Выбрать файл', width=13,
                              command=lambda: self.__choice_spectre(name, first_key, second_key))
        choice_sp.grid(row=1, column=5, sticky='E',padx=20)
        self.conf_sp = tk.Button(fr_data, text='Редактировать', width=13, state='disabled',
                                 command=lambda: self.__start_spectre_configure(name,
                                                                                first_key,
                                                                                second_key,
                                                                                self.spectre_path))
        self.conf_sp.grid(row=2, column=5, sticky='E',padx=20)
        create_sp = tk.Button(fr_data, text='Создать спектр', width=13,
                              command=lambda: self.__start_spectre_configure(name,
                                                                             first_key,
                                                                             second_key,
                                                                             create=True))
        create_sp.grid(row=3, column=5, sticky='E',padx=20)

        try:
            if self.global_tree_db[name].get_last_level_data(first_key, second_key,
                                                             "spectre numbers") is None:
                raise Exception
            self.SP_number['text'] = f'Номер спектра: ' \
                                     f'{self.global_tree_db[name].get_last_level_data(first_key, second_key, "spectre numbers")}'
            self.SP_path['text'] = f'Путь к спектру: ' \
                                   f'{self.global_tree_db[name].get_last_level_data(first_key, second_key, "spectre")}'
            self.conf_sp['state'] = 'normal'
            self.spectre_path = os.path.join(self.path,
                                             self.SP_path['text'].split("Путь к спектру: ")[-1])

        except:
            pass

    def flu_source_interface(self, parent_widget, name, first_key, second_key):
        iind = self.PAR[1][self.PAR[2].index(first_key)]
        from_l = second_key.split('_')[-1][0]
        to_l = second_key.split('_')[-1][1]
        spectres = DataParcer(self.path + '/').get_spectre_for_flux(iind, from_l, to_l)

        fr_data = parent_widget

        e = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'energy_type')
        en_type = tk.Label(fr_data, text=f'{e}')
        en_type.grid(row=0, column=0, columnspan=3, sticky='NW')
        spectres_label = tk.Label(fr_data)
        spectres_label.grid(row=1, column=0, columnspan=3, rowspan=8, sticky='NW')

        if len(spectres) != 6:
            print('Опознано неправильное количество спектров.\nПроверьте наличие файлов .spc в проекте')
            if len(spectres) < 6:
                t = 'Проверьте файлы .spc в проекте\nНайдено менее 6 спектров'
            if len(spectres) > 6:
                t = 'Проверьте файлы .spc в проекте\nНайдено более 6 спектров'

        elif len(spectres) == 6:
            t = 'Список спектров:\n'

            for i in spectres.keys():
                t += '№ ' + spectres[i] + '   ' + i + '\n'
            self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre',
                                                         [i for i in spectres.keys()])
            self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre numbers',
                                                         [i for i in spectres.values()])

        spectres_label['text'] = t

    def current_source_interface(self, parent_widget, name, first_key, second_key):
        fr_data = parent_widget
        e = self.global_tree_db[name].get_last_level_data(first_key, second_key, 'energy_type')
        en_type = tk.Label(fr_data, text=f'{e}')
        en_type.grid(row=0, column=0, columnspan=3)

        try:
            d = self.global_tree_db[name].get_last_level_data(first_key, second_key, "distribution")
        except:
            d = ''

        distr_label = tk.Label(fr_data, text=f'Distribution:  {d}')
        distr_label.grid(row=1, column=0, sticky='W', columnspan=4)
        choice_distr_button = tk.Button(fr_data, text='Выбрать файл',
                                        command=lambda: self.__choice_distribution(distr_label, name, first_key,
                                                                                   second_key))
        choice_distr_button.grid(row=1, column=4, sticky='W', columnspan=1, padx=20)

    def add_part(self, index, name, id):

        a = SelectParticleDialog(self.PAR[2])
        self.wait_window(a)
        new_particle = a.lb_current
        source = self.tree[index].get_children()[0]

        if new_particle not in self.global_tree_db[name].get_first_level_keys():
            #     for i in self.PAR[2]:
            #         if new_particle in i:
            #             name_for_db = i
            #             break

            self.add_part_insert_db(index, name, new_particle)

            print(self.global_tree_db[name].get_first_level_keys())

            lb = new_particle.split()[-1]
            part = self.tree[index].insert(source, index, text=lb, open=True)
            boundary_source = self.tree[index].insert(part, 0, text='С границ', open=True)
            surface_source = self.tree[index].insert(part, 1, text='Поверхностные', open=True)
            volume_source = self.tree[index].insert(part, 2, text='Объёмные', open=True)

            source_keys = self.global_tree_db[name].get_second_level_keys(new_particle)
            print(source_keys)
            for i, s_key in enumerate(source_keys):
                self.tree[index].insert(surface_source, i, text=f'{s_key}', open=True)

        else:
            print('Объект уже существует')

    def add_part_insert_db(self, index, name, name_for_db):
        self.global_tree_db[name].insert_first_level(name_for_db)
        number = self.PAR[1][self.PAR[2].index(name_for_db)]
        obj = self.global_tree_db[name]
        ar = self.PL.get(number)
        for i in range(ar.shape[0]):
            for j in range(1, ar.shape[1]):
                if ar[i, j] == 1:
                    energy_type = f'Источник электронов №{number} из {j}го в {i}й'
                    name = f'Flu_e_{number}_{j}{i}'

                    obj.insert_second_level(name_for_db, f'{name}', {})

                    obj.insert_third_level(name_for_db, f'{name}', 'energy_type', energy_type)
                    obj.insert_third_level(name_for_db, f'{name}', 'name', name)
                    obj.insert_third_level(f'{name_for_db}', f'{name}', 'spectre', 'не выбран')

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
        print('ПОСЛЕ УДАЛЕНИЯ')
        print(self.global_tree_db[name].get_first_level_keys())

    def pl_tree_insert(self, source, number):
        pl_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PL')))
        PL = DataParcer(pl_dir).pl_decoder()

        ar = PL.get(number)
        for i in range(ar.shape[0]):
            for j in range(1, ar.shape[1]):
                if ar[i, j] == 1:
                    energy_type = f'Источник электронов №{number} из {j}го в {i}й'
                    name = f'Flu_e_{number}_{j}{i}'

                    self.tree[-1].insert(source, i, text=name)

    def lay_tree_insert(self, source):
        lay_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('LAY')))
        LAY = DataParcer(lay_dir).lay_decoder()

        for i in range(LAY.shape[0]):
            if LAY[i, 1] == 1:
                energy_type = 'Current'
                name = f'{energy_type}_layer_{i}'
                self.tree[-1].insert(source[0], i, text=name)

            if LAY[i, 2] == 1:
                energy_type = 'Sigma'
                name = f'{energy_type}_layer_{i}'
                self.tree[-1].insert(source[1], i, text=name)

    def __tree_view_deconstructor(self):
        data = [i for i in self.global_tree_db.keys()]

        a = DeleteGSourceDialog(data)
        self.wait_window(a)
        delete_gsource = a.lb_current

        self.notebook.forget(self.tabs_dict[delete_gsource][0])
        self.tree.pop(self.tabs_dict[delete_gsource][0])
        self.tabs_dict.pop(delete_gsource)
        self.global_tree_db.pop(delete_gsource)

    def test(self):
        self.__copy_to_project(None)

    def save(self):
        Save_remp(self.global_tree_db, self.path)

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
        print(self.spectre_number_data)

    def __start_spectre_configure(self, name, first_key, second_key, sp_path=None, create=False):
        ex = SpectreConfigure(self.path, self.parent)
        ex.constructor()
        ex.focus_set()

        if create is False:  # start as configure
            ex.open_spectre(True, sp_path)
            ex.button_create_spectre['state'] = 'disabled'
            ex.button_open_spectre['state'] = 'disabled'
            ex.spetre_type_cobbobox['state'] = 'disabled'

        self.wait_window(ex)

        try:
            self.SP_number['text'] = f'Номер спектра: {ex.spectre_number_val.get()}'
            self.SP_path['text'] = f'Путь к спектру: {os.path.split(ex.spectre_path)[-1]}'
            self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre',
                                                         os.path.split(ex.spectre_path)[-1])
            self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre numbers',
                                                         ex.spectre_number_val.get())

            self.conf_sp['state'] = 'normal'
        except:
            print('Ошибка в переотриcовке номера спектра')

    def __choice_spectre(self, name, first_key, second_key):

        self.spectre_path = fd.askopenfilename(title='Выберите файл spectre',
                                               filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
        if self.spectre_path == '':
            return
        self.__copy_to_project(self.spectre_path)

        with open(self.spectre_path, 'r') as file:
            lines = file.readlines()

        self.conf_sp['state'] = 'normal'

        self.SP_number['text'] = f'Номер спектра: {lines[2].strip()}'
        self.SP_path['text'] = f'Путь к спектру: {os.path.split(self.spectre_path)[-1]}'
        self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre',
                                                     os.path.split(self.spectre_path)[-1])
        self.global_tree_db[name].insert_third_level(first_key, second_key, 'spectre numbers',
                                                     lines[2].strip())

    def __choice_distribution(self, label, name, first_key, second_key):
        distribution_file = fd.askopenfilename(title=f'Выберите файл distribution для {second_key}',
                                               filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))

        if distribution_file == '':
            return

        t = os.path.split(distribution_file)[-1]
        label['text'] = f'Distribution:  {t}'

        self.global_tree_db[name].insert_third_level(first_key, second_key, 'distribution', t)

    def __copy_to_project(self, target):
        t = target
        if os.path.normpath(self.path) in os.path.normpath(t):
            return
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
