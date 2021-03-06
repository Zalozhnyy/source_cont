import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd
import os
import shutil

from loguru import logger

from source_Project_reader import DataParser, SubtaskDecoder


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


@logger.catch()
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
        self.selected_data.bind("<Double-Button-1>", self.add_e)

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

    def add_e(self, event):
        if self.lb_current is None:
            return
        self.destroy()

    def onExit(self):
        self.lb_current = None
        self.destroy()


@logger.catch()
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
        self.selected_data.bind("<Double-Button-1>", self.add_e)

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

    def add_e(self, event):
        if self.lb_current is None:
            return
        self.destroy()

    def onExit(self):
        self.lb_current = None
        self.destroy()


@logger.catch()
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
        self.selected_data.bind("<Double-Button-1>", self.add_e)

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

    def add_e(self, event):
        if self.lb_current is None:
            return
        self.destroy()

    def onExit(self):
        self.lb_current = None
        self.destroy()


@logger.catch()
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


@logger.catch()
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


@logger.catch()
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


@logger.catch()
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
        except Exception:
            pass

        for val in self.db[key]:
            t = '--'.join(val)
            tk.Label(self.sources_canvas, text=t).pack(fill='both')


@logger.catch()
class SelectLagInterface(tk.Toplevel):
    def __init__(self, path, init_values=[]):
        super().__init__()

        self.path = path

        self.focus()
        self.grab_set()

        self.title = 'Направление воздействия'
        self.resizable(width=False, height=False)

        self.protocol("WM_DELETE_WINDOW", lambda: self.onExit(False))

        self._entry_vector_values = [tk.StringVar(), tk.StringVar(), tk.StringVar()]
        [self._entry_vector_values[i].set('') for i in range(3)]

        self._entry_vector = []
        self._enable_var = tk.IntVar()
        self._enable_var.set(0)

        self.vector_data = [None, None, None]
        self.enable = False

        if len(init_values) != 0:
            for i in range(len(self._entry_vector_values)):
                self._entry_vector_values[i].set(f'{init_values[i]:.4g}')
                self.vector_data[i] = float(init_values[i])

            self._restore_init_values = init_values.copy()

        self.initUi()

    def onExit(self, save=True):
        if all([i is not None for i in self.vector_data]):
            vector = (self.vector_data[0] ** 2 + self.vector_data[1] ** 2 + self.vector_data[2] ** 2) ** 0.5

            if vector > 1.001 or vector < 0.999:
                mb.showerror('Ошибка', f'Введённые значения не поохожи на единичный вектор.\n'
                                       f'Вектор равен {vector}\n\n'
                                       f'Сохранение невозможно. Введите корректные значения')
                return

        if save is True:
            self.destroy()

        elif save is False:
            ask = mb.askyesno('Сохранение', 'Сохранить данные?')

            if ask is True:
                self.destroy()

            elif ask is False:
                if self.vector_data != [None, None, None]:
                    self.vector_data = self._restore_init_values
                self.destroy()

    def initUi(self):
        labl = tk.Label(self, text='Направление воздействия')
        labl.grid(row=1, column=0, sticky='N', padx=5, pady=5, columnspan=2)

        enable = tk.Checkbutton(self, text='Включить', command=self.en_change, variable=self._enable_var,
                                onvalue=1, offvalue=0)
        enable.grid(row=1, column=2, sticky='N', padx=5, pady=5)

        find_in_pech = tk.Button(self, text='Из проекта переноса', command=self.__find_lag_in_pechs, width=22)
        find_in_pech.grid(row=1, column=3, sticky='N', padx=5, pady=5)

        find_in_pech = tk.Button(self, text='Из настроек подзадачи', command=self.__find_lag_in_subtask, width=22)
        find_in_pech.grid(row=2, column=3, sticky='N', padx=5, pady=5)

        save_exit = tk.Button(self, text='Ок', command=self.onExit, width=14)
        save_exit.grid(row=4, column=3, sticky='N', padx=5, pady=5)

        description_text = ['X', 'Y', 'Z']

        for i in range(3):
            self._entry_vector_values[i].trace('w',
                                               lambda name, index, mode, ind=i: self.__data_validation(ind))

            self._entry_vector.append(tk.Entry(self, textvariable=self._entry_vector_values[i], state='disabled',
                                               width=10, justify='center'))

        for i in range(3):
            tk.Label(self, text=description_text[i], justify='center').grid(row=2, column=i, padx=5, pady=10,
                                                                            sticky='N')
            self._entry_vector[i].grid(row=3, column=i, padx=5, pady=5, sticky='N')

            self.__data_validation(i)

    def __data_validation(self, i):
        try:
            val = float(self._entry_vector_values[i].get())

            if val == '':
                raise Exception

            self._entry_vector[i].configure(bg='#FFFFFF')
            self.vector_data[i] = val

        except Exception:
            self._entry_vector[i].configure(bg='#F08080')
            self.vector_data[i] = 0

    def __find_lag_in_pechs(self):
        pech_path = fd.askdirectory(title='Выберите директорию проекта переноса',
                                    initialdir=self.path)

        if pech_path == '':
            return

        source_path = os.path.join(pech_path, 'initials/source')
        if os.path.exists(source_path):
            lag = DataParser(pech_path).pech_check_utility(source_path)
            lag = list(map(float, lag.split()))

            self.vector_data = lag
            [self._entry_vector_values[i].set(f'{self.vector_data[i]:.4g}') for i in range(len(self.vector_data))]
            # self._enable_var.set(1)
            # self.en_change()

        else:
            mb.showerror('Ошибка', 'Не найден файл с координатами. Выберите другой способ задания координат.')

    def __find_lag_in_subtask(self):

        sub = SubtaskDecoder(self.path)
        if sub.subtask_path is None:
            mb.showerror('Подзадача', 'Файл подзадачи не найден в проекте. выберите другой способ задания координат.')
            return

        self._enable_var.set(1)
        self.en_change()

        self.vector_data = sub.get_subtask_koord_local()

        [self._entry_vector_values[i].set(f'{self.vector_data[i]:.4g}') for i in range(len(self.vector_data))]

    def en_change(self):
        state = self._enable_var.get()

        if state == 1:
            [self._entry_vector[i].configure(state='normal') for i in range(3)]
            for i in range(3):
                self.vector_data[i] = float(self._entry_vector_values[i].get())
        if state == 0:
            [self._entry_vector[i].configure(state='disabled') for i in range(3)]
            [self._entry_vector_values[i].set('0') for i in range(3)]
            self.vector_data = [None, None, None]


@logger.catch()
class MarpleElectronicsInterface(tk.Toplevel):
    def __init__(self, path, label_1, label_2, title_label, set_starter_items: tuple = (None, None)):
        super().__init__()

        self.grab_set()

        self.path = path
        self.protocol("WM_DELETE_WINDOW", self.onExit)

        if all([i is not None for i in set_starter_items]):
            self.first_item, self.second_item = set_starter_items
        else:
            self.first_item = 'Файл не выбран'
            self.second_item = 'Файл не выбран'

        self.first_item_label = label_1
        self.second_item_label = label_2
        self.title_label = title_label

        self.initUi()

    def initUi(self):
        row = 0
        tk.Label(self, text=self.title_label).grid(row=row, column=0, columnspan=3, sticky='NW')

        row += 1

        first_item_frame = ttk.Labelframe(self, text=self.first_item_label)
        first_item_frame.grid(row=1)

        self.first_item = tk.Label(first_item_frame, text=self.first_item)
        self.first_item.grid(row=row, column=0, columnspan=2, sticky='NWSE', padx=30, pady=5)

        item_1_add_button = tk.Button(first_item_frame, text='Выбрать файл',
                                      command=lambda: self.choice_file(self.first_item))
        # item_1_clear_button = tk.Button(first_item_frame, text='Удалить',
        #                                 command=lambda: self.delete_choice(self.first_item))

        item_1_add_button.grid(row=row, column=2, sticky='NW', padx=3)
        # item_1_clear_button.grid(row=row, column=3, sticky='NW', padx=3)
        row += 1

        second_item_frame = ttk.Labelframe(self, text=self.second_item_label)
        second_item_frame.grid(row=2)

        self.second_item = tk.Label(second_item_frame, text=self.second_item)
        self.second_item.grid(row=row, column=0, columnspan=2, sticky='NWSE', padx=30, pady=5)

        item_2_add_button = tk.Button(second_item_frame, text='Выбрать файл',
                                      command=lambda: self.choice_file(self.second_item))
        # item_2_clear_button = tk.Button(second_item_frame, text='Удалить',
        #                                 command=lambda: self.delete_choice(self.second_item))

        item_2_add_button.grid(row=row, column=2, sticky='NW', padx=3)
        # item_2_clear_button.grid(row=row, column=3, sticky='NW', padx=3)
        row += 1

        configure_button = tk.Button(self, text='Редактировать', command=self.open_notepad)
        configure_button.grid(row=1 , column=2, columnspan=3, pady=5, padx=30)

    def onExit(self):
        return_tuple = [self.first_item['text'], self.second_item['text']]

        if '' in return_tuple or 'Файл не выбран' in return_tuple:
            ask = mb.askyesno('Закрыть окно?', 'Выбраны не все файлы. Закрыть окно?')

            if ask is True:
                if return_tuple[0] == 'Файл не выбран':
                    return_tuple[0] = None
                if return_tuple[1] == 'Файл не выбран':
                    return_tuple[1] = None
            if ask is False:
                return

        self.first_item = return_tuple[0]
        self.second_item = return_tuple[1]
        self.destroy()

    def delete_choice(self, item):
        item['text'] = 'Файл не выбран'

    def choice_file(self, item):
        distribution_file = fd.askopenfilename(title='Выберите файл',
                                               initialdir=self.path,
                                               filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))

        if distribution_file == '':
            return

        distribution_file = copy_to_project(distribution_file, self.path)
        item['text'] = os.path.split(distribution_file)[-1]

    def open_notepad(self):
        if self.first_item == 'Файл не выбран' and self.second_item == 'Файл не выбран':
            return
        if type(self.first_item) is not str:
            return_tuple = (self.first_item['text'], self.second_item['text'])
        else:
            return

        select_to_view = SelectSpectreToView([i for i in return_tuple if i != 'Файл не выбран'])
        self.wait_window(select_to_view)

        file = select_to_view.lb_current
        select_to_view.destroy()

        self.open_notepad_with_chosen_file(file)

    def open_notepad_with_chosen_file(self, f):
        file = os.path.join(self.path, f)
        osCommandString = f"notepad.exe {file}"
        os.system(osCommandString)



if __name__ == '__main__':
    root = tk.Tk()

    path = r'C:\Work\Test_projects\template_faraday'
    a = MarpleElectronicsInterface(path, 'place_holder1', 'place_holder2', 'place_holder3')

    root.mainloop()
