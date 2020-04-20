import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from collections import namedtuple


def config_read():
    with open(r"config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line.strip())
    return cur_dir


def open_button():
    filename = fd.askdirectory(title='Укажите путь к проекту REMP', initialdir=os.getcwd())
    handle = open(r"config.txt", "w", encoding='utf-8')
    handle.write(f'{filename}')
    handle.close()

    with open(r"config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line.strip())
    if len(cur_dir) < 1:
        mb.showerror('Error', 'Путь не выбран')
    else:
        mb.showinfo('Info', 'Путь сохранён.')
    print(cur_dir)
    # main()


def check_folder():
    prj_name = []
    for f in os.listdir(config_read()[0]):
        if f.endswith(".PRJ") or f.endswith(".prj"):
            prj_name.append(f)

    with open(os.path.join(config_read()[0], rf'{prj_name[0]}'), 'r', encoding='utf-8') as file:
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


def pr_dir():
    pr_dir = os.path.abspath(config_read()[0])
    return pr_dir


def file_dialog(title=None, initialdir=None, filetypes=None):
    directory = fd.askopenfilename(title=title, initialdir=initialdir, filetypes=filetypes)
    if os.path.exists(directory):
        print('dir =', directory)
        return directory


def save_for_remp_form(source_type=None, source_name=None, layer_index=None, amplitude=None,
                       time_for_dict=None, particle_index=None, func_for_dict=None,
                       lag_and_koord=None, distribution=None, spectre=None,
                       external_field_component=None):

    out = {'source_type': source_type,
           'source_name': source_name,
           'external_field_component':external_field_component,
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


source_list = []
gursa_dict = {}
source_number = 1

time_func_dict = {}

remp_sourses_dict = {}

tab_list = []

if __name__ == '__main__':
    test = tk.Tk()

    tk.Button(test, text='123', command=lambda: file_dialog(title='Выберите файл spectr',
                                                            initialdir=f'{config_read()[0]}/pechs/spectr',
                                                            filetypes=(
                                                                ("all files", "*.*"), ("txt files", "*.txt*")))).pack()

    test.mainloop()
