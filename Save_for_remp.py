import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import numpy as np
from scipy import integrate
import os


class Save_remp():
    def __init__(self, data_object=None, path=None):
        self.db = data_object
        self.path = path

        self.calc_amplitude = 0.

        self.save()

    def save(self):
        out = ''
        for item in self.db.items():
            gsource_db = item[1]
            name = item[0]
            try:
                self.calc_amplitude = self.amplitude_calculation(gsource_db)
            except:
                print(f'Введены не все данные в источнике {name}')
                mb.showerror('Предупреждение', f'Введены не все данные в источнике {name}')
                return

            for f_key in gsource_db.get_first_level_keys():
                for s_key in gsource_db.get_second_level_keys(f_key):
                    if 'Flu' in s_key:
                        a = self.flux_save(gsource_db, f_key, s_key, name)
                        out += a
                        if 'None' in a:
                            print(f'Введены не все данные в источнике {s_key}')
                            mb.showerror('Предупреждение', f'Введены не все данные в источнике {s_key}')
                            return

                    if 'Volume' in s_key:
                        a = self.volume_save(gsource_db, f_key, s_key, name)
                        out += a
                        if 'None' in a:
                            print(f'Введены не все данные в источнике {s_key}')
                            mb.showerror('Предупреждение', f'Введены не все данные в источнике {s_key}')
                            return

                    if 'Current' in s_key:
                        d = self.current_save(gsource_db, f_key, s_key, name)
                        if 'None' in d:
                            print(f'В источнике {s_key} нет тока')
                        else:
                            out += d

                    if 'Gursa' in s_key:
                        a = self.gursa_save(gsource_db, f_key, s_key, name)
                        out += a
                        if 'None' in a:
                            print(f'Введены не все данные в источнике {s_key}')
                            mb.showerror('Предупреждение', f'Введены не все данные в источнике {s_key}')
                            return

                    if 'Boundaries' in s_key:
                        a = self.boundaries_save(gsource_db, f_key, s_key, name)
                        out += a
                        if 'None' in a:
                            print(f'Введены не все данные в источнике {s_key}')
                            mb.showerror('Предупреждение', f'Введены не все данные в источнике {s_key}')
                            return


        self.save_file(out)

    def flux_save(self, gsource_db, f_key, s_key, name):

        out = ''
        out += f'Flux\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence_number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<layer index>\n'
        out += f'{s_key.split("_")[-1][0]} {s_key.split("_")[-1][1]}\n'
        out += f'<particle index>\n'
        out += f'{s_key.split("_")[2]}\n'
        out += f'<amplitude>\n'
        out += '{:6g}\n'.format(self.calc_amplitude)
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

        try:
            if len(gsource_db.get_last_level_data(f_key, s_key, "spectre")) != 6:
                raise Exception
            out += f'<spectre>\n'
            out += ' '.join(gsource_db.get_last_level_data(f_key, s_key, "spectre")) + f'\n'
        except:
            out += 'None' + f'\n'

        try:
            if len(gsource_db.get_last_level_data(f_key, s_key, "spectre numbers")) != 6:
                raise Exception

            out += f'<spectre number>\n'
            out += ' '.join((gsource_db.get_last_level_data(f_key, s_key, "spectre numbers"))) + '\n'
        except:
            out += 'None' + f'\n'

        out += '\n'

        return out

    def volume_save(self, gsource_db, f_key, s_key, name):
        out = ''
        out += f'Volume\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence_number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<layer index>\n'
        out += f'{s_key.split("_")[-1][0]}\n'
        out += f'<particle index>\n'
        out += f'{s_key.split("_")[1]}\n'
        out += f'<amplitude>\n'
        out += '{:6g}\n'.format(self.calc_amplitude)
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

        try:
            out += f'<spectre>\n'
            out += ''.join(gsource_db.get_last_level_data(f_key, s_key, "spectre")) + f'\n'
        except:
            out += 'None' + f'\n'

        try:
            out += f'<spectre number>\n'
            out += ''.join((gsource_db.get_last_level_data(f_key, s_key, "spectre numbers"))) + '\n'
        except:
            out += 'None' + f'\n'
        out += '\n'

        return out

    def current_save(self, gsource_db, f_key, s_key, name):
        out = ''
        out += f'{"_".join(s_key.split("_")[:2])}\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence_number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<layer index>\n'
        out += f'{s_key.split("_")[-1]}\n'
        out += f'<amplitude>\n'
        out += '{:6g}\n'.format(self.calc_amplitude)
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
        # out += f'<spectre>\n'
        # out += f'{gsource_db.get_last_level_data(f_key, s_key, "spectre")}' + f'\n'
        # out += f'<spectre number>\n'
        # out += f'{gsource_db.get_last_level_data(f_key, s_key, "spectre numbers")}' + '\n'
        out += '<distribution>\n'
        out += f'{gsource_db.get_last_level_data(f_key, s_key, "distribution")}' + '\n'

        out += '\n'

        return out

    def gursa_save(self, gsource_db, f_key, s_key, name):
        out = ''
        out += f'{s_key.split("_")[0]}\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence_number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<amplitude>\n'
        out += '{:6g}\n'.format(self.calc_amplitude)
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

        try:
            out += f'<spectre>\n'
            out += f'{gsource_db.get_last_level_data(f_key, s_key, "spectre")}' + f'\n'
        except:
            out += 'None' + f'\n'

        try:
            out += f'<spectre number>\n'
            out += f'{gsource_db.get_last_level_data(f_key, s_key, "spectre numbers")}' + '\n'
        except:
            out += 'None' + f'\n'

        out += '\n'

        return out

    def boundaries_save(self, gsource_db, f_key, s_key, name):
        out = ''
        out += f'{s_key.split("_")[0]}\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence_number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<amplitude>\n'
        out += '{:6g}\n'.format(self.calc_amplitude)
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

        try:
            if len(gsource_db.get_last_level_data(f_key, s_key, "spectre")) != 6:
                raise Exception
            out += f'<spectre>\n'
            out += ' '.join(gsource_db.get_last_level_data(f_key, s_key, "spectre")) + f'\n'
        except:
            out += 'None' + f'\n'

        try:
            if len(gsource_db.get_last_level_data(f_key, s_key, "spectre numbers")) != 6:
                raise Exception

            out += f'<spectre number>\n'
            out += ' '.join((gsource_db.get_last_level_data(f_key, s_key, "spectre numbers"))) + '\n'
        except:
            out += 'None' + f'\n'

        out += '\n'

        return out

    def save_file(self, string):

        file = os.path.join(self.path, 'remp_sources')
        file = os.path.normpath(file)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(string)

        mb.showinfo('Save', f'Сохранено в {file}')

    def amplitude_calculation(self, gsource_db):
        time = np.array(gsource_db.get_share_data("time"), dtype=float)
        func = np.array(gsource_db.get_share_data("func"), dtype=float)
        amplitude = float(gsource_db.get_share_data("amplitude"))

        ampl_save = amplitude / integrate.trapz(x=time, y=func)

        return ampl_save
