import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import locale


# def config_read():
#     with open(r"config.txt", 'r', encoding='utf-8') as g:
#         cur_dir = []
#         for line in g:
#             cur_dir.append(line.strip())
#     return cur_dir


# def open_button():
#     filename = fd.askdirectory(title='Укажите путь к проекту REMP', initialdir=os.getcwd())
#     if filename == '':
#         return
#     handle = open(r"config.txt", "w", encoding='utf-8')
#     handle.write(f'{filename}')
#     handle.close()
#
#     with open(r"config.txt", 'r', encoding='utf-8') as g:
#         cur_dir = []
#         for line in g:
#             cur_dir.append(line.strip())
#     # if len(cur_dir) < 1:
#     #     mb.showerror('Error', 'Путь не выбран')
#     # else:
#     #     mb.showinfo('Info', 'Путь сохранён.')
#     print(cur_dir)
#     # main()


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


# def pr_dir():
#     pr_dir = os.path.abspath(config_read()[0])
#     return pr_dir

def timef_global_save(path):
    # global time_func_dict
    pr_dir = path.split('/')[-1]
    if len(time_func_dict) == 0:
        mb.showinfo('save', 'Нечего сохранять!')
        return
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
        print('dir =', directory)
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
    try:
        with open('properties.ini', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for i in lines:
            unic_path.update({i.strip(): ''})
    except:
        pass

    for f in os.listdir(path):
        if f.endswith(".PRJ") or f.endswith(".prj"):
            unic_path.update({path: ''})

    for i in path_dict.keys():
        unic_path.update({i.strip(): ''})

    with open('properties.ini', 'w', encoding='utf-8') as file:
        for i, key in enumerate(unic_path.keys()):
            file.write(key + '\n')


def get_recent_projects():
    out = {}
    try:
        with open('properties.ini', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for i in lines:
            out.update({i.strip(): ''})
    except:
        pass
    return out


source_list = []
gursa_dict = {}
source_number = 1

time_func_dict = {}

remp_sourses_dict = {}

unic_path = get_recent_projects()
dict_for_recent_pr = {}
recent_path = ''
path_for_remp_save =''

tab_list = []

# if __name__ == '__main__':
#     test = tk.Tk()
#
#     tk.Button(test, text='123', command=lambda: file_dialog(title='Выберите файл spectr',
#                                                             initialdir=f'{}/pechs/spectr',
#                                                             filetypes=(
#                                                                 ("all files", "*.*"), ("txt files", "*.txt*")))).pack()
#
#     test.mainloop()

