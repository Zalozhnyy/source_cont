import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import os


class Save_remp():
    def __init__(self, data_object=None, path=None):
        self.db = data_object
        self.path = path

        self.save()

    def save(self):
        out = ''
        for item in self.db.items():
            gsource_db = item[1]
            name = item[0]

            for f_key in gsource_db.get_first_level_keys():
                for s_key in gsource_db.get_second_level_keys(f_key):
                    if 'Flu' in s_key:
                        out += self.flux_save(gsource_db, f_key, s_key)
                        if 'None' in out:
                            print(f'Введены не все данные в источнике {s_key}')
                            return
                    if 'Current' in s_key:
                        out += self.current_save(gsource_db, f_key, s_key)
                        if 'None' in out:
                            print(f'Введены не все данные в источнике {s_key}')
                            return
                    if 'Gursa' in s_key:
                        out += self.gursa_save(gsource_db, f_key, s_key)
                        if 'None' in out:
                            print(f'Введены не все данные в источнике {s_key}')
                            return

                            # print(out)
        self.save_file(out)

    def flux_save(self, gsource_db, f_key, s_key):
        out = ''
        out += f'Flux\n'
        out += '<Influence number>\n'
        out += gsource_db.get_share_data('influence_number') + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<layer index>\n'
        out += f'{s_key.split("_")[-1][0]} {s_key.split("_")[-1][1]}\n'
        out += f'<particle index>\n'
        out += f'{s_key.split("_")[2]}\n'
        out += f'<amplitude>\n'
        out += f'{gsource_db.get_share_data("amplitude")}\n'
        out += f'<time function>\n'
        out += f'{gsource_db.get_share_data("count")}\n'
        time = ''
        for i in gsource_db.get_share_data("time"):
            time += str(i) + ' '
        out += f'{time}\n'
        func = ''
        for i in gsource_db.get_share_data("func"):
            func += str(i) + ' '
        out += f'{func}\n'
        out += f'<lag (1 - PLANE, 2 - SPHERE), parameters>\n'
        out += f'{gsource_db.get_share_data("lag").strip()}\n'
        out += f'<spectre>\n'
        out += ' '.join(gsource_db.get_last_level_data(f_key, s_key, "spectre")) + f'\n'
        out += f'<spectre_number>\n'
        out += ' '.join((gsource_db.get_last_level_data(f_key, s_key, "spectre_numbers"))) + '\n'
        out += '\n'

        return out

    def current_save(self, gsource_db, f_key, s_key):
        out = ''
        out += f'{"_".join(s_key.split("_")[:2])}\n'
        out += '<Influence number>\n'
        out += gsource_db.get_share_data('influence_number') + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<layer index>\n'
        out += f'{s_key.split("_")[-1]}\n'
        out += f'<amplitude>\n'
        out += f'{gsource_db.get_share_data("amplitude")}\n'
        out += f'<time function>\n'
        out += f'{gsource_db.get_share_data("count")}\n'
        time = ''
        for i in gsource_db.get_share_data("time"):
            time += str(i) + ' '
        out += f'{time}\n'
        func = ''
        for i in gsource_db.get_share_data("func"):
            func += str(i) + ' '
        out += f'{func}\n'
        out += f'<lag (1 - PLANE, 2 - SPHERE), parameters>\n'
        out += f'{gsource_db.get_share_data("lag").strip()}\n'
        out += f'<spectre>\n'
        out += f'{gsource_db.get_last_level_data(f_key, s_key, "spectre")}' + f'\n'
        out += f'<spectre_number>\n'
        out += f'{gsource_db.get_last_level_data(f_key, s_key, "spectre_numbers")}' + '\n'
        out += '<distribution>\n'
        if s_key.split("_"[1]) == 'x':
            out += 'JX\n'
        elif s_key.split("_"[1]) == 'y':
            out += 'JY\n'
        elif s_key.split("_"[1]) == 'z':
            out += 'JZ\n'

        out += '\n'

        return

    def gursa_save(self, gsource_db, f_key, s_key):
        out = ''
        out += f'{s_key.split("_")[0]}\n'
        out += '<Influence number>\n'
        out += gsource_db.get_share_data('influence_number') + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<amplitude>\n'
        out += f'{gsource_db.get_share_data("amplitude")}\n'
        out += f'<time function>\n'
        out += f'{gsource_db.get_share_data("count")}\n'
        time = ''
        for i in gsource_db.get_share_data("time"):
            time += str(i) + ' '
        out += f'{time}\n'
        func = ''
        for i in gsource_db.get_share_data("func"):
            func += str(i) + ' '
        out += f'{func}\n'
        out += f'<lag (1 - PLANE, 2 - SPHERE), parameters>\n'
        out += f'{gsource_db.get_share_data("lag").strip()}\n'
        out += f'<spectre>\n'
        out += f'{gsource_db.get_last_level_data(f_key, s_key, "spectre")}' + f'\n'
        out += f'<spectre_number>\n'
        out += f'{gsource_db.get_last_level_data(f_key, s_key, "spectre_numbers")}' + '\n'
        out += '\n'

        return out

    def save_file(self, string):

        file = os.path.join(self.path, 'remp_sources')
        file = os.path.normpath(file)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(string)

        mb.showinfo('Save', f'Сохранено в {file}')
