import os
import sys

sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from tkinter import ttk
import numpy as np
import locale

from United_Layers import UnitedLayers
from Gursa import Gursa
from TOK import InitialField, ExternalField, Koshi
from Flu import FluTab
from plane_wave import PlaneWave
from Project_reader import DataParcer
from Main_frame import *
from utility import *


def folder_creator(path):
    dir = path

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


# def reset(parent):
#     for tabs in parent:
#         tabs.destroy()
#     tab_list.clear()
#
#     source_list.clear()
#     time_func_dict.clear()
#     gursa_dict.clear()
#     remp_sourses_dict.clear()
#     source_number = 1
#
#     global reset_trigger
#     reset_trigger = True
#
#     main()


def change_path(parent):

    for tabs in parent:
        tabs.destroy()

    tab_list.clear()
    source_list.clear()
    time_func_dict.clear()
    remp_sourses_dict.clear()
    gursa_dict.clear()
    source_number = 1

    path = open_button()
    main(path)


def start_from_recent(path, parent):
    print(path)
    if len(parent) != 0:
        for tabs in parent:
            tabs.destroy()

    tab_list.clear()
    source_list.clear()
    time_func_dict.clear()
    remp_sourses_dict.clear()
    gursa_dict.clear()
    source_number = 1
    main(path)


def main(path):
    # main_frame = FrameGen(root)

    if path is None:
        return

    file_dict = check_folder(path)
    if file_dict is None:
        mb.showerror('Project error', f'Файл .PRJ  не найден. Указана неправильная директория\n{main_frame.path}')
        return
    set_recent_projects(path, unic_path)

    folder_creator(path)  # создаём папку time functions

    tok_dir = os.path.normpath(os.path.join(path, file_dict.get('TOK')))
    pl_dir = os.path.normpath(os.path.join(path, file_dict.get('PL')))
    lay_dir = os.path.normpath(os.path.join(path, file_dict.get('LAY')))

    TOK = DataParcer(tok_dir).tok_decoder()
    PL = DataParcer(pl_dir).pl_decoder()
    LAY = DataParcer(lay_dir).lay_decoder()

    if np.any(LAY[:, 1:] == 1):
        # Класс рассчте Current,Sigma
        u_tab = UnitedLayers(root, energy_type='Current and Sigma', path=path)

        u_tab.lay_dir = lay_dir
        u_tab.pl_dir = pl_dir

        u_tab.notebook_tab = nb.add(u_tab, text=f"Current and Sigma")
        u_tab.notebooks()

        tab_list.append(u_tab)

    for key in PL.keys():
        ar = PL.get(key)
        for i in range(ar.shape[0]):
            for j in range(1, ar.shape[1]):
                if ar[i, j] == 1:
                    energy_type = f'Источник электронов №{key} из {j}го в {i}й'
                    name = f'Flu_e_{key}_{j}{i}'
                    tab = FluTab(root, name, f'{energy_type}', path=path)
                    tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
                    tab.notebooks()

                    tab_list.append(tab)
                    # self.output_dictionary_flu(name, energy_type)
                    # source_number += 1
                    #
                    # lay_label = tk.Label(self.source_labels, text=f'{name}')
                    # lay_label.grid(row=7 + self.label_num, column=3)
                    # self.layers_label_list.append(lay_label)
                    # self.label_num += 1

        if ar[:, 0].any() == 1:
            mb.showinfo('ERROR', 'Частицы в нулевом слое!')

    if TOK[0] == 1:
        energy_type = 'Начальное поле'
        tab = InitialField(root, 'Initial_field', f'{energy_type}', path=path)
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.notebooks()

        tab_list.append(tab)

    if TOK[1] == 1:
        energy_type = 'Внешнее поле'

        tab = ExternalField(root, 'External_field', f'{energy_type}', path=path)
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.notebooks()

        tab_list.append(tab)

    if TOK[2] == 1:
        energy_type = 'Gursa'

        tab = Gursa(root, 'Gursa', f'{energy_type}', path=path)
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.notebooks()

        tab_list.append(tab)

    if TOK[2] == 0:
        energy_type = 'Koshi'

        tab = Koshi(root, 'PECHS', f'{energy_type}', path=path)
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.koshi_nb()
        tab_list.append(tab)

    plane_check = True  # затычка перед нормальной проверкой на наличие в проекте
    if plane_check is True:
        tab = PlaneWave(root, 'PlaneWave', 'Плоская волна', path=path)
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.notebooks()
        tab_list.append(tab)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1200x600')
    main_frame = FrameGen(root)
    main_frame._konstr()

    main_frame.filemenu.add_command(label="Открыть проект", command=lambda: change_path(tab_list))

    main_frame.recent_pr_menu = tk.Menu(main_frame.filemenu, tearoff=0)
    for key in get_recent_projects().keys():
        main_frame.recent_pr_menu.add_command(label=f'{key}', command=lambda: start_from_recent(key, tab_list))

    main_frame.filemenu.add_cascade(label="Недавние проекты", menu=main_frame.recent_pr_menu)

    main_frame.filemenu.add_command(label="Сохранить (output dicts)", command=timef_global_save)

    main_frame.toolbar()

    main_frame.filemenu.add_command(label="Очистить папку time functions", command=tf_global_del)
    # main_frame.filemenu.add_command(label="Reset", command=lambda: reset(tab_list))
    main_frame.filemenu.add_command(label="Exit", command=main_frame.onExit)

    nb = ttk.Notebook(root)
    nb.grid()

    # main()

    root.mainloop()
