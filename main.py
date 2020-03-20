import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import integrate


def config_read():
    with open(r"config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line.strip())
    return cur_dir


def open_button():
    filename = fd.askdirectory(title='Укажите путь к проекту REMP',
                               initialdir=os.getcwd())
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
    main()


def check_folder():
    prj_name = []
    for f in os.listdir(config_read()[0]):
        if f.endswith(".PRJ") or f.endswith(".prj"):
            prj_name.append(f)

    with open(os.path.join(config_read()[0], rf'{prj_name[0]}'), 'r') as file:
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

    return out


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


class FrameGen(tk.Frame):
    # def __new__(cls, parent, name='Title', energy_type='Название типа энергии'):
    #     return super(FrameGen, cls).__new__(cls)

    def __init__(self, parent, name='Title', energy_type='Название типа энергии'):
        tk.Frame.__init__(self, parent)
        self.parent = root
        self.name = name
        self.energy_type = energy_type
        self.__konstr()

        self.entry_func = []
        self.entry_time = []
        self.cell_numeric = tk.StringVar()
        self.func_entry_vel = []
        self.time_entry_vel = []
        self.func_list = []
        self.time_list = []
        self.entry_f_val = tk.StringVar()
        self.entry_time_fix_val = tk.StringVar()
        self.spectr = []

        self.path = os.path.normpath(config_read()[0])
        self.dir_name = config_read()[0].split('/')[-1]
        self.gursa_count = []
        self.gursa_numeric = 0
        self.existe_gursa_label = []
        self.gursa_dict = {}
        self.gursa_label_dict = {}

        self.x = []

        self.external_tf_num = []

        self.pr_dict = {
            '<номер источника>': 0,
            '<тип источника>': 0,
            '<название источника>': 0,
            '<номер слоя>': 0,
            '<номер слоя из>': 0,
            '<номер слоя в>': 0,
            '<амплитуда источинка в ближней зоне источника>': 0,
            '<амплитуда источинка в дальней зоне источника>': 0,
            '<спектр источника>': 0,
            '<временная функция источинка>': 0,
            '<запаздывание(0 - нет, 1 - есть)>': 0,
            '<X-координата источника>': 0,
            '<Y-координата источника>': 0,
            '<Z-координата источника>': 0,
            '<X-координата объекта>': 0,
            '<Y-координата объекта>': 0,
            '<Z-координата объекта>': 0,
            '<полярный угол поворта локальной системы координат относительно глобальной>': None,
            '<азимутальный угол поворта локальной системы координат относительно глобальной>': None,
            '<X-компонента направляющего косинуса для расчета в дальней зоне>': None,
            '<Y-компонента направляющего косинуса для расчета в дальней зоне>': None,
            '<Z-компонента направляющего косинуса для расчета в дальней зоне>': None
        }
        self.gursa_out_dict = {}

        print(repr(self))

    def __repr__(self):
        return f'{self.name}'

    def __konstr(self):
        self.parent.title("Sources")
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Путь к PECHS", command=lambda: (tk.Frame.destroy(self), open_button()))
        filemenu.add_command(label="Reset", command=self.reset)
        filemenu.add_command(label="Global save", command=timef_global_save)
        filemenu.add_command(label="Очистить timefunctions", command=tf_global_del)
        filemenu.add_command(label="Exit", command=self.onExit)

        menubar.add_cascade(label="Файл", menu=filemenu)
        # menubar.add_command(label="test", command=lambda: print(len(source_list)))

    def notebooks(self):
        nb.add(self, text=f"{self.name}")

        rows = 0
        while rows < 100:
            self.rowconfigure(rows, weight=0, minsize=5)
            self.columnconfigure(rows, weight=0, minsize=5)
            rows += 1

        label_name_energy = tk.Label(self, text=f'{self.energy_type}')
        label_name_energy.grid(row=5, column=0, columnspan=2)
        label_func = tk.Label(self, text='value', width=8)
        label_func.grid(row=6, column=1, padx=2, pady=2)
        label_time = tk.Label(self, text='time', width=8)
        label_time.grid(row=6, column=0, padx=2, pady=2)

        self.button_browse = tk.Button(self, width=10, text='Load', state='active',
                                       command=lambda: self.ent_load(
                                           fd.askopenfilename(
                                               initialdir=rf'{pr_dir}/time functions/user configuration').split(
                                               '/')[-1]))
        self.button_browse.grid(row=1, column=2, padx=3)
        self.button_browse_def = tk.Button(self, width=10, text='Load default', state='active',
                                           command=lambda: self.ent_load('default.dtf'))
        self.button_browse_def.grid(row=1, column=3, padx=3)
        self.button_save = tk.Button(self, width=10, text='Save as', state='disabled', command=self.time_save)
        self.button_save.grid(row=2, column=2, padx=3)
        self.button_save_def = tk.Button(self, width=10, text='Save as default', command=self.time_save_def,
                                         state='disabled')
        self.button_save_def.grid(row=2, column=3, padx=3)
        self.entry_generate_value = tk.Entry(self, width=5, textvariable=self.cell_numeric, state='normal')
        self.entry_generate_value.grid(row=5, column=3)
        self.button_generate = tk.Button(self, width=10, text='Generate', command=self.ent, state='active')
        self.button_generate.grid(row=5, column=2, padx=3)
        self.button_read_gen = tk.Button(self, width=10, text='Read', command=self.get, state='disabled')
        self.button_read_gen.grid(row=6, column=2)
        self.button_calculate = tk.Button(self, width=10, text='Calculate', command=self.calculate, state='disabled')
        self.button_calculate.grid(row=1, column=5, padx=3)
        self.add_button = tk.Button(self, width=6, text='add cell', state='disabled',
                                    command=lambda: self.add_entry())
        self.del_button = tk.Button(self, width=6, text='del cell', state='disabled',
                                    command=lambda: self.delete_entry())
        self.add_button.grid(row=1, column=0, sticky='WS')
        self.del_button.grid(row=1, column=1, sticky='WS')

        if 'Sigma' in self.name or 'Current' in self.name or 'Flu' in self.name or 'Gursa' in self.name:
            self.entry_f_val.set(1.)
            label_f = tk.Label(self, text='F')
            label_f.grid(row=2, column=5, padx=3, sticky='E')
            entry_f = tk.Entry(self, width=3, textvariable=self.entry_f_val)
            entry_f.grid(row=2, column=6, padx=3)

        if 'External_field' in self.name:
            tk.Label(self, text='Ex').grid(row=2, column=5, sticky='E', padx=3)
            tk.Label(self, text='Ey').grid(row=3, column=5, sticky='E', padx=3)
            tk.Label(self, text='Ez').grid(row=4, column=5, sticky='E', padx=3)
            tk.Label(self, text='hx').grid(row=5, column=5, sticky='E', padx=3)
            tk.Label(self, text='hy').grid(row=6, column=5, sticky='E', padx=3)
            tk.Label(self, text='hz').grid(row=7, column=5, sticky='E', padx=3)
            self.button_calculate.destroy()

            self.graph_ext_checkbutton = tk.BooleanVar()
            self.graph_ext_checkbutton.set(0)
            ttk.Checkbutton(self, text='Построение графика', variable=self.graph_ext_checkbutton,
                            onvalue=1, offvalue=0).grid(row=1, column=7, columnspan=2)

            self.external_field_values_dict = {
                'Ex': 0,
                'Ey': 0,
                'Ez': 0,
                'hx': 0,
                'hy': 0,
                'hz': 0
            }
            self.ext_load_tf_button = []
            self.some_x_val = [tk.StringVar() for _ in range(6)]

            for i in self.some_x_val:
                i.set('0')
            for i in range(6):
                some_x = tk.Entry(self, textvariable=self.some_x_val[i], width=4)
                some_x.grid(row=2 + i, column=6)

            keys = []
            [keys.append(i) for i in self.external_field_values_dict.keys()]

            for i in range(len(keys)):
                self.ext_load_tf_button.append(tk.Button(self, text=f'calc {keys[i]} tf', overrelief='ridge',
                                                         width=9, state='disabled'))
                self.ext_load_tf_button[i].grid(row=2 + i, column=7, padx=3)

            self.ext_load_tf_button[0].configure(command=lambda: self.calculate_external_field(keys[0]))
            self.ext_load_tf_button[1].configure(command=lambda: self.calculate_external_field(keys[1]))
            self.ext_load_tf_button[2].configure(command=lambda: self.calculate_external_field(keys[2]))
            self.ext_load_tf_button[3].configure(command=lambda: self.calculate_external_field(keys[3]))
            self.ext_load_tf_button[4].configure(command=lambda: self.calculate_external_field(keys[4]))
            self.ext_load_tf_button[5].configure(command=lambda: self.calculate_external_field(keys[5]))

        if 'Gursa' in self.name:
            self.add_button_gursa = tk.Button(self, text='Add source', width=10, command=self.gursa_cw,
                                              state='disabled')
            self.add_button_gursa.grid(row=10, column=2)

            self.button_calculate.destroy()

            self.gursa_graphs_checkbutton_val = tk.BooleanVar()
            self.gursa_graphs_checkbutton_val.set(0)
            gursa_graphs_checkbutton = tk.Checkbutton(self, text='Построение графиков',
                                                      variable=self.gursa_graphs_checkbutton_val, onvalue=1, offvalue=0)
            gursa_graphs_checkbutton.grid(row=1, column=7, columnspan=2)

            self.gursa_combobox = ttk.Combobox(self, values=self.gursa_dict.keys(), width=8)
            self.gursa_combobox.grid(row=10, column=4)
            self.delete_gursa_class_button = tk.Button(self, text='Delete obj', command=self.regrid_gursa, width=8)
            self.delete_gursa_class_button.grid(row=11, column=4)

    def gursa_cw(self):

        self.x = Gursa(name=f'Gursa_{self.gursa_numeric}')
        self.x.F = float(self.entry_f_val.get())

        self.wait_window(self.x)

        if self.x.calc_state == 1:
            self.gursa_count.append(self.x)

            self.gursa_dict.update({f'{self.x.name}': self.x})

            for label in self.gursa_label_dict.values():
                label.destroy()

            for i in range(len(self.gursa_dict.keys())):
                self.gursa_label_dict.update(
                    {f'{self.gursa_count[i].name}': tk.Label(self, text=f'{self.gursa_count[i].name}')})

            for i, label in enumerate(self.gursa_label_dict.values()):
                label.grid(row=12 + i, column=2)

            keys = []
            for i in self.gursa_dict.keys():
                keys.append(i)
            self.gursa_combobox.configure(values=keys)

            self.gursa_numeric += 1

            self.spectr = self.x.Spektr_output

            self.calculate_gursa()

            if self.x.spectr_type.get() == 1:
                type = 'DISCRETE'
                np.savetxt(f'{pr_dir}/time functions/Gursa/Spektr_output_{self.x.name}.txt',
                           self.x.Spektr_output, fmt='%-6.3g', header='SP_TYPE={}\n[DATA]'.format(type),
                           comments='', delimiter='\t')

            elif self.x.spectr_type.get() == 0:
                type = 'CONTINUOUS'
                np.savetxt(
                    f'{pr_dir}/time functions/Gursa/Spektr_output_{self.x.name}.txt',
                    self.x.Spektr_output, fmt='%-6.3g', comments='', delimiter='\t',
                    header='SP_TYPE={}\n[DATA]\n{:.2g}'.format(type, self.x.spectr_cont[0, 0]))

            time_func_dict.update({f'{self.x.name}': [f'time functions/Gursa/time_{self.x.name}.tf',
                                                      f'time functions/Gursa/Spektr_output_{self.x.name}.txt']})

            self.output_dictionary()

    def koshi_nb(self):
        nb.add(self, text=f"{self.name}")

        rows = 0
        while rows < 100:
            self.rowconfigure(rows, weight=0, minsize=5)
            self.columnconfigure(rows, weight=0, minsize=5)
            rows += 1
        source_button = tk.Button(self, text='Открыть программу source', command=lambda: os.startfile('source.exe'))
        source_button.grid(row=5, column=5)

    def regrid_gursa(self):

        for i, ob in enumerate(source_list):
            if ob.get('< название источника >') == self.gursa_combobox.get():
                mb.showinfo('work', 'work')
                source_list.pop(i)

        self.gursa_label_dict.get(self.gursa_combobox.get()).grid_forget()

        self.gursa_dict.pop(self.gursa_combobox.get())
        time_func_dict.pop(self.gursa_combobox.get())

        self.gursa_label_dict.pop(self.gursa_combobox.get())

        self.gursa_count.clear()
        for val in self.gursa_dict.values():
            self.gursa_count.append(val)

        for i, label in enumerate(self.gursa_label_dict.values()):
            # print(label)
            label.grid_configure(row=12 + i)

        keys = []
        for i in self.gursa_dict.keys():
            keys.append(i)
        self.gursa_combobox.configure(values=keys)

    def initial_field_notebook(self):
        nb.add(self, text=f"{self.name}")
        self.ini_f_labes_file = []

        rows = 0
        while rows < 50:
            self.rowconfigure(rows, weight=1, minsize=3)
            self.columnconfigure(rows, weight=1, minsize=3)
            rows += 1

        tk.Label(self, text='Ex').grid(row=2, column=5, sticky='E', padx=3)
        tk.Label(self, text='Ey').grid(row=3, column=5, sticky='E', padx=3)
        tk.Label(self, text='Ez').grid(row=4, column=5, sticky='E', padx=3)
        tk.Label(self, text='hx').grid(row=5, column=5, sticky='E', padx=3)
        tk.Label(self, text='hy').grid(row=6, column=5, sticky='E', padx=3)
        tk.Label(self, text='hz').grid(row=7, column=5, sticky='E', padx=3)

        self.some_x_val = [tk.StringVar() for _ in range(6)]

        for i in self.some_x_val:
            i.set('0')
        for i in range(6):
            some_x = tk.Entry(self, textvariable=self.some_x_val[i], width=4)
            some_x.grid(row=2 + i, column=6)

        ini_save_button = tk.Button(self, width=10, text='Save', state='normal', command=self.save_Initial_field)
        ini_save_button.grid(row=0, column=6, pady=5)

    def ent(self):
        self.entry_func.clear()
        self.entry_time.clear()
        self.func_entry_vel.clear()
        self.time_entry_vel.clear()

        self.func_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric.get()))]
        self.time_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric.get()))]
        for i in range(int(self.cell_numeric.get())):
            self.entry_func.append(tk.Entry(self, width=9, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=7 + i, column=1, pady=3)
            self.entry_time.append(tk.Entry(self, width=9, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=7 + i, column=0, pady=3)

        a, A = self.time_grid()

        self.entry_time_label = tk.Label(self, text=f'{a}')
        self.entry_time_label.grid(row=7 + int(self.cell_numeric.get()) + 1, column=0)
        self.entry_func_label = tk.Label(self, text='[0 : 1]')
        self.entry_func_label.grid(row=7 + int(self.cell_numeric.get()) + 1, column=1)

        self.obriv_tf_label = tk.Label(self, text='Обрыв tf')
        self.obriv_tf_label.grid(row=8 + int(self.cell_numeric.get()) + 1, column=0)
        self.entry_time_fix_val.set(f'{A[-1]}')
        self.entry_time_fix = tk.Entry(self, textvariable=self.entry_time_fix_val, width=6)
        self.entry_time_fix.grid(row=8 + int(self.cell_numeric.get()) + 1, column=1)

        self.button_browse.configure(state='disabled')
        self.button_browse_def.configure(state='disabled')
        self.button_read_gen.configure(state='normal')
        self.add_button.configure(state='normal')
        self.del_button.configure(state='normal')

        if self.name != 'External_field' and self.name != 'Gursa':
            self.button_calculate.configure(state='normal')

        if self.name == 'External_field':
            for i in self.ext_load_tf_button:
                i.configure(state='normal')
        if self.name == 'Gursa':
            self.add_button_gursa.configure(state='normal')

    def ent_load(self, path):
        with open(rf'{pr_dir}/time functions/user configuration/{path}', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        # print(lines)

        for word in lines[0].split():
            self.func_entry_vel.append(float(word))
        for word in lines[1].split():
            self.time_entry_vel.append(float(word))
        # print('func = ', self.func_entry_vel)
        # print('time = ', self.time_entry_vel)

        entr_utility_func = [tk.StringVar() for _ in range(len(self.func_entry_vel))]
        entr_utility_time = [tk.StringVar() for _ in range(len(self.func_entry_vel))]
        for i in range(len(self.func_entry_vel)):
            self.entry_func.append(tk.Entry(self, width=9, textvariable=entr_utility_func[i], justify='center'))
            self.entry_func[i].grid(row=7 + i, column=1, pady=3)
            entr_utility_func[i].set('{:.4g}'.format(self.func_entry_vel[i]))
            self.func_entry_vel[i] = entr_utility_func[i]
            # print(f'{i} ', type(entr_utility_func[i]), entr_utility_func[i])

        for i in range(len(self.time_entry_vel)):
            self.entry_time.append(tk.Entry(self, width=9, textvariable=entr_utility_time[i], justify='center'))
            self.entry_time[i].grid(row=7 + i, column=0, pady=3)
            entr_utility_time[i].set('{:.4g}'.format(self.time_entry_vel[i]))
            self.time_entry_vel[i] = entr_utility_time[i]

        a, A = self.time_grid()

        self.entry_time_label = tk.Label(self, width=9, text=f'{a}')
        self.entry_time_label.grid(row=7 + len(self.time_entry_vel) + 1, column=0)
        self.entry_func_label = tk.Label(self, width=9, text='[0 : 1]')
        self.entry_func_label.grid(row=7 + len(self.func_entry_vel) + 1, column=1)

        self.obriv_tf_lavel = tk.Label(self, text='Обрыв tf')
        self.obriv_tf_lavel.grid(row=8 + len(self.func_entry_vel) + 1, column=0)
        self.entry_time_fix_val.set(f'{A[-1]}')
        self.entry_time_fix = tk.Entry(self, textvariable=self.entry_time_fix_val, width=6)
        self.entry_time_fix.grid(row=8 + len(self.func_entry_vel) + 1, column=1)

        if len(self.func_entry_vel) != len(self.time_entry_vel):
            mb.showerror('Load error', 'Размерности не совпадают')
            self.onExit()

        self.button_read_gen.configure(state='normal')
        self.button_generate.configure(state='disabled')
        self.button_browse_def.configure(state='disabled')
        self.button_browse.configure(state='disabled')
        self.add_button.configure(state='normal')
        self.del_button.configure(state='normal')

    def add_entry(self):
        for i in self.entry_func:
            i.destroy()
        for i in self.entry_time:
            i.destroy()

        self.entry_time.clear()
        self.entry_func.clear()

        new_f = tk.StringVar()
        self.func_entry_vel.append(new_f)
        new_t = tk.StringVar()
        self.time_entry_vel.append(new_t)

        for i in range(len(self.time_entry_vel)):
            self.entry_func.append(tk.Entry(self, width=9, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=7 + i, column=1, pady=3)
            self.entry_time.append(tk.Entry(self, width=9, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=7 + i, column=0, pady=3)

        self.entry_time_label.grid_configure(row=len(self.func_entry_vel) + 2 + 7)
        self.entry_func_label.grid_configure(row=len(self.func_entry_vel) + 2 + 7)

        self.obriv_tf_lavel.grid_configure(row=len(self.func_entry_vel) + 2 + 8)
        self.entry_time_fix.grid_configure(row=len(self.func_entry_vel) + 2 + 8)

        self.button_calculate.configure(state='disabled')

    def delete_entry(self):
        for i in self.entry_func:
            i.destroy()
        for i in self.entry_time:
            i.destroy()

        self.entry_time.clear()
        self.entry_func.clear()

        self.func_entry_vel.pop()
        self.time_entry_vel.pop()

        for i in range(len(self.time_entry_vel)):
            self.entry_func.append(tk.Entry(self, width=9, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=7 + i, column=1, pady=3)
            self.entry_time.append(tk.Entry(self, width=9, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=7 + i, column=0, pady=3)

        self.entry_time_label.grid_configure(row=len(self.func_entry_vel) + 2 + 7)
        self.entry_func_label.grid_configure(row=len(self.func_entry_vel) + 2 + 7)

        self.obriv_tf_lavel.grid_configure(row=len(self.func_entry_vel) + 2 + 8)
        self.entry_time_fix.grid_configure(row=len(self.func_entry_vel) + 2 + 8)

        self.button_calculate.configure(state='disabled')

    # def del_entry(self):
    #
    #     self.func_entry_vel.pop()
    #     self.time_entry_vel.pop()

    def get(self):

        # print('get', type(self.func_entry_vel[0]))
        self.func_list.clear()
        self.time_list.clear()

        for i in self.func_entry_vel:
            self.func_list.append(float(i.get()))
        for i in self.time_entry_vel:
            self.time_list.append(float(i.get()))

        self.value_check(func=self.func_list, time=self.time_list)
        self.button_generate.configure(state='disabled')
        self.entry_generate_value.configure(state='disabled')
        self.button_save.configure(state='active')
        self.button_save_def.configure(state='active')
        self.button_browse.configure(state='disabled')
        if self.name != 'External_field' and self.name != 'Gursa':
            self.button_calculate.configure(state='normal')

        if self.name == 'External_field':
            for i in self.ext_load_tf_button:
                i.configure(state='normal')
        if self.name == 'Gursa':
            self.add_button_gursa.configure(state='normal')

        # print('time = ', self.time_list)
        # print('func = ', self.func_list)

    def time_save(self):

        save_dir = fd.asksaveasfilename(title='Назовите файл', filetypes=(("dtf files", "*.dtf"), ("All files", "*.*"))
                                        , defaultextension=("dtf files", "*.dtf"),
                                        initialdir=rf'{pr_dir}/time functions/user configuration')
        with open(save_dir, 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            save_dir_inf = save_dir.split('/')[-1]
            mb.showinfo('Save', f'Сохранено в time functions/user configuration/{save_dir_inf}')

    def time_save_def(self):
        with open(rf'{pr_dir}/time functions/user configuration/default.dtf', 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            mb.showinfo('Save default',
                        f'Сохранено стандартной в time functions/user configuration/default.dtf')

    def interpolate_user_time(self):
        self.grd_def = self.child_parcecer_grid()
        self.user_timeset = float(self.entry_time_fix_val.get())

        # print(f'функция {self.func_list}')
        # print(f'время {self.time_list}')
        entry_f = np.array(self.func_list)
        entry_t = np.array(self.time_list)

        # блок проверки на ограничение пользователем тайм функции
        if self.grd_def[-1] == self.user_timeset:
            time_cell = self.grd_def
            if entry_t[-1] != time_cell[-1]:
                entry_t = np.append(entry_t, time_cell[-1])
                entry_f = np.append(entry_f, 0)
            if entry_t[0] != 0 and entry_f[0] != 0:
                entry_t = np.insert(entry_t, 0, 0)
                entry_f = np.insert(entry_f, 0, 0)
        else:
            time_right_side = np.where(self.user_timeset == self.grd_def)[0]
            if len(time_right_side) == 0:
                time_right_side = \
                    np.where(abs(self.user_timeset - self.grd_def) <= (self.grd_def[1] - self.grd_def[0]) / 2)[0]
            # print(time_right_side)
            time_cell = self.grd_def[:time_right_side[0]]
            for i in range(len(entry_f)):
                if entry_t[i] > time_cell[-1]:
                    entry_t = np.delete(entry_t, np.s_[i:], 0)
                    entry_f = np.delete(entry_f, np.s_[i:], 0)
                    break
            if entry_t[-1] != time_cell[-1]:
                entry_t = np.append(entry_t, time_cell[-1])
                entry_f = np.append(entry_f, entry_f[-1])
            if entry_t[0] != 0 and entry_f[0] != 0:
                entry_t = np.insert(entry_t, 0, 0)
                entry_f = np.insert(entry_f, 0, 0)

        for i in range(len(entry_t) - 1):
            if entry_t[i] > entry_t[i + 1]:
                print(f'Value error время уменьшается на одном из отрезков {i}')

        time_count = []
        func_out = []
        for i in range(len(entry_t) - 1):
            k, b = Calculations().linear_dif(entry_f[i], entry_t[i], entry_f[i + 1], entry_t[i + 1])
            # print(f'k = {k} , b = {b}')
            # print(np.extract((time_cell == entry_t[i]),time_cell))
            dt = time_cell[1] - time_cell[0]
            left_side = np.where(time_cell == entry_t[i])[0]
            right_side = np.where(time_cell == entry_t[i + 1])[0]

            if len(left_side) != 1:
                left_side = np.where(abs(time_cell - entry_t[i]) <= dt / 2)[0]
            if len(right_side) != 1:
                right_side = np.where(abs(time_cell - entry_t[i + 1]) <= dt / 2)[0]

            # print(type(left_side), time_cell[left_side])
            # print(type(right_side), time_cell[right_side][0], time_cell[100])
            # (f'{time_cell[left_side]} - {time_cell[right_side]}')
            if i != len(entry_t) - 2:

                for j in time_cell[left_side[0]:right_side[0]]:
                    if j == time_cell[right_side[0]]:
                        print(j)
                        print(f'curent f len = {len(func_out)}')
                        print('')
                    func_out.append(Calculations().solve(j, k, b))
                    time_count.append(j)
            else:
                for j in time_cell[left_side[0]:right_side[0] + 1]:
                    func_out.append(Calculations().solve(j, k, b))
                    time_count.append(j)

        # print(len(func_out))
        # print('заданныйэ = ', time_cell.shape, time_cell[-1])
        # print('по факту = ', len(time_count), time_count[-1])

        return func_out, time_count

    def save_Initial_field(self):

        back = self.name

        if len(self.ini_f_labes_file) != 0:
            for i in self.ini_f_labes_file:
                i.destroy()
            self.ini_f_labes_file.clear()

        if ask is True:
            self.name = tk.simpledialog.askstring('Введите имя файла', 'Func name')
            if len(self.name) == 0 or self.name == ' ':
                self.name = back
        self.ini_f_labes_file.append(tk.Label(self, text=f'time functions/time_{self.name}_koef.txt'))
        self.ini_f_labes_file[0].grid(row=0, column=7)
        Initial_field_values_dict = {
            'Ex': self.some_x_val[0].get(),
            'Ey': self.some_x_val[1].get(),
            'Ez': self.some_x_val[2].get(),
            'hx': self.some_x_val[3].get(),
            'hy': self.some_x_val[4].get(),
            'hz': self.some_x_val[5].get()
        }

        with open(rf'{pr_dir}/time functions/time_{self.name}_koef.txt', "w", encoding='utf-8') as f:
            for item in Initial_field_values_dict.items():
                # print(f'{item[0]} = {item[1]}')
                f.write(f'{item[0]} = {item[1]}\n')

    def calculate(self):
        if 'Current' in self.name or 'Sigma' in self.name or 'Flu_e' in self.name:

            if len(self.spectr) == 0:
                self.spectr_dir = fd.askopenfilename(title='Выберите файл spectr',
                                                     initialdir=f'{config_read()[0]}/pechs/spectr',
                                                     filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
                self.spectr = np.loadtxt(self.spectr_dir, skiprows=3)

            else:
                answer = mb.askyesno(title="Spectr", message="Выбрать новый спектр?")
                if answer is True:
                    self.spectr_dir = fd.askopenfilename(title='Выберите файл spectr', initialdir=f'{config_read()[0]}',
                                                         filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
                    self.spectr = np.loadtxt(self.spectr_dir, skiprows=3)

            self.calculate_lay_pl()

    def calculate_lay_pl(self):

        func_out, time_count = self.interpolate_user_time()
        func_out = np.array(func_out)
        time_count = np.array(time_count)
        output_matrix = np.column_stack((time_count, func_out))

        # integrate
        E_cp = np.sum(self.spectr[:, 0] * self.spectr[:, 1]) / np.sum(self.spectr[:, 1])

        F = float(self.entry_f_val.get())
        intergal_tf = integrate.simps(y=output_matrix[:, 1], x=output_matrix[:, 0], dx=output_matrix[:, 0])

        koef = F / (0.23 * E_cp * intergal_tf * 1e3 * 1.6e-19)

        file_name = f'time functions/time_{self.name}.tf'
        # np.savetxt(f'{pr_dir}/time functions/time_{self.name}.tf', output_matrix, fmt='%-8.4g',
        #            header=f'1 pechs\n{time_count[0]} {time_count[-1]} {koef}\n{len(time_count)}', delimiter='\t',
        #            comments='')
        np.savetxt(f'{pr_dir}/time functions/time_{self.name}.tf', output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_{self.name}.tf\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')

        time_func_dict.update({f'{self.name}': os.path.normpath(file_name)})

        self.output_dictionary()

        figure = plt.Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot(time_count, func_out, label='Пользовательская функция')

        ax.set_xlabel('Time , s', fontsize=14)
        ax.set_ylabel('Function', fontsize=14)
        chart_type = FigureCanvasTkAgg(figure, self)

        chart_type.get_tk_widget().grid(row=2, column=8, rowspan=40, columnspan=20, padx=10)
        ax.set_title(f'{self.name}')
        ax.legend()

    def calculate_external_field(self, key):

        if len(self.spectr) == 0:
            self.spectr_dir = fd.askopenfilename(title='Выберите файл spectr',
                                                 initialdir=f'{config_read()[0]}/pechs/spectr',
                                                 filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
            self.spectr = np.loadtxt(self.spectr_dir, skiprows=3)

        else:
            answer = mb.askyesno(title="Spectr", message="Выбрать новый спектр?")
            if answer is True:
                self.spectr_dir = fd.askopenfilename(title='Выберите файл spectr', initialdir=f'{config_read()[0]}',
                                                     filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
                self.spectr = np.loadtxt(self.spectr_dir, skiprows=3)

        self.external_field_values_dict = {
            'Ex': self.some_x_val[0].get(),
            'Ey': self.some_x_val[1].get(),
            'Ez': self.some_x_val[2].get(),
            'hx': self.some_x_val[3].get(),
            'hy': self.some_x_val[4].get(),
            'hz': self.some_x_val[5].get()
        }

        func_out, time_count = self.interpolate_user_time()
        func_out = np.array(func_out)
        time_count = np.array(time_count)
        output_matrix = np.column_stack((time_count, func_out))

        file_name = f'time functions/TOK/time_ext_{key}.tf'
        # np.savetxt(f'{pr_dir}/time functions/TOK/time_ext_{key}.tf', output_matrix, fmt='%-8.4g',
        #            header=f'{key} = {self.external_field_values_dict.get(key)}\ntime\t\tfunc', delimiter='\t',
        #            comments='')
        np.savetxt(f'{pr_dir}/time functions/TOK/time_ext_{key}.tf', output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_ext_{key}.tf\n'
                          f'<Составляющая поля>\n'
                          f'{key}\n'
                          f'<Значение составляющей поля>\n'
                          f'{self.external_field_values_dict.get(key)}\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')
        self.external_tf_num.append(file_name)

        if self.name in time_func_dict.keys():
            time_func_dict.popitem()
        if len(self.external_tf_num) == 1:
            time_func_dict.update({f'{self.name}': self.external_tf_num[0]})
        else:
            time_func_dict.update({f'{self.name}': self.external_tf_num})

        self.output_dictionary()

        if self.graph_ext_checkbutton.get() == 1:
            plt.plot(time_count, func_out)
            plt.title(f'{key} = {self.external_field_values_dict.get(key)}')
            plt.xlabel('Time , s', fontsize=14)
            plt.ylabel('Function', fontsize=14)
            plt.show()

    def calculate_gursa(self):
        func_out, time_count = self.interpolate_user_time()
        func_out = np.array(func_out)
        time_count = np.array(time_count)
        output_matrix = np.column_stack((time_count, func_out))

        # integrate
        E_cp = np.sum(self.spectr[:, 0] * self.spectr[:, 1]) / np.sum(self.spectr[:, 1])

        F = float(self.entry_f_val.get())
        intergal_tf = integrate.simps(y=output_matrix[:, 1], x=output_matrix[:, 0], dx=output_matrix[:, 0])

        koef = F / (0.23 * E_cp * intergal_tf * 1e3 * 1.6e-19)

        file_name = f'time functions/Gursa/time_{self.x.name}.tf'
        # np.savetxt(f'{pr_dir}/time functions/Gursa/time_{self.x.name}.tf', output_matrix, fmt='%-8.4g',
        #            header=f'1 pechs\n{time_count[0]} {time_count[-1]} {koef}\n{len(time_count)}', delimiter='\t',
        #            comments='')
        np.savetxt(f'{pr_dir}/time functions/Gursa/time_{self.x.name}.tf', output_matrix, fmt='%-8.4g',
                   header=f'<Номер временной функции>\n'
                          f'{source_number}\n'
                          f'<Название временной функции>\n'
                          f'time_{self.x.name}.tf\n'
                          f'<Временная фукнция t с, доля>',
                   delimiter='\t', comments='')

        if self.gursa_graphs_checkbutton_val.get() is True:
            figure = plt.Figure(figsize=(8, 4.5), dpi=65)
            ax = figure.add_subplot(111)
            ax.plot(time_count, func_out, label='Пользовательская функция')

            ax.set_xlabel('Time , s', fontsize=12)
            ax.set_ylabel('Function', fontsize=12)
            chart_type = FigureCanvasTkAgg(figure, self)

            chart_type.get_tk_widget().grid(row=2, column=8, rowspan=15, columnspan=30, padx=10)
            ax.set_title(f'{self.x.name}')
            ax.legend()

            figure1 = plt.Figure(figsize=(8, 4.5), dpi=65)
            ax = figure1.add_subplot(111)
            ax.semilogy(self.x.pe_source_graph[:, 0], self.x.pe_source_graph[:, 1])

            ax.set_xlabel('Radius between objects, km', fontsize=12)
            ax.set_ylabel('Energy part', fontsize=12)
            chart_type = FigureCanvasTkAgg(figure1, self)

            chart_type.get_tk_widget().grid(row=17, column=8, rowspan=15, columnspan=30, padx=10, pady=10)
            ax.set_title('Photon flux, $\mathdefault{1/cm^{2}}$')
            ax.legend()

    def output_dictionary(self):

        global source_number, source_list, gursa_dict

        if 'Current' in self.name or 'Sigma' in self.name:

            self.pr_dict.update({
                '<номер источника>': source_number,
                '<тип источника>': self.energy_type,
                '<название источника>': self.name,
                '<номер слоя>': self.name.split()[-1],
                '<номер слоя из>': 0,
                '<номер слоя в>': 0,
                '<амплитуда источинка в ближней зоне источника>': 0,
                '<амплитуда источинка в дальней зоне источника>': float(self.entry_f_val.get()),
                '<спектр источника>': self.spectr_dir,
                '<временная функция источинка>': time_func_dict.get(f'{self.name}'),
                '<запаздывание(0 - нет, 1 - есть)>': 1,
                '<X-координата источника>': 0,
                '<Y-координата источника>': 0,
                '<Z-координата источника>': 0,
                '<X-координата объекта>': 0,
                '<Y-координата объекта>': 0,
                '<Z-координата объекта>': 0,
                '<полярный угол поворта локальной системы координат относительно глобальной>': None,
                '<азимутальный угол поворта локальной системы координат относительно глобальной>': None,
                '<X-компонента направляющего косинуса для расчета в дальней зоне>': None,
                '<Y-компонента направляющего косинуса для расчета в дальней зоне>': None,
                '<Z-компонента направляющего косинуса для расчета в дальней зоне>': None
            })

            delete_keys = ['<номер слоя из>',
                           '<номер слоя в>',
                           '<X-координата источника>',
                           '<Y-координата источника>',
                           '<Z-координата источника>',
                           '<X-координата объекта>',
                           '<Y-координата объекта>',
                           '<Z-координата объекта>',
                           '<полярный угол поворта локальной системы координат относительно глобальной>',
                           '<азимутальный угол поворта локальной системы координат относительно глобальной>',
                           '<X-компонента направляющего косинуса для расчета в дальней зоне>',
                           '<Y-компонента направляющего косинуса для расчета в дальней зоне>',
                           '<Z-компонента направляющего косинуса для расчета в дальней зоне>',
                           '<амплитуда источинка в ближней зоне источника>'
                           ]

            for key in delete_keys:
                if key in self.pr_dict.keys():
                    self.pr_dict.pop(key)

            source_list.append(self.pr_dict)

        if 'Flu' in self.name:
            layers = []
            [layers.append(i) for i in self.name]

            self.pr_dict.update({
                '<номер источника>': source_number,
                '<тип источника>': self.energy_type,
                '<название источника>': self.name,
                '<номер слоя>': 0,
                '<номер слоя из>': layers[-2],
                '<номер слоя в>': layers[-1],
                '<амплитуда источинка в ближней зоне источника>': 0,
                '<амплитуда источинка в дальней зоне источника>': float(self.entry_f_val.get()),
                '<спектр источника>': self.spectr_dir,
                '<временная функция источинка>': time_func_dict.get(f'{self.name}'),
                '<запаздывание(0 - нет, 1 - есть)>': 1,
                '<X-координата источника>': 0,
                '<Y-координата источника>': 0,
                '<Z-координата источника>': 0,
                '<X-координата объекта>': 0,
                '<Y-координата объекта>': 0,
                '<Z-координата объекта>': 0,
                '<полярный угол поворта локальной системы координат относительно глобальной>': None,
                '<азимутальный угол поворта локальной системы координат относительно глобальной>': None,
                '<X-компонента направляющего косинуса для расчета в дальней зоне>': None,
                '<Y-компонента направляющего косинуса для расчета в дальней зоне>': None,
                '<Z-компонента направляющего косинуса для расчета в дальней зоне>': None
            })
            delete_keys = ['<номер слоя>',
                           '<X-координата источника>',
                           '<Y-координата источника>',
                           '<Z-координата источника>',
                           '<X-координата объекта>',
                           '<Y-координата объекта>',
                           '<Z-координата объекта>',
                           '<полярный угол поворта локальной системы координат относительно глобальной>',
                           '<азимутальный угол поворта локальной системы координат относительно глобальной>',
                           '<X-компонента направляющего косинуса для расчета в дальней зоне>',
                           '<Y-компонента направляющего косинуса для расчета в дальней зоне>',
                           '<Z-компонента направляющего косинуса для расчета в дальней зоне>',
                           '<амплитуда источинка в ближней зоне источника>'
                           ]

            for key in delete_keys:
                if key in self.pr_dict.keys():
                    self.pr_dict.pop(key)

            print('flu')
            source_list.append(self.pr_dict)

            # with open(rf'output dicts/{self.name}_out.txt', 'w', encoding='utf-8') as file:
            #     for item in self.pr_dict.items():
            #         file.write(f'{item[0]}\n')
            #         file.write(f'{item[1]}\n')

        if 'Gursa' in self.name:

            class_gursa = self.x
            # for class_gursa in self.gursa_dict.values():

            pr_dict = {}
            pr_dict.update({
                '<номер источника>': source_number,
                '<тип источника>': 'Gursa',
                '<название источника>': class_gursa.name,
                '<номер слоя>': 0,
                '<номер слоя из>': 0,
                '<номер слоя в>': 0,
                '<амплитуда источинка в ближней зоне источника>': class_gursa.F,
                '<амплитуда источинка в дальней зоне источника>': 0,
                '<спектр источника>': time_func_dict.get(f'{class_gursa.name}')[1],
                '<временная функция источинка>': time_func_dict.get(f'{class_gursa.name}')[0],
                '<запаздывание(0 - нет, 1 - есть)>': 0,
                '<X-координата источника>': class_gursa.M2[0],
                '<Y-координата источника>': class_gursa.M2[1],
                '<Z-координата источника>': class_gursa.M2[2],
                '<X-координата объекта>': class_gursa.M1[0],
                '<Y-координата объекта>': class_gursa.M1[1],
                '<Z-координата объекта>': class_gursa.M1[2],
                '<полярный угол поворта локальной системы координат относительно глобальной>': None,
                '<азимутальный угол поворта локальной системы координат относительно глобальной>': None,
                '<X-компонента направляющего косинуса для расчета в дальней зоне>': None,
                '<Y-компонента направляющего косинуса для расчета в дальней зоне>': None,
                '<Z-компонента направляющего косинуса для расчета в дальней зоне>': None
            })

            delete_keys = ['<номер слоя>',
                           '<номер слоя из>',
                           '<номер слоя в>',
                           '<полярный угол поворта локальной системы координат относительно глобальной>',
                           '<азимутальный угол поворта локальной системы координат относительно глобальной>',
                           '<полярный угол поворта локальной системы координат относительно глобальной>',
                           '<X-компонента направляющего косинуса для расчета в дальней зоне>',
                           '<Y-компонента направляющего косинуса для расчета в дальней зоне>',
                           '<Z-компонента направляющего косинуса для расчета в дальней зоне>',
                           '<амплитуда источинка в дальней зоне источника>'
                           ]

            for key in delete_keys:
                if key in pr_dict.keys():
                    pr_dict.pop(key)

            source_list.append(pr_dict)

        # if 'External_field' in self.name:
        #
        #     self.pr_dict.update({
        #         '< номер источника >': source_number,
        #         '< тип источника >': self.energy_type,
        #         '< название источника >': self.name,
        #         '< номер слоя >': 0,
        #         '< номер слоя из >': 0,
        #         '< номер слоя в >': 0,
        #         '< амплитуда источинка в ближней зоне источника >': 0,
        #         '< амплитуда источинка в дальней зоне источника >': 0,
        #         '< спектр источника >': self.spectr_dir,
        #         '< временная функция источинка >': time_func_dict.get(f'{self.name}'),
        #         '< запаздывание(0 - нет, 1 - есть) >': 1,
        #         '< X-координата источника >': 0,
        #         '< Y-координата источника >': 0,
        #         '< Z-координата источника >': 0,
        #         '< X-координата объекта >': 0,
        #         '< Y-координата объекта >': 0,
        #         '< Z-координата объекта >': 0,
        #         '< полярный угол поворта локальной системы координат относительно глобальной >': None,
        #         '< азимутальный угол поворта локальной системы координат относительно глобальной >': None,
        #         '< X-компонента направляющего косинуса для расчета в дальней зоне >': None,
        #         '< Y-компонента направляющего косинуса для расчета в дальней зоне >': None,
        #         '< Z-компонента направляющего косинуса для расчета в дальней зоне >': None
        #     })
        #
        #     delete_keys = ['< номер слоя из >',
        #                    '< номер слоя >',
        #                    '< номер слоя в >',
        #                    '< X-координата источника >',
        #                    '< Y-координата источника >',
        #                    '< Z-координата источника >',
        #                    '< X-координата объекта >',
        #                    '< Y-координата объекта >',
        #                    '< Z-координата объекта >',
        #                    '< полярный угол поворта локальной системы координат относительно глобальной >',
        #                    '< азимутальный угол поворта локальной системы координат относительно глобальной >',
        #                    '< X-компонента направляющего косинуса для расчета в дальней зоне >',
        #                    '< Y-компонента направляющего косинуса для расчета в дальней зоне >',
        #                    '< Z-компонента направляющего косинуса для расчета в дальней зоне >',
        #                    '< амплитуда источинка в ближней зоне источника >',
        #                    '< амплитуда источинка в дальней зоне источника >'
        #                    ]
        #
        #     for key in delete_keys:
        #         if key in self.pr_dict.keys():
        #             self.pr_dict.pop(key)
        #
        #     with open(rf'output dicts/{self.name}_out.txt', 'w', encoding='utf-8') as file:
        #         for item in self.pr_dict.items():
        #             file.write(f'{item[0]}\n')
        #             file.write(f'{item[1]}\n')
        #
        #         for item in self.external_field_values_dict.items():
        #             file.write(f'< {item[0]} >\n')
        #             file.write(f'{item[1]}\n')
        source_number += 1

    def reset(self):

        nb.destroy()
        check_folder().clear()
        time_func_dict.clear()
        main()

    def onExit(self):
        self.quit()

    def time_grid(self):
        a = DataParcer(os.path.join(f'{self.path}', check_folder().get('GRD'))).grid_parcer()
        return f'[{a[0]} : {a[-1]}]', a

    def child_parcecer_grid(self):
        return DataParcer(os.path.join(f'{self.path}', check_folder().get('GRD'))).grid_parcer()

    def value_check(self, func, time):
        for item in func:
            if not (0 <= item <= 1):
                mb.showerror('Value error', f'Значение функции {item} выходит за пределы')
        for item in time:
            if not (self.child_parcecer_grid()[0] <= item <= self.child_parcecer_grid()[-1]):
                mb.showerror('Value error', f'Значение временной функции {item} выходит за пределы')


class Gursa(tk.Toplevel):
    def __init__(self, name='Gursa_N'):
        super().__init__(root)

        self.name = name
        self.spectr = []
        self.spectr_cont = []
        self.Energy0 = []
        self.EnergyP = []
        self.spectr_path = ''
        self.Spektr_output = []
        self.calc_state = 0

        self.generate = 0
        self.generate_val = tk.StringVar()
        self.func_val = []
        self.dol_val = []
        self.entry_func = []
        self.entry_dol = []

        self.grab_set()
        self.focus()

        self.child_window()
        print(repr(self))

    # def __repr__(self):
    #     return f'Gursa n{self.gursa_count}'

    def child_window(self):
        self.title('PE source')
        self.geometry('800x300')

        rows = 0
        while rows < 30:
            self.rowconfigure(rows, weight=0, minsize=3)
            self.columnconfigure(rows, weight=0, minsize=3)
            rows += 1

        x_y_z = ['X', 'Y', 'Z']
        label_names = ['Координаты источника (км)', 'Координаты объекта (км)', 'Число ячеек сетки']
        self.entry_koord_ist_val = [tk.StringVar() for _ in range(3)]
        self.entry_koord_obj_val = [tk.StringVar() for _ in range(3)]
        self.entry_koord_ist_val[0].set('0')
        self.entry_koord_ist_val[1].set('0')
        self.entry_koord_ist_val[2].set('40')
        self.entry_koord_obj_val[0].set('0')
        self.entry_koord_obj_val[1].set('0')
        self.entry_koord_obj_val[2].set('60')
        self.entry_grid_value = tk.StringVar()
        self.entry_grid_value.set('1000')
        tk.Entry(self, textvariable=self.entry_grid_value, width=9).grid(row=3, column=1)

        for i in range(3):
            entry_koord_ist = tk.Entry(self, textvariable=self.entry_koord_ist_val[i], width=9)
            entry_koord_ist.grid(row=1, column=1 + i, padx=1, pady=2)
            tk.Label(self, text=x_y_z[i]).grid(row=0, column=1 + i)
            tk.Label(self, text=label_names[i]).grid(row=1 + i, column=0, sticky='W')
        for i in range(3):
            entry_koord_ist = tk.Entry(self, textvariable=self.entry_koord_obj_val[i], width=9)
            entry_koord_ist.grid(row=2, column=1 + i, padx=1, pady=2)

        self.button_browse_spectr = tk.Button(self, text='Browse',
                                              command=self.take_spectr, state='normal')
        self.button_browse_spectr.grid(row=1, column=5, padx=5)
        self.button_rasch = tk.Button(self, text='Calc', command=self.main, state='disabled')
        self.button_rasch.grid(row=5, column=0)

        self.button_generate = tk.Button(self, text='Сгенерировать', command=self.ent)
        self.button_generate.grid(row=5, column=3, columnspan=3)
        self.generate_entry = tk.Entry(self, textvariable=self.generate_val, width=5)
        self.generate_entry.grid(row=5, column=2)

        self.spectr_type = tk.IntVar()

        self.radio_cont = tk.Radiobutton(self, text='CONTINUOUS', variable=self.spectr_type, value=0)
        self.radio_cont.grid(row=1, column=6, sticky="W")
        radio_dis = tk.Radiobutton(self, text='DISCRETE', variable=self.spectr_type, value=1)
        radio_dis.grid(row=2, column=6, sticky="W")
        self.spectr_type.set(0)

    def take_spectr(self):
        if self.generate == 0:
            path = fd.askopenfilename(title='Выберите файл spectr',
                                      filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
            # path = 'spectr_3_49_norm_na_1.txt'
            with open(path, 'r') as file_handler:
                i = 0
                s = []
                if self.spectr_type.get() == 0:
                    for line in file_handler:
                        i += 1
                        if 'SP_TYPE=DISCRETE' in line:
                            mb.showerror('Spectr error', 'Выбран спектр DISCRETE')
                            break
                        if i < 3: continue
                        if len(line.split()) < 2:
                            # print(type(s))
                            line = line + '0'
                            s.append(line.split())
                        else:
                            s.append(line.split())

                    out = np.array(s, dtype=float)
                    self.spectr_cont = np.copy(out)
                    for i in range(len(out) - 1):
                        out[i, 0] = (out[i, 0] + out[i + 1, 0]) / 2
                        out[i, 1] = out[i + 1, 1]
                    out = np.delete(out, np.s_[-1:], 0)
                elif self.spectr_type.get() == 1:
                    for line in file_handler:
                        if 'SP_TYPE=CONTINUOUS' in line:
                            mb.showerror('Spectr error', 'Выбран спектр CONTINUOUS')
                            break
                    out = np.loadtxt(path, skiprows=2)

                self.button_rasch.configure(state='normal')
                self.spectr = out

            self.button_rasch.configure(state='normal')
            # print(self.spectr)

    def ent(self):

        if len(self.entry_func) > 0:
            for ent in self.entry_func:
                ent.destroy()
            self.entry_func.clear()

            for ent in self.entry_dol:
                ent.destroy()
            self.entry_dol.clear()

        self.func_val.clear()
        self.dol_val.clear()

        tk.Label(self, text='Energy , кЭв').grid(row=6, column=1)
        tk.Label(self, text='Доля').grid(row=6, column=2)
        self.func_val = [tk.StringVar() for _ in range(int(self.generate_val.get()))]
        self.dol_val = [tk.StringVar() for _ in range(int(self.generate_val.get()))]

        for i in range(int(self.generate_val.get())):
            self.entry_func.append(tk.Entry(self, width=9, textvariable=self.func_val[i], justify='center'))
            self.entry_func[i].grid(row=8 + i, column=1, pady=2)
            self.entry_dol.append(tk.Entry(self, width=9, textvariable=self.dol_val[i], justify='center'))
            self.entry_dol[i].grid(row=8 + i, column=2, pady=2)

        self.generate = 1

        self.button_browse_spectr.configure(state='disabled')
        self.button_rasch.configure(state='normal')

        if len(self.entry_dol) == 1:
            self.spectr_type.set(1)
            self.radio_cont.configure(state='disabled')
        else:
            self.radio_cont.configure(state='normal')

    def delta_R(self, DOT0, DOT1):
        r = ((DOT0[0] - DOT1[0]) ** 2 + (DOT0[1] - DOT1[1]) ** 2 + (DOT0[2] - DOT1[2]) ** 2) ** 0.5
        return r

    def ro_air(self, h, h0):
        ro = 1.23 * 10 ** -3 * np.exp(-(h + h0) / 7)
        return ro

    def koord(self, x1, y1, z1):
        A = np.array((x1, y1, z1), dtype=float)
        return A

    def koord_param(self, x1, x2, t):  # D1-источник  D2- короббка
        x = x1 + (x2 - x1) * t
        return x

    def main(self):

        self.M2 = self.koord(self.entry_koord_ist_val[0].get(),
                             self.entry_koord_ist_val[1].get(),
                             self.entry_koord_ist_val[2].get())
        self.M1 = self.koord(self.entry_koord_obj_val[0].get(),
                             self.entry_koord_obj_val[1].get(),
                             self.entry_koord_obj_val[2].get())
        try:
            if any([val < 0 for val in self.M2]) or any([val < 0 for val in self.M1]):
                mb.showerror('Koord error', 'Введите положительные значения')
                raise Exception
        except Exception:
            print(self.M2)
            print(self.M1)
            return print('Введите положительные значения')

        N = int(self.entry_grid_value.get())

        # Блок чтения ручной генерации
        if self.generate == 1:

            if self.spectr_type.get() == 1:

                out = np.zeros((len(self.func_val), 2), dtype=float)
                for i in range(len(self.func_val)):
                    out[i, 0] = float(self.func_val[i].get())
                    out[i, 1] = float(self.dol_val[i].get())

                self.spectr = out

            elif self.spectr_type.get() == 0:

                out = np.zeros((len(self.func_val), 2), dtype=float)
                for i in range(len(self.func_val)):
                    out[i, 0] = float(self.func_val[i].get())
                    out[i, 1] = float(self.dol_val[i].get())

                self.spectr_cont = np.copy(out)

                for i in range(len(out) - 1):
                    out[i, 0] = (out[i, 0] + out[i + 1, 0]) / 2
                    out[i, 1] = out[i + 1, 1]

                out = np.delete(out, np.s_[-1:], 0)

                self.spectr = out

        # __________________________________

        self.Energy0 = self.spectr[:, 0] * 10 ** -3  # энергия должна быть в МэВ
        self.EnergyP = self.spectr[:, 1]

        self.Spektr_output = np.zeros((len(self.Energy0), 2), dtype=float)

        # БЛОК ЧТЕНИЯ ТАБЛИЦ ПОСТОЯННЫХ
        materials_path = os.path.join(config_read()[0], 'pechs\materials')
        if os.path.exists(materials_path):
            print(f'{materials_path} exist')

        photon_values_dir = os.path.join(materials_path, 'mat-air/photon/xtbl.23')
        electron_values_dir = os.path.join(materials_path, 'mat-air/electron/xtbl.23')

        electron_values = np.loadtxt(electron_values_dir, skiprows=18)
        photon_values = np.loadtxt(photon_values_dir, skiprows=18)

        electron_values = 10 ** electron_values
        photon_values = 10 ** photon_values

        sum_dol = np.zeros((len(self.Energy0), N), dtype=float)

        for j in range(len(self.Energy0)):

            Lx = self.M1[0] - self.M2[0]
            Ly = self.M1[1] - self.M2[1]
            Lz = self.M1[2] - self.M2[2]
            dx = Lx / N
            dy = Ly / N
            dz = Lz / N
            PT = np.linspace(0, 1, N)

            R0 = ((self.M1[0] - self.M2[0]) ** 2 + (self.M1[1] - self.M2[1]) ** 2 + (
                    self.M1[2] - self.M2[2]) ** 2) ** 0.5

            X = np.zeros(N, dtype=float)
            Y = np.zeros(N, dtype=float)
            Z = np.zeros(N, dtype=float)
            R = np.zeros(N, dtype=float)
            ro = np.zeros(N, dtype=float)

            for i in range(len(X)):
                X[i] = self.koord_param(self.M2[0], self.M1[0], PT[i])
                Y[i] = self.koord_param(self.M2[1], self.M1[1], PT[i])
                Z[i] = self.koord_param(self.M2[2], self.M1[2], PT[i])
                pr_k = np.array((X[i], Y[i], Z[i]))
                R[i] = self.delta_R(self.M2, pr_k)

            for i in range(N):  # расчет плотности
                if i == 0:
                    ro[i] = self.ro_air(0, self.M2[2])
                else:
                    if self.M2[2] > self.M1[2]:
                        ro[i] = self.ro_air(0, Z[i])
                    else:
                        ro[i] = self.ro_air(Z[i] - Z[0], self.M2[2])

            Energy_reduction = np.zeros(N, dtype=float)
            lam = np.zeros(N, dtype=float)
            Energy_reduction[0] = self.EnergyP[j]
            sum_dol[j, 0] = self.EnergyP[j]

            KSI = np.interp(self.Energy0[j] * 10 ** 6, photon_values[:, 0], photon_values[:, 1])

            for i in range(N):
                lam[i] = KSI * ro[i]  # cm**2/g * g/cm**3 ------- 1/cm
            for i in range(1, N):
                Energy_reduction[i] = Energy_reduction[i - 1] * np.exp(
                    -(R[i] * 10 ** 5 - R[i - 1] * 10 ** 5) * lam[i])
                sum_dol[j, i] = Energy_reduction[i]

            self.Spektr_output[j, 1] = Energy_reduction[-1] * (4 * np.pi * (R0 * 10 ** 5) ** 2) ** -1

        sum_dol_out = sum_dol.sum(axis=0)

        for i in range(1, N):
            sum_dol_out[i] = sum_dol_out[i] * (4 * np.pi * (R[i] * 10 ** 5) ** 2) ** -1

        if self.spectr_type.get() == 1:
            type = 'DISCRETE'
        elif self.spectr_type.get() == 0:
            type = 'CONTINUOUS'

        if self.spectr_type.get() == 1:
            self.Spektr_output[:, 0] = self.Energy0 * 10 ** 3

        elif self.spectr_type.get() == 0:
            self.Spektr_output[:, 0] = self.spectr_cont[1:, 0]
            for i in range(len(self.Spektr_output) - 1, 0, -1):
                self.Spektr_output[i, 1] = self.Spektr_output[i - 1, 1]

        self.pe_source_graph = np.column_stack((R[1:], sum_dol_out[1:]))

        self.calc_state = 1

        self.destroy()

    # def name_transfer(self):
    #     if self.spectr_type.get() == 1:
    #         type = 'DISCRETE'
    #     elif self.spectr_type.get() == 0:
    #         type = 'CONTINUOUS'
    #     return type


class Calculations:

    def linear_dif(self, y1, x1, y2, x2):
        self.k = (y2 - y1) / (x2 - x1)
        self.b = y1 - (y2 - y1) * x1 / (x2 - x1)
        return self.k, self.b

    def solve(self, x, k, b):
        self.f = k * x + b
        return self.f


class DataParcer:
    def __init__(self, path):
        self.path = path

    def lay_decoder(self):
        #### .LAY DECODER
        with open(rf'{self.path}', 'r') as file:
            lines = file.readlines()
        lay_numeric = int(lines[2])
        out_lay = np.zeros((lay_numeric, 3), dtype=int)
        j = 0
        for i in range(len(lines)):
            if '<Номер, название слоя>' in lines[i]:  # 0 - номер слоя  1 - стороннй ток  2 - стро. ист.
                out_lay[j, 0] = int(lines[i + 1].split()[0])
                out_lay[j, 1] = int(lines[i + 3].split()[2])
                out_lay[j, 2] = int(lines[i + 3].split()[3])
                j += 1
        # print('.LAY  ', out_lay)
        return out_lay

    def tok_decoder(self):
        #### .TOK DECODER
        with open(rf'{self.path}', 'r') as file:
            lines_tok = file.readlines()
        out_tok = np.zeros(3, dtype=int)
        for i in range(len(lines_tok)):
            if '<Начальное поле (0-нет,1-да)>' in lines_tok[i]:
                out_tok[0] = int(lines_tok[i + 1])
            if '<Внешнее поле (0-нет,1-да)>' in lines_tok[i]:
                out_tok[1] = int(lines_tok[i + 1])
            if '<Тип задачи (0-Коши 1-Гурса>' in lines_tok[i]:
                out_tok[2] = int(lines_tok[i + 1])
            # добавить тение строки гурса
        # print('.TOK  ', out_tok)
        return out_tok

    def pl_decoder(self):
        #### .PL DECODER
        with open(rf'{self.path}', 'r') as file:
            lines_pl = file.readlines()
        for line in range(len(lines_pl)):
            if '<Количество слоев>' in lines_pl[line]:
                pl_numeric = int(lines_pl[line + 1])
                out_pl = np.zeros((pl_numeric, pl_numeric), dtype=int)

            if '<Частица номер>' in lines_pl[line]:
                for i in range(pl_numeric):
                    for j in range(len(lines_pl[line + 2 + i].split())):
                        out_pl[i, j] = int(lines_pl[line + 2 + i].split()[j])

        # print('.PL\n', out_pl)
        return out_pl

    def grid_parcer(self):
        #### .PL DECODER
        with open(rf'{self.path}', 'r') as file:
            lines = file.readlines()
        out = np.array(lines[15].split(), dtype=float)
        return out


def checker():
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
            root.destroy()

    global pr_dir
    pr_dir = os.path.abspath(config_read()[0])
    check_class = FrameGen(root, 'Check')

    if not os.path.exists(rf"{cur_dir[0]}"):
        mb.showerror('Dir error', 'Директория не существует. Укажите путь к PECHS.')
        open_button()
        print('dir not exist ', f' {cur_dir[0]}')
        cur_dir = config_read()

    if not os.path.exists(rf'{pr_dir}/time functions'):
        os.mkdir(f'{pr_dir}/time functions')
    if not os.path.exists(f'{pr_dir}/time functions/user configuration'):
        os.mkdir(os.path.join(f'{pr_dir}/time functions/user configuration'))
    if not os.path.exists(f'{pr_dir}/time functions/output dicts'):
        os.mkdir(os.path.join(f'{pr_dir}/time functions/output dicts'))

    if not os.path.exists(f'{pr_dir}/time functions/Gursa'):
        os.mkdir(os.path.join(f'{pr_dir}/time functions/Gursa'))

    if len(DataParcer(os.path.normpath(os.path.join(cur_dir[0], check_folder().get('TOK')))).tok_decoder()) > 0:
        if not os.path.exists(f'{pr_dir}/time functions/TOK'):
            os.mkdir(os.path.join(f'{pr_dir}/time functions/TOK'))

    try:
        lay_dir = os.path.join(cur_dir[0], check_folder().get('LAY'))
        DataParcer(lay_dir).lay_decoder()
    except FileNotFoundError:
        mb.showerror('Path error', 'Директория указана неверно')
        cur_dir.clear()
        open_button()
        cur_dir = config_read()
    # check_folder()
    del check_class

    return cur_dir


def main():
    global nb, time_func_dict, source_number, source_list, gursa_dict
    source_list = []
    gursa_dict = {}
    source_number = 1

    time_func_dict = {}

    cur_dir = checker()

    file_dict = check_folder()

    lay_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('LAY')))
    pl_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('PL')))
    tok_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('TOK')))
    grid_dir = os.path.normpath(os.path.join(cur_dir[0], file_dict.get('GRD')))

    nb = ttk.Notebook(root)
    nb.grid(sticky='nwse')

    LAY = DataParcer(lay_dir).lay_decoder()
    PL = DataParcer(pl_dir).pl_decoder()
    TOK = DataParcer(tok_dir).tok_decoder()

    for i in range(LAY.shape[0]):
        if LAY[i, 1] == 1:
            energy_type = 'Current'
            FrameGen(root, f'{energy_type}_layer {i}', 'Current').notebooks()
        if LAY[i, 2] == 1:
            energy_type = 'Sigma'
            FrameGen(root, f'{energy_type}_layer {i}', 'Sigma').notebooks()

    for i in range(PL.shape[0]):
        for j in range(1, PL.shape[1]):
            if PL[i, j] == 1:
                FrameGen(root, f'Flu_e{j}{i}', f'Источник электронов из {j}го в {i}й').notebooks()
    if PL[:, 0].any() == 1:
        mb.showinfo('ERROR', 'Частицы в нулевом слое!')

    if TOK[0] == 1:
        energy_type = 'Начальное поле'
        FrameGen(root, 'Initial_field', f'{energy_type}').initial_field_notebook()
    if TOK[1] == 1:
        energy_type = 'Внешнее поле'
        FrameGen(root, 'External_field', f'{energy_type}').notebooks()
    if TOK[2] == 1:
        energy_type = 'Gursa'
        FrameGen(root, 'Gursa', f'{energy_type}').notebooks()
    if TOK[2] == 0:
        energy_type = 'Koshi'
        FrameGen(root, 'Koshi', f'{energy_type}').koshi_nb()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1200x600')

    main()

    root.mainloop()
