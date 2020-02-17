import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import os
import numpy as np
import matplotlib.pyplot as plt


def open_button():
    filename = fd.askdirectory()
    handle = open(r"config.txt", "w", encoding='utf-8')
    handle.write(filename)
    handle.close()

    with open(r"config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line)
    if len(cur_dir) < 1:
        mb.showerror('Error', 'Путь не выбран')
    else:
        mb.showinfo('Info', 'Путь сохранён.')
    print(cur_dir)


class FrameGen(tk.Frame):
    def __init__(self, parent, name='Title', energy_type='Название типа энергии'):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.name = name
        self.energy_type = energy_type
        self.__konstr()

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

    def ent(self):
        nb.add(self, text=f"{self.name}")

        label_name_energy = tk.Label(self, text=f'{self.energy_type}')
        label_name_energy.grid(row=3, column=0, columnspan=5)
        label_func = tk.Label(self, text='value')
        label_func.grid(row=4, column=0, padx=2, pady=10)
        label_time = tk.Label(self, text='time')
        label_time.grid(row=4, column=1, padx=2, pady=10)

        button_browse = tk.Button(self, width=7, text='Browse')
        button_browse.grid(row=1, column=10)
        button_save = tk.Button(self, width=7, text='Save')
        button_save.grid(row=2, column=10)

        for i in range(5):
            entry_func = tk.Entry(self, width=8)
            entry_func.grid(row=5 + i, column=0, padx=2, pady=1)
            entry_time = tk.Entry(self, width=8)
            entry_time.grid(row=5 + i, column=1, padx=2, pady=1)


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


def main():
    global nb
    root = tk.Tk()
    root.geometry('650x450+300+200')
    with open(r"config.txt", 'r', encoding='utf-8') as g:
        cur_dir = []
        for line in g:
            cur_dir.append(line)
    lay_dir = os.path.join(cur_dir[0], 'entry_data/KUVSH.LAY')
    pl_dir = os.path.join(cur_dir[0], 'entry_data/KUVSH.PL')
    tok_dir = os.path.join(cur_dir[0], 'entry_data/KUVSH.TOK')
    # print('TOK\n',DataParcer(tok_dir).tok_decoder())
    # print('LAY\n', DataParcer(lay_dir).lay_decoder())
    print('PL\n', DataParcer(pl_dir).pl_decoder())

    # print('NON zero PL\n', np.nonzero(DataParcer(pl_dir).pl_decoder()))
    # print('Count non zero PL  = ', np.count_nonzero(DataParcer(pl_dir).pl_decoder()))
    print('Count non zero LAY = ', np.count_nonzero(DataParcer(lay_dir).lay_decoder()[:, 1:]))
    # print('Count non zero TOK = ', np.count_nonzero(DataParcer(tok_dir).tok_decoder()))

    books_pl = np.count_nonzero(DataParcer(pl_dir).pl_decoder())
    books_tok = np.count_nonzero(DataParcer(tok_dir).tok_decoder())
    books_lay = np.count_nonzero(DataParcer(lay_dir).lay_decoder()[:, 1:])
    books_count = sum((np.count_nonzero(DataParcer(pl_dir).pl_decoder()),
                       np.count_nonzero(DataParcer(tok_dir).tok_decoder()),
                       np.count_nonzero(DataParcer(lay_dir).lay_decoder()[:, 1:])))
    print('sum = ', books_count)
    a = np.nonzero(DataParcer(pl_dir).pl_decoder())

    # FrameGen(root).konstr()
    nb = ttk.Notebook(root)
    nb.grid(row=5, column=0, columnspan=10, rowspan=10)
    LAY = DataParcer(lay_dir).lay_decoder()
    PL = DataParcer(pl_dir).pl_decoder()
    for i in range(LAY.shape[0]):
        if LAY[i, 1] == 1:
            energy_type = 'Стор. ток'
            FrameGen(root, f'Слой № {i}, {energy_type}', 'Сторонний ток').ent()
        if LAY[i, 2] == 1:
            energy_type = 'Стор.ист.втор.эл.'
            FrameGen(root, f'Слой № {i}, {energy_type}', 'Стор. источник втор. эл.').ent()

    for i in range(PL.shape[0]):
        for j in range(PL.shape[1]):
            if PL[i, j] == 1:
                FrameGen(root, 'PL', f'Из {j}го в {i}й').ent()
    if PL[0, :].any() == 1:
        mb.showerror('ERROR', 'Частицы в нулевом слое!')



    root.mainloop()


if __name__ == '__main__':
    main()
