import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

import os
import numpy as np
from numpy import exp, sin, cos, tan, log10
from numpy import log as ln

from utility import config_read, check_folder, pr_dir, Calculations, source_list, time_func_dict
from Project_reader import DataParcer


def timef_global_save():
    # global time_func_dict
    with open(f'{pr_dir()}/time functions/time functions list.txt', 'w', encoding='utf-8') as file:

        for item in time_func_dict.items():
            if type(item) is not list:
                file.write(f'{item[0]} = {item[1]}\n')
            else:
                for i in item:
                    file.write(f'{i[0]} = {i[1]}\n')

        mb.showinfo('Save', 'Сохранено в time functions list.txt')

        for out_dict in source_list:
            name = out_dict.get('<название источника>')
            with open(rf'{pr_dir()}/time functions/output dicts/{name}_out.txt', 'w', encoding='utf-8') as file:
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
    def __init__(self, parent, name='Title', energy_type='Название типа энергии'):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.name = name
        self.energy_type = energy_type

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

    def _notebooks(self):

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
                                               initialdir=rf'{pr_dir()}/time functions/user configuration').split(
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

        self.add_button = tk.Button(self, width=6, text='add cell', state='disabled',
                                    command=lambda: self.add_entry())
        self.del_button = tk.Button(self, width=6, text='del cell', state='disabled',
                                    command=lambda: self.delete_entry())
        self.add_button.grid(row=1, column=0, sticky='WS')
        self.del_button.grid(row=1, column=1, sticky='WS')

    def _konstr(self):
        self.parent.title("Sources")
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        self.filemenu = tk.Menu(menubar, tearoff=0)
        # self.filemenu.add_command(label="Reset", command=lambda: self.reset(self.parent))
        self.filemenu.add_command(label="Global save", command=timef_global_save)
        self.filemenu.add_command(label="Очистить timefunctions", command=tf_global_del)

        menubar.add_cascade(label="Файл", menu=self.filemenu)
        # menubar.add_command(label="test", command=lambda: print(len(source_list)))

    def ent(self):
        self.entry_func.clear()
        self.entry_time.clear()
        self.func_entry_vel.clear()
        self.time_entry_vel.clear()

        self.func_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric.get()))]
        self.time_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric.get()))]
        for i in range(int(self.cell_numeric.get())):
            self.entry_time.append(tk.Entry(self, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=7 + i, column=0, pady=3, padx=2)
            self.entry_func.append(tk.Entry(self, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=7 + i, column=1, pady=3, padx=2)

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

    def ent_load(self, path):
        with open(rf'{pr_dir()}/time functions/user configuration/{path}', 'r', encoding='utf-8') as file:
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
            self.entry_time.append(tk.Entry(self, width=15, textvariable=entr_utility_time[i], justify='center'))
            self.entry_time[i].grid(row=7 + i, column=0, pady=3, padx=2)
            entr_utility_time[i].set('{:.4g}'.format(self.time_entry_vel[i]))
            self.time_entry_vel[i] = entr_utility_time[i]

            self.entry_func.append(tk.Entry(self, width=15, textvariable=entr_utility_func[i], justify='center'))
            self.entry_func[i].grid(row=7 + i, column=1, pady=3, padx=2)
            entr_utility_func[i].set('{:.4g}'.format(self.func_entry_vel[i]))
            self.func_entry_vel[i] = entr_utility_func[i]
            # print(f'{i} ', type(entr_utility_func[i]), entr_utility_func[i])

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
            self.entry_func.append(tk.Entry(self, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=7 + i, column=1, pady=3, padx=2)
            self.entry_time.append(tk.Entry(self, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=7 + i, column=0, pady=3, padx=2)

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
            self.entry_func.append(tk.Entry(self, width=15, textvariable=self.func_entry_vel[i], justify='center'))
            self.entry_func[i].grid(row=7 + i, column=1, pady=3, padx=2)
            self.entry_time.append(tk.Entry(self, width=15, textvariable=self.time_entry_vel[i], justify='center'))
            self.entry_time[i].grid(row=7 + i, column=0, pady=3, padx=2)

        self.entry_time_label.grid_configure(row=len(self.func_entry_vel) + 2 + 7)
        self.entry_func_label.grid_configure(row=len(self.func_entry_vel) + 2 + 7)

        self.obriv_tf_lavel.grid_configure(row=len(self.func_entry_vel) + 2 + 8)
        self.entry_time_fix.grid_configure(row=len(self.func_entry_vel) + 2 + 8)

        self.button_calculate.configure(state='disabled')

    def get(self):

        # print('get', type(self.func_entry_vel[0]))
        self.func_list.clear()
        self.time_list.clear()

        for j in self.time_entry_vel:
            self.time_list.append(j.get())

        for x, j in enumerate(self.func_entry_vel):
            if 't' in j.get():      # если есть t в строке, то заменяем это t на значение entry time с тем же индексом
                string = j.get()
                fixed_string = string.replace('t', f'{self.time_list[x]}')
                self.func_list.append(fixed_string)
            else:
                self.func_list.append(j.get())

        exeption_list = ['exp', '(', ')', '*', '**', '/']

        for x, i in enumerate(self.func_list):
            if any([e in i for e in exeption_list]):
                self.func_list = self.eval_transformation(self.func_list, self.func_entry_vel)
                break
            else:
                try:
                    self.func_list[x] = float(self.func_entry_vel[x].get())
                except ValueError:
                    mb.showerror('Value error', f'{self.func_entry_vel[x].get()} не является числом')
                    return print(f'{self.func_entry_vel[x].get()} не является числом')

        for x, i in enumerate(self.time_list):
            if any([e in i for e in exeption_list]):
                self.time_list = self.eval_transformation(self.time_list, self.time_entry_vel)
                break
            else:
                try:
                    self.time_list[x] = float(self.time_entry_vel[x].get())
                except ValueError:
                    mb.showerror('Value error', f'{self.time_entry_vel[x].get()} не является числом')
                    return print(f'{self.time_entry_vel[x].get()} не является числом')
        print('time = ', self.time_list)
        print('func = ', self.func_list)

        self.value_check(func=self.func_list, time=self.time_list)

    def eval_transformation(self, arg, replace):
        for x, i in enumerate(replace):
            if 't' in i.get():
                string = i.get()
                fixed_string = string.replace('t', f'{self.time_list[x]}')
                arg[x] = eval(fixed_string)
                replace[x].set('{:.4g}'.format(eval(fixed_string)))
            else:
                arg[x] = eval(i.get())
                replace[x].set('{:.4g}'.format(eval(i.get())))
        return arg

    def time_save(self):

        save_dir = fd.asksaveasfilename(title='Назовите файл', filetypes=(("dtf files", "*.dtf"), ("All files", "*.*"))
                                        , defaultextension=("dtf files", "*.dtf"),
                                        initialdir=rf'{pr_dir()}/time functions/user configuration')
        with open(save_dir, 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            save_dir_inf = save_dir.split('/')[-1]
            mb.showinfo('Save', f'Сохранено в time functions/user configuration/{save_dir_inf}')

    def time_save_def(self):
        with open(rf'{pr_dir()}/time functions/user configuration/default.dtf', 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')
            mb.showinfo('Save default',
                        f'Сохранено стандартной в time functions/user configuration/default.dtf')

    def time_grid(self):
        a = DataParcer(os.path.join(f'{self.path}', check_folder().get('GRD'))).grid_parcer()
        return f'[{a[0]} : {a[-1]}]', a

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

    def value_check(self, func, time):
        for item in func:
            if not (0 <= item <= 1):
                mb.showerror('Value error', f'Значение функции {item} выходит за пределы')
        for item in time:
            if not (self.child_parcecer_grid()[0] <= item <= self.child_parcecer_grid()[-1]):
                mb.showerror('Value error', f'Значение временной функции {item} выходит за пределы')

    def child_parcecer_grid(self):
        return DataParcer(os.path.join(f'{self.path}', check_folder().get('GRD'))).grid_parcer()

    def onExit(self):
        self.quit()
