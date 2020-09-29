import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd
import os
import shutil


def copy_to_project(target, project_path):
    t = os.path.normpath(target)
    project_path = os.path.normpath(project_path)

    in_project = os.path.normpath(os.path.split(t)[0])
    if project_path == in_project:
        return target
    file_name = os.path.split(t)[-1]
    save_path = os.path.join(project_path, file_name)
    if file_name in os.listdir(project_path + '/'):
        ask = mb.askyesno(f'Копирование {file_name} в проект',
                          'Файл с таким названием уже есть в проекте. Перезаписать файл?\n'
                          'да - перезаписать\n'
                          'нет - переименовать')
        if ask is True:
            shutil.copyfile(t, save_path)
        elif ask is False:
            while file_name in os.listdir(project_path + '/'):
                file_name = sd.askstring('Введите имя файла', 'Введите имя файла')
                if file_name in os.listdir(project_path + '/'):
                    print('Файл уже находится в проекте. Выберите новое имя.')
            save_path = os.path.join(project_path, file_name)
            shutil.copyfile(t, save_path)
    else:
        shutil.copyfile(t, save_path)

    return save_path


class SelectParticleDialog(tk.Toplevel):
    def __init__(self, data):
        super().__init__()

        self.data = data
        self.grab_set()

        self.lb_current = None
        self.protocol("WM_DELETE_WINDOW", self.onExit)

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
        if self.lb_current is None:
            return

        self.destroy()

    def onExit(self):
        self.lb_current = None
        self.destroy()


class DeleteGSourceDialog(tk.Toplevel):
    def __init__(self, data):
        super().__init__()

        self.data = data
        self.grab_set()

        self.lb_current = None

        self.protocol("WM_DELETE_WINDOW", self.onExit)

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
        ask = mb.askyesno('Удаление', f'Вы уверены, что хотите удалить {self.lb_current}?')
        if ask is True:
            self.destroy()
        else:
            return

    def onExit(self):
        self.lb_current = None
        self.destroy()


class SelectSpectreToView(tk.Toplevel):
    def __init__(self, data):
        super().__init__()

        self.data = data
        self.grab_set()

        self.lb_current = None

        self.protocol("WM_DELETE_WINDOW", self.onExit)

        self.constructor()
        self.data_insert()

    def constructor(self):
        self.selected_data = tk.Listbox(self, height=15, width=30)
        self.selected_data.grid(row=0, column=0, rowspan=15, columnspan=2, pady=3)

        self.selected_data.bind("<<ListboxSelect>>", self.lb_get)

        self.button_choice = tk.Button(self, text='Выбрать', width=10, command=self.add)
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
        self.destroy()

    def onExit(self):
        self.lb_current = None
        self.destroy()


class FAQ(tk.Toplevel):
    def __init__(self):
        super().__init__()

        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.onExit)

        self.init_ui()

    def onExit(self):
        self.destroy()

    def init_ui(self):
        text = 'Программа служит для создания абстракций типа "Воздействие"'


class MarpleInterface(tk.Toplevel):
    def __init__(self, path):
        super().__init__()

        self.grab_set()

        self.path = path
        self.protocol("WM_DELETE_WINDOW", self.onExit)

        self.sigma_path = ''
        self.ion_path = ''

        self.initUi()

    def initUi(self):
        tk.Label(self, text='Создание источника Marple').grid(row=0, column=0, columnspan=3, sticky='NW')

        self.sigma_label_text = 'Проводимость:  '
        sigma_label = tk.Label(self, text=self.sigma_label_text)

        self.ion_label_text = 'Степень ионизации:  '
        ion_label = tk.Label(self, text=self.ion_label_text)

        sigma_label.grid(row=1, column=0, columnspan=5, sticky='NW')
        ion_label.grid(row=2, column=0, columnspan=5, sticky='NW')

        sigma_but_title = 'Выберите файл проводимости _marple'
        sigma_but = tk.Button(self, text='Выбрать проводимость', width=28,
                              command=lambda: self.__choice_file(sigma_label, 'sigma', sigma_but_title))
        sigma_but.grid(row=1, column=5, columnspan=1, sticky='NW', pady=3, padx=20)

        ion_but_title = 'Выберите файл степени ионизации _marple'
        ion_but = tk.Button(self, text='Выбрать степень ионизации', width=28,
                            command=lambda: self.__choice_file(ion_label, 'ion', ion_but_title))
        ion_but.grid(row=2, column=5, columnspan=1, sticky='NW', pady=3, padx=20)

    def onExit(self):
        if self.ion_path == '' or self.sigma_path == '':
            ask = mb.askyesno('Закрыть окно?', 'Выбраны не все файлы. Закрыть окно?')

            if ask is True:
                self.ion_path = None
                self.sigma_path = None
            if ask is False:
                return
        self.destroy()

    def __choice_file(self, label, type, title):
        distribution_file = fd.askopenfilename(title=title,
                                               initialdir=self.path,
                                               filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))

        if distribution_file == '':
            return

        distribution_file = copy_to_project(distribution_file, self.path)

        if type == 'ion':
            self.ion_path = os.path.basename(distribution_file)
            label['text'] = self.ion_label_text + f'{os.path.basename(distribution_file)}'

        elif type == 'sigma':
            self.sigma_path = os.path.basename(distribution_file)
            label['text'] = self.sigma_label_text + f'{os.path.basename(distribution_file)}'


class MicroElectronicsInterface(tk.Toplevel):
    def __init__(self, path):
        super().__init__()

        self.grab_set()

        self.path = path
        self.protocol("WM_DELETE_WINDOW", self.onExit)

        self.field78_path = ''
        self.density78_path = ''

        self.initUi()

    def initUi(self):
        tk.Label(self, text='Задание параметров для изделий микроэлектроники').grid(
            row=0, column=0, columnspan=3, sticky='NW')

        self.field78_label_text = 'Рабочее поле в изделии микроэлектроники:    '
        field78_label = tk.Label(self, text=self.field78_label_text)

        self.density78_label_text = 'Собственная концентрация электронов проводимости\nи дырок волентной зоны:   '
        density78_label = tk.Label(self, text=self.density78_label_text)

        field78_label.grid(row=1, column=0, columnspan=5, sticky='NW')
        density78_label.grid(row=2, column=0, columnspan=5, sticky='NW')

        field78_button_title = 'Выберите файл пабочего поля в изделии микроэлектроники'

        sigma_but = tk.Button(self, text='Выбрать поле', width=28,
                              command=lambda: self.__choice_file(field78_label, 'field', field78_button_title))
        sigma_but.grid(row=1, column=5, columnspan=1, sticky='NW', pady=3, padx=20)

        density78_button_title = 'Выберите файл собственной концентрации электронов проводимости и дырок волентной зоны'
        ion_but = tk.Button(self, text='Выбрать концентрацию', width=28,
                            command=lambda: self.__choice_file(density78_label, 'density', density78_button_title))
        ion_but.grid(row=2, column=5, columnspan=1, sticky='NW', pady=3, padx=20)

    def onExit(self):
        if self.density78_path == '' or self.field78_path == '':
            ask = mb.askyesno('Закрыть окно?', 'Выбраны не все файлы. Закрыть окно?')

            if ask is True:
                self.density78_path = None
                self.field78_path = None
            if ask is False:
                return
        self.destroy()

    def __choice_file(self, label, type, title):
        distribution_file = fd.askopenfilename(title=title,
                                               initialdir=self.path,
                                               filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))

        if distribution_file == '':
            return

        distribution_file = copy_to_project(distribution_file, self.path)

        if type == 'field':
            self.field78_path = os.path.basename(distribution_file)
            label['text'] = self.field78_label_text + f'{os.path.basename(distribution_file)}'

        elif type == 'density':
            self.density78_path = os.path.basename(distribution_file)
            label['text'] = self.density78_label_text + f'{os.path.basename(distribution_file)}'


class ProgressBar(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()

        self.grab_set()
        self.focus()

        self.parent = parent
        self.progress = None

        self.protocol("WM_DELETE_WINDOW", self.onExit)

        self.initUi()

    def initUi(self):
        self.progress = ttk.Progressbar(self, orient='horizontal',
                                        length=300, mode='determinate')

        self.progress.pack(fill="x")

        self.percent_text = tk.Label(self, text='0 %')
        self.percent_text.pack()

    def update_progress(self, one_step_value):
        self.progress['value'] += one_step_value
        self.percent_text['text'] = '{:d} %'.format(int(self.progress["value"]))
        self.update()

    def update_directly(self, val):
        self.progress['value'] = val
        self.percent_text['text'] = f'{self.progress["value"]} %'
        self.update()

    def onExit(self):
        self.destroy()


class ShowDuplicateSpectreNumbers(tk.Toplevel):
    def __init__(self, db):
        super().__init__()

        self.focus()
        self.grab_set()

        self.title = 'Повторяющиеся номера спектров'
        self.resizable(width=False, height=False)

        self.db = db
        self.protocol("WM_DELETE_WINDOW", self.onExit)

        self.initUi()

    def onExit(self):
        self.destroy()

    def initUi(self):
        self.sp_numbers_frame = ttk.Labelframe(self, text='Повторяющиеся номера спектров')
        self.sp_numbers_frame.pack(side='left', fill='both', padx=10)

        self.spectres_listbox = tk.Listbox(self.sp_numbers_frame)
        self.spectres_listbox.pack(side='left', fill='both')

        self.spectres_listbox.bind("<<ListboxSelect>>", self.set_sources_to_canvas, "+")

        self.sources_frame = ttk.Labelframe(self, text='Источники')
        self.sources_frame.pack(side='left', fill='both', padx=10)

        self.sources_canvas = tk.Canvas(self.sources_frame)
        self.sources_canvas.pack(side='left', fill='both')

        self.set_listbox()

    def set_listbox(self):
        for key in self.db.keys():
            if len(self.db[key]) > 1:
                self.spectres_listbox.insert(tk.END, key)

    def set_sources_to_canvas(self, event):
        key = self.spectres_listbox.get(self.spectres_listbox.curselection())

        l = self.sources_canvas.winfo_children()
        try:
            for label in l:
                label.pack_forget()
                label.destroy()
        except:
            pass

        for val in self.db[key]:
            t = '--'.join(val)
            tk.Label(self.sources_canvas, text=t).pack(fill='both')


if __name__ == '__main__':
    root = tk.Tk()

    a = MarpleInterface(r'C:\work\Test_projects\wpala')

    root.mainloop()
