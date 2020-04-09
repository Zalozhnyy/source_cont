import tkinter as tk
from tkinter import ttk

from utility import pr_dir


class Save_remp(tk.Toplevel):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)

        self.data = data

        self.frame_exist = 0
        self.create_list = ['lag', 'distribution', 'koord_ist']

        self.main_window()

    def main_window(self):
        self.title('REMP save utility')
        self.geometry('800x300')
        rows = 0
        while rows < 30:
            self.rowconfigure(rows, weight=0, minsize=3)
            self.columnconfigure(rows, weight=0, minsize=3)
            rows += 1

        tk.Button(self, text='create', command=lambda: self.param_creator(data=self.get_choice_func())).grid(
            row=2, column=0)

        tk.Button(self, text='Save', command=self.data_conf).grid(row=4, column=0)

        tk.Button(self, text='Create txt file', command=self.save_txt).grid(row=6, column=0, columnspan=2)
        # tk.Button(self, text='create', command=self.get_choice_func).grid(row=2, column=0)

        self.choice_func = ttk.Combobox(self, values=[key for key in self.data.keys()], width=10, state='normal')
        self.choice_func.grid(row=3, column=0, pady=3, padx=3)

    def get_choice_func(self):
        print(self.choice_func.get())
        sub_dict = self.data.get(self.choice_func.get())
        return sub_dict

    def frame_gen(self):
        if self.frame_exist == 1:
            self.current_set_fr.destroy()
            self.frame_exist = 0

        self.current_set_fr = ttk.LabelFrame(self, text=f'{self.choice_func.get()}')
        self.current_set_fr.grid(row=0, column=2, rowspan=len(self.create_list))
        self.frame_exist = 1

    def param_creator(self, data):
        self.frame_gen()

        self.exist_labels = []
        self.exist_entry = []

        self.entry_vals = [tk.StringVar() for _ in range(len(data.keys()))]

        j = 0
        for i, key in enumerate(data.keys()):
            self.entry_vals[i].set(f'{data.get(key)}')

            if key in self.create_list:
                self.exist_labels.append(tk.Label(self.current_set_fr, text=f'{key}'))
                self.exist_labels[j].grid(row=j, column=3)

                self.exist_entry.append(tk.Entry(self.current_set_fr, textvariable=self.entry_vals[i]))
                self.exist_entry[j].grid(row=j, column=4)
                j += 1

    def data_conf(self):
        sub_dict = self.data.get(self.current_set_fr['text'])
        for i, key in enumerate(sub_dict.keys()):
            sub_dict.update({key: self.entry_vals[i]})

    def output_file(self, source_type, source_name, layer_index, amplitude, len_tf, time, value, lag, koord_ist,
                    distribution=None):
        time_fix = ''
        value_fix = ''
        for i in time:
            time_fix += str(i) + ' '
        for i in value:
            value_fix += str(i) + ' '

        out = f'SOURCE\n' \
              f'<source type>\n' \
              f'{source_type}\n' \
              f'<source name>\n' \
              f'{source_name}\n' \
              f'<layer index>\n' \
              f'{layer_index}\n' \
              f'<amplitude>\n' \
              f'{amplitude}\n' \
              f'<time function>\n' \
              f'{len_tf}\n' \
              f'{time_fix}\n' \
              f'{value_fix}\n' \
              f'<lag (1 - PLANE, 2 - SPHERE), parameters km>\n' \
              f'{lag}\n' \
              f'{koord_ist}\n' \
              f'<distribution>\n' \
              f'{distribution}\n\n'
        return out

    def output_file_flu(self, source_type, source_name, layer_index_from, layer_index_in, amplitude, len_tf, time,
                        value, lag, koord_ist, distribution=None):
        time_fix = ''
        value_fix = ''
        for i in time:
            time_fix += str(i) + ' '
        for i in value:
            value_fix += str(i) + ' '
        # метод для сохранения результатов под формат remp sources
        out = f'SOURCE\n' \
              f'<source type>\n' \
              f'{source_type}\n' \
              f'<source name>\n' \
              f'{source_name}\n' \
              f'<layer index from>\n' \
              f'{layer_index_from}\n' \
              f'<layer index in>\n' \
              f'{layer_index_in}\n' \
              f'<amplitude>\n' \
              f'{amplitude}\n' \
              f'<time function>\n' \
              f'{len_tf}\n' \
              f'{time_fix}\n' \
              f'{value_fix}\n' \
              f'<lag (1 - PLANE, 2 - SPHERE), parameters km>\n' \
              f'{lag}\n' \
              f'{koord_ist}\n' \
              f'<distribution>\n' \
              f'{distribution}\n\n'
        return out

    def save_txt(self):
        with open(f'{pr_dir()}/time functions/tf_for_remp.txt', 'w', encoding='utf-8') as file:
            for item in self.data.items():
                ldict = item[1]

                if 'Flu' in item[0]:
                    file.write(self.output_file_flu(source_type=ldict.get('source_type'),
                                                    source_name=ldict.get('source_name'),
                                                    layer_index_from=ldict.get('layer_index_from'),
                                                    layer_index_in=ldict.get('layer_index_in'),
                                                    amplitude=ldict.get('amplitude'),
                                                    len_tf=ldict.get('len_tf'),
                                                    time=ldict.get('time'),
                                                    value=ldict.get('value'),
                                                    lag=ldict.get('lag'),
                                                    koord_ist=ldict.get('koord_ist'),
                                                    distribution=ldict.get('distribution')))
                else:
                    file.write(self.output_file(source_type=ldict.get('source_type'),
                                                    source_name=ldict.get('source_name'),
                                                    layer_index=ldict.get('layer_index'),
                                                    amplitude=ldict.get('amplitude'),
                                                    len_tf=ldict.get('len_tf'),
                                                    time=ldict.get('time'),
                                                    value=ldict.get('value'),
                                                    lag=ldict.get('lag'),
                                                    koord_ist=ldict.get('koord_ist'),
                                                    distribution=ldict.get('distribution')))
