import tkinter as tk
from tkinter import ttk

from Gursa import Gursa
from TOK import InitialField, ExternalField, Koshi
from Flu import Flu
from Sigma_Current import Current
from Project_reader import DataParcer
from Main_frame import FrameGen
from utility import *


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

    dir = pr_dir()

    if not os.path.exists(rf"{cur_dir[0]}"):
        mb.showerror('Dir error', 'Директория не существует. Укажите путь к PECHS.')
        open_button()
        print('dir not exist ', f' {cur_dir[0]}')
        cur_dir = config_read()

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


def timef_global_save():
    # global time_func_dict
    with open(f'{pr_dir}/time functions/time functions list.txt', 'w', encoding='utf-8') as file:

        for item in time_func_dict.items():
            if type(item) is not list:
                file.write(f'{item[0]} = {item[1]}\n')
            else:
                for i in item:
                    file.write(f'{i[0]} = {i[1]}\n')

        mb.showinfo('Save', 'Сохранено в time functions list.txt')

        for out_dict in source_list:
            name = out_dict.get('<название источника>')
            with open(rf'{pr_dir}/time functions/output dicts/{name}_out.txt', 'w', encoding='utf-8') as file:
                for item in out_dict.items():
                    file.write(f'{item[0]}\n')
                    file.write(f'{item[1]}\n')


def tf_global_del():
    dir = os.path.join(config_read()[0], 'time functions')
    ask = mb.askyesno('Очистка папки', 'Вы уверены, что хотите удалить все time функции?')
    if ask is True:

        for files in os.walk(dir):
            for file in files[2]:
                if file.endswith('.tf') or file.endswith('.txt'):
                    path = os.path.join(files[0], file)
                    os.remove(path)


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

    lay_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('LAY')))
    pl_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('PL')))
    tok_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('TOK')))
    grid_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('GRD')))

    LAY = DataParcer(lay_dir).lay_decoder()
    PL = DataParcer(pl_dir).pl_decoder()
    TOK = DataParcer(tok_dir).tok_decoder()

    main_frame = FrameGen(root)
    main_frame._konstr()
    main_frame.filemenu.add_command(label="Путь к PECHS", command=lambda: change_path(tab_list))
    main_frame.filemenu.add_command(label="Reset",command=lambda: reset(tab_list))
    main_frame.filemenu.add_command(label="Exit", command=main_frame.onExit)

    for i in range(LAY.shape[0]):
        if LAY[i, 1] == 1:
            energy_type = 'Current'

            tab = Current(root, f'{energy_type}_layer {i}', 'Current')
            tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
            tab.notebooks()

            tab_list.append(tab)

        if LAY[i, 2] == 1:
            energy_type = 'Sigma'

            tab = Current(root, f'{energy_type}_layer {i}', 'Sigma')
            tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
            tab.notebooks()

            tab_list.append(tab)

    for i in range(PL.shape[0]):
        for j in range(1, PL.shape[1]):
            if PL[i, j] == 1:
                tab = Flu(root, f'Flu_e{j}{i}', f'Источник электронов из {j}го в {i}й')
                tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
                tab.notebooks()

                tab_list.append(tab)

    if PL[:, 0].any() == 1:
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

        tab = Koshi(root, 'Koshi', f'{energy_type}')
        tab.notebook_tab = nb.add(tab, text=f"{tab.name}")
        tab.koshi_nb()

        tab_list.append(tab)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1200x600')

    nb = ttk.Notebook(root)
    nb.grid(sticky='nwse')

    main()

    root.mainloop()
