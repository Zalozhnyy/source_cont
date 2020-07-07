import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd


class SelectParticleDialog(tk.Toplevel):
    def __init__(self, data):
        super().__init__()

        self.data = data
        self.grab_set()

        self.lb_current = None

        self.constructor()
        self.data_insert()

    def constructor(self):
        self.selected_data = tk.Listbox(self, height=15, width=30)
        self.selected_data.grid(row=0, column=0, rowspan=15, columnspan=2, pady=3)

        self.selected_data.bind("<<ListboxSelect>>", self.lb_get)

        self.button_choice = tk.Button(self, text='Добавить', width=10, command=self.add)
        self.button_choice.grid(row=3, column=2, padx=3)

    def data_insert(self):
        for i, d in enumerate(self.data):
            self.selected_data.insert(i, d)

    def lb_get(self, event):
        index = event.widget.curselection()[0]
        self.lb_current = self.selected_data.get(index)

    def add(self):
        self.destroy()


class DeleteGSourceDialog(tk.Toplevel):
    def __init__(self, data):
        super().__init__()

        self.data = data
        self.grab_set()

        self.lb_current = None

        self.constructor()
        self.data_insert()

    def constructor(self):
        self.selected_data = tk.Listbox(self, height=15, width=30)
        self.selected_data.grid(row=0, column=0, rowspan=15, columnspan=2, pady=3)

        self.selected_data.bind("<<ListboxSelect>>", self.lb_get)

        self.button_choice = tk.Button(self, text='Удалить', width=10, command=self.add)
        self.button_choice.grid(row=3, column=2, padx=3)

    def data_insert(self):
        for i, d in enumerate(self.data):
            self.selected_data.insert(i, d)

    def lb_get(self, event):
        index = event.widget.curselection()[0]
        self.lb_current = self.selected_data.get(index)

    def add(self):
        if self.lb_current is None:
            return
        ask = mb.askyesno('Удаление',f'Вы уверены, что хотите удалить {self.lb_current}?')
        if ask is True:
            self.destroy()
        else:
            return

