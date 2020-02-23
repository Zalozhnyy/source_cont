import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import os
import numpy as np
import matplotlib.pyplot as plt


def config_read():
    with open(r"entry_data/config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line)
    return cur_dir


def open_button():
    filename = fd.askdirectory()
    handle = open(r"entry_data/config.txt", "w", encoding='utf-8')
    handle.write(filename)
    handle.close()

    with open(r"entry_data/config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line)
    if len(cur_dir) < 1:
        mb.showerror('Error', 'Путь не выбран')
    else:
        mb.showinfo('Info', 'Путь сохранён.')
    print(cur_dir[0])


class FrameGen(tk.Frame):
    def __init__(self, parent, name='Title', energy_type='Название типа энергии'):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.name = name
        self.energy_type = energy_type
        self.__konstr()

        self.cell_numeric = tk.StringVar()
        self.func_entry_vel = []
        self.time_entry_vel = []
        self.func_list = []
        self.time_list = []

    def __konstr(self):
        self.parent.title("PECH UTILITY")
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Путь к PECHS", command=open_button)
        filemenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="Файл", menu=filemenu)

    def onExit(self):
        self.quit()

    def notebooks(self):
        nb.add(self, text=f"{self.name}")
        label_name_energy = tk.Label(self, text=f'{self.energy_type}')
        label_name_energy.grid(row=3, column=0, columnspan=5)
        label_func = tk.Label(self, text='value')
        label_func.grid(row=4, column=0, padx=2, pady=10)
        label_time = tk.Label(self, text='time')
        label_time.grid(row=4, column=1, padx=2, pady=10)

        button_browse = tk.Button(self, width=10, text='Load', command=self.ent_load)
        button_browse.grid(row=1, column=10)
        button_save = tk.Button(self, width=10, text='Save', command=self.time_save)
        button_save.grid(row=2, column=10)
        entry_generate_value = tk.Entry(self, width=6, textvariable=self.cell_numeric)
        entry_generate_value.grid(row=3, column=11, padx=5)
        button_generate = tk.Button(self, width=10, text='Generate', command=self.ent)
        button_generate.grid(row=3, column=10)
        button_read_gen = tk.Button(self, width=10, text='Read', command=self.get)
        button_read_gen.grid(row=4, column=10)

    def ent(self):
        self.func_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric.get()))]
        self.time_entry_vel = [tk.StringVar() for _ in range(int(self.cell_numeric.get()))]
        for i in range(int(self.cell_numeric.get())):
            entry_func = tk.Entry(self, width=9, textvariable=self.func_entry_vel[i])
            entry_func.grid(row=5 + i, column=0, padx=10, pady=1)
            entry_time = tk.Entry(self, width=9, textvariable=self.time_entry_vel[i])
            entry_time.grid(row=5 + i, column=1, padx=10, pady=1)

        entry_time = tk.Label(self, width=9, text=f'{self.time_grid()}')
        entry_time.grid(row=5 + int(self.cell_numeric.get()) + 1, column=1, padx=10, pady=1)
        entry_func = tk.Label(self, width=9, text='[0 : 1]')
        entry_func.grid(row=5 + int(self.cell_numeric.get()) + 1, column=0, padx=10, pady=1)

    def ent_load(self):
        with open(rf'time functions/{self.name}.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        print(lines)

        for word in lines[0].split():
            self.func_entry_vel.append(float(word))
        for word in lines[1].split():
            self.time_entry_vel.append(float(word))
        print('func = ', self.func_entry_vel)
        print('time = ', self.time_entry_vel)

        entr_utility_func = [tk.StringVar() for _ in range(len(self.func_entry_vel))]
        entr_utility_time = [tk.StringVar() for _ in range(len(self.func_entry_vel))]
        for i in range(len(self.func_entry_vel)):
            entry_func = tk.Entry(self, width=9, justify='center', textvariable=entr_utility_func[i])
            entry_func.grid(row=5 + i, column=0, padx=10, pady=1)
            entr_utility_func[i].set('{:.4g}'.format(self.func_entry_vel[i]))
            self.func_entry_vel[i] = entr_utility_func[i]
            # print(f'{i} ', type(entr_utility_func[i]), entr_utility_func[i])

        for i in range(len(self.time_entry_vel)):
            entry_time = tk.Entry(self, width=9, justify='center', textvariable=entr_utility_time[i])
            entry_time.grid(row=5 + i, column=1, padx=10, pady=1)
            entr_utility_time[i].set('{:.4g}'.format(self.time_entry_vel[i]))
            self.time_entry_vel[i] = entr_utility_time[i]

        entry_time = tk.Label(self, width=9, text=f'{self.time_grid()}')
        entry_time.grid(row=5 + len(self.time_entry_vel) + 1, column=1, padx=10, pady=1)
        entry_func = tk.Label(self, width=9, text='[0 : 1]')
        entry_func.grid(row=5 + len(self.func_entry_vel) + 1, column=0, padx=10, pady=1)

        if len(self.func_entry_vel) != len(self.time_entry_vel):
            mb.showerror('Load error', 'Размерности не совпадают')
            self.onExit()

    def get(self):

        print('get', type(self.func_entry_vel[0]))
        self.func_list.clear()
        self.time_list.clear()

        for i in self.func_entry_vel:
            self.func_list.append(float(i.get()))
        for i in self.time_entry_vel:
            self.time_list.append(float(i.get()))

        self.value_check(func=self.func_list, time=self.time_list)

        print('time = ', self.time_list)
        print('func = ', self.func_list)

    def time_save(self):
        with open(rf'time functions/{self.name}.txt', 'w', encoding='utf-8') as file:
            for i in self.func_list:
                file.write(f'{i} ')
            file.write('\n')
            for i in self.time_list:
                file.write(f'{i} ')

    def time_grid(self):
        a = DataParcer('entry_data/KUVSH.GRD').grid_parcer()
        return f'[{a[0]} : {a[-1]}]'

    def child_parcecer_grid(self):
        return DataParcer('entry_data/KUVSH.GRD').grid_parcer()

    def value_check(self, func, time):
        for item in func:
            if not (0 <= item <= 1):
                mb.showerror('Value error', 'Значение функции выходит за пределы')
        for item in time:
            if not (self.child_parcecer_grid()[0] <= item <= self.child_parcecer_grid()[-1]):
                mb.showerror('Value error', 'Временная функция выходит за пределы')


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
        out_tok = np.zeros(2, dtype=int)
        for i in range(len(lines_tok)):
            if '<Начальное поле (0-нет,1-да)>' in lines_tok[i]:
                out_tok[0] = int(lines_tok[i + 1])
            if '<Внешнее поле (0-нет,1-да)>' in lines_tok[i]:
                out_tok[1] = int(lines_tok[i + 1])
        # print('.TOK  ', out_tok)
        return out_tok

    def pl_decoder(self):
        #### .PL DECODER
        with open(rf'{self.path}', 'r') as file:
            lines_pl = file.readlines()
        for i in range(len(lines_pl)):
            if '<Количество слоев>' in lines_pl[i]:
                pl_numeric = int(lines_pl[i + 1])
                out_pl = np.zeros((pl_numeric, pl_numeric), dtype=int)

            if '<Частица номер>' in lines_pl[i]:
                for k in range(pl_numeric):
                    out_pl[k, 0] = int(lines_pl[i + 2 + k].split()[0])
                    out_pl[k, 1] = int(lines_pl[i + 2 + k].split()[1])
                    out_pl[k, 2] = int(lines_pl[i + 2 + k].split()[2])
                    out_pl[k, 3] = int(lines_pl[i + 2 + k].split()[3])
                    out_pl[k, 4] = int(lines_pl[i + 2 + k].split()[4])
                    out_pl[k, 5] = int(lines_pl[i + 2 + k].split()[5])
        # print('.PL\n', out_pl)
        return out_pl

    def grid_parcer(self):
        #### .PL DECODER
        with open(rf'{self.path}', 'r') as file:
            lines = file.readlines()
        out = np.array(lines[15].split(), dtype=float)
        return out


def main():
    global nb
    if os.path.exists(r"entry_data/config.txt"):
        print('config exist')
    else:
        open_button()
    cur_dir = config_read()

    if len(cur_dir) == 0:
        open_button()
        cur_dir = config_read()

    if not os.path.exists(rf"{cur_dir[0]}"):
        mb.showerror('Dir error', 'Директория не существует. Укажите путь к PECHS.')
        open_button()
        print('config exist ', f' {cur_dir[0]}')
        cur_dir = config_read()

    if not os.path.exists(r'time functions'):
        os.mkdir('time functions')

    lay_dir = os.path.join(cur_dir[0], 'entry_data/KUVSH.LAY')
    pl_dir = os.path.join(cur_dir[0], 'entry_data/KUVSH.PL')
    tok_dir = os.path.join(cur_dir[0], 'entry_data/KUVSH.TOK')
    grid_dir = os.path.join(cur_dir[0], 'entry_data/KUVSH.GRD')
    # print('TOK\n',DataParcer(tok_dir).tok_decoder())
    # print('LAY\n', DataParcer(lay_dir).lay_decoder())
    # print('PL\n', DataParcer(pl_dir).pl_decoder())

    # print('NON zero PL\n', np.nonzero(DataParcer(pl_dir).pl_decoder()))
    # print('Count non zero PL  = ', np.count_nonzero(DataParcer(pl_dir).pl_decoder()))
    # print('Count non zero LAY = ', np.count_nonzero(DataParcer(lay_dir).lay_decoder()[:, 1:]))
    # print('Count non zero TOK = ', np.count_nonzero(DataParcer(tok_dir).tok_decoder()))

    # books_pl = np.count_nonzero(DataParcer(pl_dir).pl_decoder())
    # books_tok = np.count_nonzero(DataParcer(tok_dir).tok_decoder())
    # books_lay = np.count_nonzero(DataParcer(lay_dir).lay_decoder()[:, 1:])
    # books_count = sum((np.count_nonzero(DataParcer(pl_dir).pl_decoder()),
    #                    np.count_nonzero(DataParcer(tok_dir).tok_decoder()),
    #                    np.count_nonzero(DataParcer(lay_dir).lay_decoder()[:, 1:])))
    # print('sum = ', books_count)
    # a = np.nonzero(DataParcer(pl_dir).pl_decoder())

    print(DataParcer(grid_dir).grid_parcer().shape)
    print(FrameGen(root).time_grid())
    nb = ttk.Notebook(root)
    nb.grid(row=5, column=0, columnspan=10, rowspan=10)
    LAY = DataParcer(lay_dir).lay_decoder()
    PL = DataParcer(pl_dir).pl_decoder()
    TOK = DataParcer(tok_dir).tok_decoder()
    for i in range(LAY.shape[0]):
        if LAY[i, 1] == 1:
            energy_type = 'Стор. ток'
            FrameGen(root, f'Слой № {i}, {energy_type}', 'Сторонний ток').notebooks()
        if LAY[i, 2] == 1:
            energy_type = 'Стор.ист.втор.эл.'
            FrameGen(root, f'Слой № {i}, {energy_type}', 'Стор. источник втор. эл.').notebooks()

    for i in range(PL.shape[0]):
        for j in range(1, PL.shape[1]):
            if PL[i, j] == 1:
                FrameGen(root, 'PL', f'Источник электронов из {j}го в {i}й').notebooks()
    if PL[:, 0].any() == 1:
        mb.showerror('ERROR', 'Частицы в нулевом слое!')

    if TOK[0] == 1:
        energy_type = 'Начальное поле'
        FrameGen(root, 'TOK', f'{energy_type}').notebooks()
    if TOK[1] == 1:
        energy_type = 'Внешнее поле'
        FrameGen(root, 'TOK', f'{energy_type}').notebooks()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x600+300+200')

    main()

    root.mainloop()
