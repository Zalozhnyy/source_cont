import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb

import numpy as np
from scipy import integrate
import os
import pickle
import json

from loguru import logger

from source_Dialogs import ShowDuplicateSpectreNumbers


@logger.catch()
class Save_remp:
    def __init__(self, marple, micro_electronics, data_object, path):
        self.db = data_object
        self.path = path

        self.marple = marple
        self.micro_electronics = micro_electronics

        self.calc_amplitude = 0.
        self.saved = False

        self.exist_spectres = []

        self.save()

        self.create_spectre_list()

    def save(self):
        self.numbers_control()
        out = ''

        if self.marple is not None:
            out += self.save_marple()

        if self.micro_electronics is not None:
            out += self.save_micro_electronics()

        for item in self.db.items():
            gsource_db = item[1]
            name = item[0]
            try:
                if gsource_db.get_share_data('amplitude') is None or gsource_db.get_share_data('amplitude') == 0:
                    raise Exception

                if gsource_db.get_share_data('integrate'):
                    self.calc_amplitude = self.amplitude_calculation(gsource_db)
                else:
                    self.calc_amplitude = gsource_db.get_share_data('amplitude')
            except Exception:
                print(f'Введены не все данные в источнике {name}')
                mb.showerror('Предупреждение', f'Некорректная амплитуда в {name}')
                return

            for f_key in gsource_db.get_first_level_keys():
                for s_key in gsource_db.get_second_level_keys(f_key):
                    if 'Flu' in s_key:
                        a = self.flux_save(gsource_db, f_key, s_key, name)
                        out += a
                        if 'None' in a:
                            print(f'Введены не все данные в источнике {s_key}')
                            mb.showerror('Предупреждение', f'Введены не все данные в источнике {s_key}')
                            print(a)
                            return

                    if s_key.split('_')[0] == 'Volume78':
                        a = self.volume78_save(gsource_db, f_key, s_key, name)
                        out += a
                        if 'None' in a:
                            print(f'Введены не все данные в источнике {s_key}')
                            mb.showerror('Предупреждение', f'Введены не все данные в источнике {s_key}')
                            print(a)
                            return

                    if s_key.split('_')[0] == 'Volume':
                        a = self.volume_save(gsource_db, f_key, s_key, name)
                        out += a
                        if 'None' in a:
                            print(f'Введены не все данные в источнике {s_key}')
                            mb.showerror('Предупреждение', f'Введены не все данные в источнике {s_key}')
                            print(a)
                            return

                    if 'Current' in s_key:
                        d = self.current_save(gsource_db, f_key, s_key, name)
                        if d is None:
                            print(f'Добавьте частицу в проект')
                            return
                        elif 'None' in d:
                            print(f'В источнике {s_key} нет тока')
                        else:
                            out += d

                    if 'Sigma' in s_key:
                        d = self.current_save(gsource_db, f_key, s_key, name, energy=True)
                        out += d
                        if d is None:
                            print(f'Добавьте частицу в проект')
                            return
                        elif 'None' in d:
                            print(f'Введены не все данные в источнике {s_key}')
                            mb.showerror('Предупреждение', f'Введены не все данные в источнике {s_key} {f_key}')
                            print(d)
                            return

                    if 'Boundaries' in s_key:
                        a = self.boundaries_save(gsource_db, f_key, s_key, name)
                        out += a
                        if 'None' in a:
                            print(f'Введены не все данные в источнике {s_key}')
                            mb.showerror('Предупреждение', f'Введены не все данные в источнике {s_key}')
                            print(a)
                            return

        self.save_file(out)

        with open(os.path.join(self.path, 'Sources.pkl'), 'wb') as f:
            pickle.dump(self.db, f)

        try:
            JsonSave(self.marple, self.micro_electronics, self.db, self.path)
        except Exception:
            print('Ошибка в новом формате сохранения (JSON).')

        self.saved = True

    def flux_save(self, gsource_db, f_key, s_key, name):

        out = ''
        out += f'Flux\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        # out += '<particle number>\n'
        # out += str(gsource_db.get_share_data('particle number')) + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<layer index>\n'
        out += f'{s_key.split("_")[-2]} {s_key.split("_")[-1]}\n'
        out += f'<particle index>\n'
        out += f'{s_key.split("_")[2]}\n'
        out += f'<amplitude>\n'
        out += '{:.5g}\n'.format(self.calc_amplitude)
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
        out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'spectre') + '\n'

        out += f'<spectre number>\n'
        out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'spectre numbers') + '\n'

        out += '\n'

        return out

    def volume_save(self, gsource_db, f_key, s_key, name):
        out = ''
        out += f'Volume\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        # out += '<particle number>\n'
        # out += str(gsource_db.get_share_data('particle number')) + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<layer index>\n'
        out += f'{s_key.split("_")[-1]}\n'
        out += f'<particle index>\n'
        out += f'{s_key.split("_")[1]}\n'
        out += f'<amplitude>\n'
        out += '{:.5g}\n'.format(self.calc_amplitude)
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
        out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'spectre') + '\n'

        out += f'<spectre number>\n'
        out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'spectre numbers') + '\n'

        out += '\n'

        return out

    def volume78_save(self, gsource_db, f_key, s_key, name):
        out = ''
        out += f'Volume78\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        # out += '<particle number>\n'
        # out += str(gsource_db.get_share_data('particle number')) + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<layer index>\n'
        out += f'{s_key.split("_")[-1]}\n'
        out += f'<particle index>\n'
        out += f'{s_key.split("_")[1]}\n'
        out += f'<amplitude>\n'
        out += '{:.5g}\n'.format(self.calc_amplitude)
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

        if gsource_db.get_last_level_data(f_key, s_key, 'spectre') is not None:
            out += f'<spectre>\n'
            out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'spectre') + '\n'

            out += f'<spectre number>\n'
            out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'spectre numbers') + '\n'

        if gsource_db.get_last_level_data(f_key, s_key, 'distribution') is not None:
            out += f'<distribution>\n'
            out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'distribution') + '\n'

        out += '\n'

        return out

    def current_save(self, gsource_db, f_key, s_key, name, energy=False):
        out = ''
        if energy:
            out += f'Sigma\n'
        else:
            out += f'{"_".join(s_key.split("_")[:2])}\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        # out += '<particle number>\n'
        # try:
        #     out += str(gsource_db.get_share_data('particle number')) + '\n'
        # except:
        #     return None

        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<layer index>\n'
        out += f'{s_key.split("_")[-1]}\n'
        out += f'<amplitude>\n'
        out += '{:.5g}\n'.format(self.calc_amplitude)
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

        out += f'<distribution>\n'
        out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'distribution') + '\n'
        out += '\n'

        return out

    def boundaries_save(self, gsource_db, f_key, s_key, name):
        out = ''
        out += f'{s_key.split("_")[0]}\n'
        out += '<influence number>\n'
        out += gsource_db.get_share_data('influence number') + '\n'
        out += '<influence name>\n'
        out += name + '\n'
        out += '<particle index>\n'
        out += str(gsource_db.get_share_data('particle number')) + '\n'
        out += f'<source name>\n'
        out += f'{s_key}\n'
        out += f'<amplitude>\n'
        out += '{:.5g}\n'.format(self.calc_amplitude)
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
        out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'spectre') + '\n'

        out += f'<spectre number>\n'
        out += self._get_last_level_data_with_exception(gsource_db, f_key, s_key, 'spectre numbers') + '\n'

        out += '\n'

        return out

    def save_marple(self):
        out = ''
        out += 'Marple_sigma\n'
        out += '<distribution>\n'
        out += f'{self.marple["sigma"]}\n'
        out += '\n'

        out += 'Marple_ionization\n'
        out += '<distribution>\n'
        out += f'{self.marple["ion"]}\n'
        out += '\n'

        return out

    def save_micro_electronics(self):
        out = ''
        out += 'Field78\n'
        out += '<distribution>\n'
        out += f'{self.micro_electronics["field78"]}\n'
        out += '\n'

        out += 'Density78\n'
        out += '<distribution>\n'
        out += f'{self.micro_electronics["density78"]}\n'
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
        amplitude = abs(float(gsource_db.get_share_data("amplitude")))

        try:
            ampl_save = amplitude / integrate.trapz(x=time, y=func)
        except (RuntimeWarning, ZeroDivisionError):
            ampl_save = amplitude
            print('Амплитуда не была поделена, найдено деление на ноль')

        return ampl_save

    def numbers_control(self):
        numbers = []
        for item in self.db.items():
            gsource_db = item[1]
            name = item[0]

            for f_key in gsource_db.get_first_level_keys():
                for s_key in gsource_db.get_second_level_keys(f_key):
                    if 'Current' in s_key or 'Sigma' in s_key:
                        continue

                    spectre = gsource_db.get_last_level_data(f_key, s_key, "spectre")
                    spectre_number = gsource_db.get_last_level_data(f_key, s_key, "spectre numbers")

                    if spectre is None:
                        print(f'Не выбраны данные в {name} {f_key} {s_key}')
                        return

                    if type(spectre_number) is list:
                        for i in range(len(spectre_number)):
                            numbers.append([int(spectre_number[i]), [name, f_key, s_key]])

                    else:
                        numbers.append([spectre_number, [name, f_key, s_key]])

        e_numbers = []
        for i in range(len(numbers)):
            e_numbers.append(int(numbers[i][0]))

        if len(e_numbers) == len(set(e_numbers)):  # нет повторяющихся элементов
            return

        re_numbers = {}  # словарь хранящий источники с одинаковыми номерами спектров
        setarr = sorted(set(e_numbers))
        for i, x in enumerate(setarr):

            n = x

            val_for_dict = []
            for j in range(len(numbers)):
                if n == numbers[j][0]:
                    val_for_dict.append(numbers[j][1])

            re_numbers.update({n: val_for_dict})

        if len(re_numbers) != 0:
            ask = mb.askyesno('Внимание', 'Обнаружены одинаковые номера спектров.\n'
                                          'Показать подробности?')
            if ask is True:
                ex = ShowDuplicateSpectreNumbers(re_numbers)
                ex.grab_set()

    def create_spectre_list(self):

        for item in self.db.items():
            gsource_db = item[1]
            name = item[0]

            for f_key in gsource_db.get_first_level_keys():
                for s_key in gsource_db.get_second_level_keys(f_key):
                    if 'Flu' in s_key:
                        data = gsource_db.get_last_level_data(f_key, s_key, 'spectre')
                        if type(data) is list:
                            [self.exist_spectres.append(i) for i in data if i not in self.exist_spectres]
                        else:
                            self.exist_spectres.append(data)

                    if 'Volume' in s_key:
                        data = gsource_db.get_last_level_data(f_key, s_key, 'spectre')
                        if type(data) is list:
                            [self.exist_spectres.append(i) for i in data if i not in self.exist_spectres]
                        else:
                            self.exist_spectres.append(data)

                    if 'Boundaries' in s_key:
                        data = gsource_db.get_last_level_data(f_key, s_key, 'spectre')
                        if type(data) is list:
                            [self.exist_spectres.append(i) for i in data if i not in self.exist_spectres]
                        else:
                            self.exist_spectres.append(data)

        with open(os.path.join(self.path, 'spectres'), 'w', encoding='utf-8') as file:
            file.write('<Particles spectrum>\n')
            file.write(str(len(self.exist_spectres)) + '\n')
            try:

                for sp in self.exist_spectres:
                    file.write(sp + '\n')

            except TypeError:
                print('Список спектров не был создан')
                return

    def _get_last_level_data_with_exception(self, data_object, first_key, second_key, last_key):
        out = ''

        db_vel = data_object.get_last_level_data(first_key, second_key, last_key)

        if db_vel is None:
            out = 'None'
            return out

        if type(db_vel) is list:
            out = ' '.join(list(map(str, db_vel)))

        else:
            out += str(db_vel)

        return out


@logger.catch()
class JsonSave:
    def __init__(self, marple, micro_electronics, data_object, path):
        self.db = data_object
        self.path = path

        self.marple = marple
        self.micro_electronics = micro_electronics

        self.save_dict = {
            "Influences": {
                "Lag": {
                    "Type": 0,
                    "X": 0,
                    "Y": 0,
                    "Z": 0,
                }
            }
        }

        self.local_influence_dict = {}

        self.calc_amplitude = 0.

        self.init_save_dict()

    def init_save_dict(self):

        if self.marple is not None:
            marple_dict = {
                'Marple': {
                    'Sigma': f'{self.marple["sigma"]}',
                    'Ionization': f'{self.marple["ion"]}'
                }
            }
            self.save_dict = {**marple_dict, **self.save_dict}

        if self.micro_electronics is not None:
            mic_dict = {
                'Microelectronics': {
                    'Field78': f'{self.micro_electronics["field78"]}',
                    'Density78': f'{self.micro_electronics["density78"]}'
                }
            }
            self.save_dict = {**mic_dict, **self.save_dict}

        for item in self.db.items():
            gsource_db = item[1]
            name = item[0]

            self.local_influence_dict.clear()

            try:
                if gsource_db.get_share_data('integrate'):
                    self.calc_amplitude = self.amplitude_calculation(gsource_db)
                else:
                    self.calc_amplitude = gsource_db.get_share_data('amplitude')
            except Exception:
                print(f'Введены не все данные в источнике {name}')
                mb.showerror('Предупреждение', f'Введены не все данные в источнике {name}')
                return

            lag = list(map(float, gsource_db.get_share_data("lag").strip().split())) if gsource_db.get_share_data(
                "lag") is not None else [0, 0, 0, 0]
            self.save_dict['Influences']["Lag"]['Type'] = int(lag[0])
            self.save_dict['Influences']["Lag"]['X'] = lag[1] if lag[0] != 0 else 0
            self.save_dict['Influences']["Lag"]['Y'] = lag[2] if lag[0] != 0 else 0
            self.save_dict['Influences']["Lag"]['Z'] = lag[3] if lag[0] != 0 else 0

            self.local_influence_dict = {
                name: {
                    "Influence number": int(gsource_db.get_share_data('influence number')),
                    "Amplitude": float('{:.5g}'.format(self.calc_amplitude)),
                    "Time function": {
                        "Count": gsource_db.get_share_data("count"),
                        # "Time": gsource_db.get_share_data("time"),
                        # "Value": gsource_db.get_share_data("func"),
                        "Time": ' '.join(list(map(str, gsource_db.get_share_data("time")))),
                        "Value": ' '.join(list(map(str, gsource_db.get_share_data("func")))),
                    },

                    "Sources": {

                    }
                }
            }

            self.write_sources_to_local_dict(name, gsource_db)

            self.save_dict['Influences'] = {**self.save_dict['Influences'], **self.local_influence_dict}

        path = os.path.join(self.path, 'remp_sources.json')
        with open(path, 'w') as file:
            json.dump(self.save_dict, file, indent=4)

    def write_sources_to_local_dict(self, name, gsource_db):

        for f_key in gsource_db.get_first_level_keys():
            if 'Current' in f_key:
                if 'Currents' not in self.local_influence_dict[name]['Sources'].keys():
                    self.local_influence_dict[name]['Sources'].update({'Currents': {}})

                self.write_current_to_local_dict(name, gsource_db, f_key)

            elif 'Sigma' in f_key:
                if 'Sigmas' not in self.local_influence_dict[name]['Sources'].keys():
                    self.local_influence_dict[name]['Sources'].update({'Sigmas': {}})

                self.write_sigma_to_local_dict(name, gsource_db, f_key)

            else:  # частицы
                for s_key in gsource_db.get_second_level_keys(f_key):
                    if 'Flu' in s_key:
                        if 'Surface' not in self.local_influence_dict[name]['Sources'].keys():
                            self.local_influence_dict[name]['Sources'].update({'Surface': {}})

                        self.write_flux_to_local_dict(name, gsource_db, f_key, s_key)

                    elif s_key.split('_')[0] == 'Volume78':
                        if 'Volume' not in self.local_influence_dict[name]['Sources'].keys():
                            self.local_influence_dict[name]['Sources'].update({'Volume': {}})

                        self.write_volume78_to_local_dict(name, gsource_db, f_key, s_key)

                    elif s_key.split('_')[0] == 'Volume':
                        if 'Volume' not in self.local_influence_dict[name]['Sources'].keys():
                            self.local_influence_dict[name]['Sources'].update({'Volume': {}})

                        self.write_volume_to_local_dict(name, gsource_db, f_key, s_key)

                    elif 'Boundaries' in s_key:
                        if 'From boundaries' not in self.local_influence_dict[name]['Sources'].keys():
                            self.local_influence_dict[name]['Sources'].update({'From boundaries': {}})

                        self.write_boundaries_to_local_dict(name, gsource_db, f_key, s_key)

                    else:
                        print(f'{s_key} не распознан')

    def write_current_to_local_dict(self, name, gsource_db, first_key):
        for second_key in gsource_db.get_second_level_keys(first_key):
            source_name = second_key

            current_dict = {
                'Type': f'{"_".join(source_name.split("_")[:2])}',
                'Layer index': int(f'{source_name.split("_")[-1]}'),
                'Distribution': self._get_last_level_data_with_exception(gsource_db, first_key, second_key,
                                                                         'distribution')
            }

            self.local_influence_dict[name]['Sources']['Currents'].update({source_name: current_dict})

    def write_sigma_to_local_dict(self, name, gsource_db, first_key):
        for second_key in gsource_db.get_second_level_keys(first_key):
            source_name = second_key

            sigma_dict = {
                'Type': 'Sigma',
                'Layer index': int(f'{source_name.split("_")[-1]}'),
                'Distribution': self._get_last_level_data_with_exception(gsource_db, first_key, second_key,
                                                                         'distribution')
            }

            self.local_influence_dict[name]['Sources']['Sigmas'].update({source_name: sigma_dict})

    def write_flux_to_local_dict(self, name, gsource_db, first_key, second_key):
        source_name = second_key

        flux_dict = {
            'Type': 'Flux',
            'Layer index from': int(f'{second_key.split("_")[-2]}'),
            'Layer index to': int(f'{second_key.split("_")[-1]}'),
            'Particle index': int(f'{second_key.split("_")[2]}'),
            'Spectre': self._get_last_level_data_with_exception(gsource_db, first_key, second_key, 'spectre'),
            'Spectre number': self._get_last_level_data_with_exception(gsource_db, first_key, second_key,
                                                                       'spectre numbers'),
        }

        self.local_influence_dict[name]['Sources']['Surface'].update({source_name: flux_dict})

    def write_volume78_to_local_dict(self, name, gsource_db, first_key, second_key):
        source_name = second_key

        flux_dict = {
            'Type': 'Volume78',
            'Layer index': int(f'{second_key.split("_")[-1]}'),
            'Particle index': int(f'{second_key.split("_")[1]}'),
            'Spectre': self._get_last_level_data_with_exception(gsource_db, first_key, second_key, 'spectre'),
            'Spectre number': self._get_last_level_data_with_exception(gsource_db, first_key, second_key,
                                                                       'spectre numbers'),
            'Distribution': self._get_last_level_data_with_exception(gsource_db, first_key, second_key,
                                                                     'distribution') if gsource_db.get_last_level_data(
                first_key, second_key, 'distribution') is not None else None
        }

        self.local_influence_dict[name]['Sources']['Volume'].update({source_name: flux_dict})

    def write_volume_to_local_dict(self, name, gsource_db, first_key, second_key):
        source_name = second_key

        flux_dict = {
            'Type': 'Volume',
            'Layer index': int(f'{second_key.split("_")[-1]}'),
            'Particle index': int(f'{second_key.split("_")[1]}'),
            'Spectre': self._get_last_level_data_with_exception(gsource_db, first_key, second_key, 'spectre'),
            'Spectre number': self._get_last_level_data_with_exception(gsource_db, first_key, second_key,
                                                                       'spectre numbers')
        }

        self.local_influence_dict[name]['Sources']['Volume'].update({source_name: flux_dict})

    def write_boundaries_to_local_dict(self, name, gsource_db, first_key, second_key):
        source_name = second_key

        flux_dict = {
            'Type': f'{second_key.split("_")[0]}',
            'Particle index': int(f'{second_key.split("_")[1]}'),
            'Spectre': self._get_last_level_data_with_exception(gsource_db, first_key, second_key, 'spectre'),
            'Spectre number': self._get_last_level_data_with_exception(gsource_db, first_key, second_key,
                                                                       'spectre numbers')
        }

        self.local_influence_dict[name]['Sources']['From boundaries'].update({source_name: flux_dict})

    def amplitude_calculation(self, gsource_db):
        time = np.array(gsource_db.get_share_data("time"), dtype=float)
        func = np.array(gsource_db.get_share_data("func"), dtype=float)
        amplitude = abs(float(gsource_db.get_share_data("amplitude")))

        try:
            ampl_save = amplitude / integrate.trapz(x=time, y=func)
        except RuntimeWarning:
            ampl_save = amplitude
            print('Амплитуда не была поделена, найдено деление на ноль')

        return ampl_save

    def _get_last_level_data_with_exception(self, data_object, first_key, second_key, last_key):
        out = ''

        db_vel = data_object.get_last_level_data(first_key, second_key, last_key)

        if db_vel is None:
            out = 'None'
            return out

        if type(db_vel) is list:
            out = ' '.join(list(map(str, db_vel)))

        else:
            out += str(db_vel)

        return out


if __name__ == '__main__':
    path = r'C:\Work\Test_projects\test_sources_project'

    with open('Sources.pkl', 'rb') as f:
        db = pickle.load(f)

    ex = JsonSave(None, None, db, path)
