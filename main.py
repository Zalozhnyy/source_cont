import tkinter as tk
from tkinter import ttk


class Frame_gen(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.konstr()

    def konstr(self):
        mainmenu = tk.Menu(root)
        root.config(menu=mainmenu)

        filemenu = tk.Menu(mainmenu, tearoff=0)
        filemenu.add_command(label="Открыть...")
        filemenu.add_command(label="Сохранить...")

        mainmenu.add_cascade(label="Файл", menu=filemenu)

    def ent(self):
        main_menu = tk.Menu(root)

        main_menu.add_command(label='Файл')
        main_menu.add_command(label='Справка')
        nb.add(self, text="1st")

        label_name_energy = tk.Label(self, text='Название вида энергии')
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


if __name__ == '__main__':
    root = tk.Tk()
    main_menu = tk.Menu(root)

    main_menu.add_command(label='Файл')
    main_menu.add_command(label='Справка')
    Frame_gen(root)
    nb = ttk.Notebook(root)
    nb.grid(row=5, column=0, columnspan=10, rowspan=10)

    for i in range(10):
        Frame_gen(root).ent()

        # nb.add(tab, text="1st")
        # lbl = tk.Label(tab, text='Название вида энергии')
        # lbl.grid(row=1, column=0,columnspan=5)
        #
        # for i in range(5):
        #     entry_func = tk.Entry(tab,width=8)
        #     entry_func.grid(row=5 + i, column=0,padx=2, pady=1)
        #     entry_time = tk.Entry(tab,width=8)
        #     entry_time.grid(row=5 + i, column=1,padx=2, pady=1)

    root.title('example')
    root.geometry("650x450+300+200")

    root.mainloop()
