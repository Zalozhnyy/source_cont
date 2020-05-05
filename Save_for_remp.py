import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb


# from utility import pr_dir


# class Save_remp_(tk.Toplevel):
#     def __init__(self, parent=None, data=None):
#         super().__init__(parent)
#
#         self.data = data.copy()
#
#         self.frame_exist = 0
#         self.create_list = ['lag', 'distribution', 'koord_ist']
#         self.distribution_list = ['JX', 'JY', 'JZ']
#
#         self.main_window()
#
#     def main_window(self):
#         self.title('REMP save utility')
#         self.geometry('800x300')
#         rows = 0
#         while rows < 30:
#             self.rowconfigure(rows, weight=0, minsize=3)
#             self.columnconfigure(rows, weight=0, minsize=3)
#             rows += 1
#
#         self.buttons_frame()
#
#     def buttons_frame(self):
#         self.buttons_fr = ttk.LabelFrame(self, text=f'Редактирование/сохранение')
#         self.buttons_fr.grid(row=0, column=0, rowspan=3, columnspan=3, padx=5, pady=5)
#
#         self.configure_output = tk.Button(self.buttons_fr, text='Редактировать', width=13,
#                                           command=lambda: self.param_creator(data=self.get_choice_func()))
#         self.configure_output.grid(row=0, column=0, pady=3, padx=3)
#
#         self.choice_func = ttk.Combobox(self.buttons_fr, values=[key for key in self.data.keys()], width=20,
#                                         state='normal')
#         self.choice_func.grid(row=0, column=1, pady=3, padx=3, columnspan=2)
#
#         self.button_save = tk.Button(self.buttons_fr, text='Сохранить', command=self.data_conf, width=13, )
#         self.button_save.grid(row=2, column=0, pady=3, padx=3)
#
#         self.save_file = tk.Button(self.buttons_fr, text='Создать txt', command=self.save_txt, width=13, )
#         self.save_file.grid(row=5, column=0, pady=3, padx=3)
#
#         # self.button_delete_save = tk.Button(self.buttons_fr, text='Удалить', command=self.delete_from_txt, width=13)
#         # self.button_delete_save.grid(row=1, column=0, pady=3, padx=3)
#         self.button_delete_save = tk.Button(self.buttons_fr, text='Удалить', command=self.delete_from_txt,
#                                             width=13)
#         self.button_delete_save.grid(row=1, column=0, pady=3, padx=3)
#
#         self.choice_func.set(list(self.data.keys())[0])
#         self.param_creator(data=self.get_choice_func())
#
#     def get_choice_func(self):
#         print(self.choice_func.get())
#         sub_dict = self.data.get(self.choice_func.get())
#         return sub_dict
#
#     def frame_gen(self):
#         if self.frame_exist == 1:
#             self.current_set_fr.destroy()
#             self.frame_exist = 0
#
#         self.current_set_fr = ttk.LabelFrame(self, text=f'{self.choice_func.get()}')
#         self.current_set_fr.grid(row=0, column=3, rowspan=len(self.create_list), padx=5, pady=5, sticky='NW')
#         self.frame_exist = 1
#
#     def param_creator(self, data):
#         self.frame_gen()
#
#         self.exist_labels = []
#         self.exist_entry = []
#
#         self.entry_vals = [tk.StringVar() for _ in range(len(data.keys()))]
#
#         j = 0
#         for i, key in enumerate(data.keys()):
#             self.entry_vals[i].set(f'{data.get(key)}')
#
#             if key in self.create_list:
#                 self.exist_labels.append(tk.Label(self.current_set_fr, text=f'{key}'))
#                 self.exist_labels[j].grid(row=j, column=3)
#
#                 if key == 'distribution':
#                     self.destr_cmb = ttk.Combobox(self.current_set_fr, values=[i for i in self.distribution_list],
#                                                   width=10, state='normal')
#                     self.destr_cmb.grid(row=j, column=4, pady=3, padx=3, sticky='')
#                     j += 1
#                     continue
#
#                 self.exist_entry.append(tk.Entry(self.current_set_fr, textvariable=self.entry_vals[i]))
#                 self.exist_entry[j].grid(row=j, column=4, pady=3, padx=3)
#                 j += 1
#
#     def delete_from_txt(self):
#         target = self.choice_func.get()
#         self.data.pop(target)
#
#         self.choice_func.configure(values=[key for key in self.data.keys()])
#         self.choice_func.set('')
#
#     def data_conf(self):
#         sub_dict = self.data.get(self.current_set_fr['text'])
#         for i, key in enumerate(sub_dict.keys()):
#             if key in self.create_list:
#                 if key == 'distribution':
#                     sub_dict.update({key: self.destr_cmb.get()})
#                 else:
#                     sub_dict.update({key: self.entry_vals[i].get()})
#
#     def save_txt(self):
#         out = ''
#         for item in self.data.items():
#             ldict = item[1]
#             for lkey in ldict.keys():
#                 lval = ldict.get(lkey)
#                 if lval is not None:
#
#                     # исключения по сохранению
#                     if lkey == 'source_type':
#                         out += f'{lval}\n'
#
#                     elif lkey == 'time_function':
#                         len = ldict.get(lkey)[0]
#                         time, value = ldict.get(lkey)[1], ldict.get(lkey)[2]
#                         time_fix = ''
#                         value_fix = ''
#                         for i in time:
#                             time_fix += str(i) + ' '
#                         for i in value:
#                             value_fix += str(i) + ' '
#
#                         lkey = lkey.replace('_', ' ')
#                         out += f'<{lkey}>\n{len}\n{time_fix}\n{value_fix}\n'
#
#                     else:
#                         lkey = lkey.replace('_', ' ')
#                         out += f'<{lkey}>\n{lval}\n'
#             out += '\n'
#
#         with open(f'{pr_dir()}/time functions/_remp.txt', 'w', encoding='utf-8') as file:
#             file.write(out)


class Save_remp():
    def __init__(self, data=None, path=None):
        self.data = data.copy()
        self.path = path

        self.frame_exist = 0
        self.create_list = ['lag', 'distribution', 'koord_ist']
        self.distribution_list = ['JX', 'JY', 'JZ']

        if len(self.data) == 0:
            mb.showinfo('save','Нечего сохранять!')
            return

        self.save_txt()

    def save_txt(self):
        out = ''
        for item in self.data.items():
            ldict = item[1]
            for lkey in ldict.keys():
                lval = ldict.get(lkey)
                if lval is not None:

                    # исключения по сохранению
                    if lkey == 'source_type':
                        out += f'{lval}\n'

                    elif lkey == 'time_function':
                        len = ldict.get(lkey)[0]
                        time, value = ldict.get(lkey)[1], ldict.get(lkey)[2]
                        time_fix = ''
                        value_fix = ''
                        for i in time:
                            time_fix += str(i) + ' '
                        for i in value:
                            value_fix += str(i) + ' '

                        lkey = lkey.replace('_', ' ')
                        out += f'<{lkey}>\n{len}\n{time_fix}\n{value_fix}\n'

                    else:
                        lkey = lkey.replace('_', ' ')
                        out += f'<{lkey}>\n{lval}\n'
            out += '\n'

        with open(f'{self.path}/remp_sources', 'w', encoding='utf-8') as file:
            file.write(out)

        mb.showinfo('Save', f'Сохранено в {self.path}/remp_sources')
