import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import numpy as np
import os
import locale

from utility import *
from United_Layers import UnitedLayers
from Project_reader import DataParcer
from Gursa import Gursa
from TOK import InitialField, ExternalField, Koshi
from Flu import FluTab
from plane_wave import PlaneWave
from Save_for_remp import Save_remp


class MainWindow(tk.Frame):
    def __init__(self, parent, path=None):
        tk.Frame.__init__(self)
        self.parent = parent
        self.path = path

        self.notebook = None

        self.toolbar()

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
        self.filemenu.add_command(label="Сохранение для РЭМП", command=self.remp_save)

        self.filemenu.add_command(label="Открыть папку с проектом", command=self.open_folder)
        # self.filemenu.add_command(label="Очистить папку time functions", command=lambda: tf_global_del(self.path))
        self.filemenu.add_command(label='Перезагрузка', command=self.reset)
        self.filemenu.add_command(label="Exit", command=self.onExit)

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

        self.file_dict = self.check_folder()
        if self.file_dict is None:
            mb.showerror('Project error', f'Файл .PRJ  не найден. Указана неправильная директория\n{self.path}')
            return
        set_recent_projects(self.path, get_recent_projects())

        self.folder_creator()  # создаём папку time functions
        self.initial()

    def reset(self):
        if self.path is None:
            return
        self.initial()

    def remp_save(self):
        if self.path is None:
            return
        Save_remp(data=remp_sourses_dict, path=self.path)

    def open_folder(self):
        if self.path is None:
            return
        os.startfile(self.path)

    def clear_global_dicts(self):
        source_list.clear()
        time_func_dict.clear()
        remp_sourses_dict.clear()
        gursa_dict.clear()

    def initial(self):
        try:
            self.notebook.destroy()
        except:
            pass

        self.clear_global_dicts()

        self.notebook = ttk.Notebook(self.parent)
        self.notebook.grid()

        tok_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('TOK')))
        pl_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('PL')))
        lay_dir = os.path.normpath(os.path.join(self.path, self.file_dict.get('LAY')))

        TOK = DataParcer(tok_dir).tok_decoder()
        PL = DataParcer(pl_dir).pl_decoder()
        LAY = DataParcer(lay_dir).lay_decoder()

        if np.any(LAY[:, 1:] == 1):
            # Класс рассчте Current,Sigma
            u_tab = UnitedLayers(parent=self.parent, path=self.path, name='Current and Sigma',
                                 energy_type='Current and Sigma')

            u_tab.lay_dir = lay_dir
            u_tab.pl_dir = pl_dir

            self.notebook.add(u_tab, text=f"Current and Sigma")
            u_tab.notebooks()

        for key in PL.keys():
            ar = PL.get(key)
            for i in range(ar.shape[0]):
                for j in range(1, ar.shape[1]):
                    if ar[i, j] == 1:
                        energy_type = f'Источник электронов №{key} из {j}го в {i}й'
                        name = f'Flu_e_{key}_{j}{i}'
                        tab = FluTab(self.parent, self.path, name, f'{energy_type}')
                        self.notebook.add(tab, text=f"{tab.name}")
                        tab.notebooks()

            # if ar[:, 0].any() == 1:
            #     mb.showinfo('ERROR', 'Частицы в нулевом слое!')

        if TOK[0] == 1:
            energy_type = 'Начальное поле'
            tab = InitialField(self.parent, self.path, 'Initial_field', f'{energy_type}')
            self.notebook.add(tab, text=f"{tab.name}")
            tab.notebooks()

        if TOK[1] == 1:
            energy_type = 'Внешнее поле'

            tab = ExternalField(self.parent, self.path, 'External_field', f'{energy_type}')
            self.notebook.add(tab, text=f"{tab.name}")
            tab.notebooks()

        if TOK[2] == 1:
            energy_type = 'Gursa'

            tab = Gursa(self.parent, self.path, 'Gursa', f'{energy_type}')
            self.notebook.add(tab, text=f"{tab.name}")
            tab.notebooks()

        if TOK[2] == 0:
            energy_type = 'Koshi'

            tab = Koshi(self.parent, self.path, 'PECHS', f'{energy_type}')
            self.notebook.add(tab, text=f"{tab.name}")
            tab.koshi_nb()

        plane_check = False  # затычка перед нормальной проверкой на наличие в проекте
        if plane_check is True:
            tab = PlaneWave(self.parent, self.path, 'PlaneWave', 'Плоская волна')
            self.notebook.add(tab, text=f"{tab.name}")
            tab.notebooks()
