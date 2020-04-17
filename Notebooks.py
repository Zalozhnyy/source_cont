import tkinter as tk
from tkinter import ttk

from United_Layers import UnitedLayers
from Gursa import Gursa
from TOK import InitialField, ExternalField, Koshi
from Flu import FluTab
from plane_wave import PlaneWave
from Project_reader import DataParcer
from Main_frame import FrameGen
from utility import *
import sys

sys.path.append(os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

def checker(parent):
    if os.path.exists(r"config.txt"):
        print('config exist')
    else:
        open_button()
    cur_dir = config_read()

    if len(cur_dir) < 1:
        print(f'len cur_dir < 1')
        mb.showerror('Path error', 'Укажите все необходимые директории')
        answer = mb.askyesno(title="Директории не выбраны", message="Выбрать директории заново?")
        if answer is True:
            open_button()
            cur_dir = config_read()
        else:
            parent.destroy()
            return

    if not os.path.exists(rf"{cur_dir[0]}"):
        mb.showerror('Dir error', 'Директория не существует. Укажите путь к PECHS.')
        open_button()
        print('dir not exist ', f' {cur_dir[0]}')
        cur_dir = config_read()

    dir = pr_dir()

    if not os.path.exists(rf'{dir}/time functions'):
        os.mkdir(f'{dir}/time functions')
    if not os.path.exists(f'{dir}/time functions/user configuration'):
        os.mkdir(os.path.join(f'{dir}/time functions/user configuration'))
    if not os.path.exists(f'{dir}/time functions/output dicts'):
        os.mkdir(os.path.join(f'{dir}/time functions/output dicts'))

    if not os.path.exists(f'{dir}/time functions/Gursa'):
        os.mkdir(os.path.join(f'{dir}/time functions/Gursa'))

    if len(DataParcer(os.path.normpath(os.path.join(cur_dir[0], check_folder().get('TOK')))).tok_decoder()) > 0:
        if not os.path.exists(f'{dir}/time functions/TOK'):
            os.mkdir(os.path.join(f'{dir}/time functions/TOK'))

    try:
        lay_dir = os.path.join(cur_dir[0], check_folder().get('LAY'))
        DataParcer(lay_dir).lay_decoder()
    except FileNotFoundError:
        mb.showerror('Path error', 'Директория указана неверно')
        cur_dir.clear()
        open_button()
        cur_dir = config_read()
    # check_folder()

    return cur_dir


def reset(parent):
    for tabs in parent:
        tabs.destroy()
    tab_list.clear()

    check_folder().clear()
    source_list.clear()
    time_func_dict.clear()
    gursa_dict.clear()
    source_number = 1
    main()


def change_path(parent):
    for tabs in parent:
        tabs.destroy()

    tab_list.clear()
    check_folder().clear()
    source_list.clear()
    time_func_dict.clear()
    gursa_dict.clear()
    source_number = 1

    open_button()
    main()


def main():
    cur_dir = checker(root)

    file_dict = check_folder()

    tok_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('TOK')))
    pl_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('PL')))

    TOK = DataParcer(tok_dir).tok_decoder()
    PL = DataParcer(pl_dir).pl_decoder()

    main_frame = FrameGen(root)
    main_frame._konstr()
    main_frame.filemenu.add_command(label="Путь к РЭМП", command=lambda: change_path(tab_list))
    main_frame.filemenu.add_command(label="Reset", command=lambda: reset(tab_list))
    main_frame.filemenu.add_command(label="Exit", command=main_frame.onExit)

    # Класс рассчте Current,Sigma,Flu
    u_tab = UnitedLayers(root, energy_type='Current and Sigma')

    u_tab.lay_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('LAY')))
    u_tab.pl_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('PL')))

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
                    tab = FluTab(root, name, f'{energy_type}')
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
        tab = InitialField(root, 'Initial_field', f'{energy_type}')
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.notebooks()

        tab_list.append(tab)

    if TOK[1] == 1:
        energy_type = 'Внешнее поле'

        tab = ExternalField(root, 'External_field', f'{energy_type}')
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.notebooks()

        tab_list.append(tab)

    if TOK[2] == 1:
        energy_type = 'Gursa'

        tab = Gursa(root, 'Gursa', f'{energy_type}')
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.notebooks()

        tab_list.append(tab)

    if TOK[2] == 0:
        energy_type = 'Koshi'

        tab = Koshi(root, 'PECHS', f'{energy_type}')
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.koshi_nb()
        tab_list.append(tab)

    plane_check = True  # затычка перед нормальной проверкой на наличие в проекте
    if plane_check is True:
        tab = PlaneWave(root, 'PlaneWave', 'Плоская волна')
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.notebooks()
        tab_list.append(tab)


if __name__ == '__main__':


    root = tk.Tk()
    root.geometry('1200x600')

    nb = ttk.Notebook(root)
    nb.grid()

    main()

    root.mainloop()
