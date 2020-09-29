import numpy as np
import locale
import os
from tkinter import filedialog as fd
from tkinter import messagebox as mb


class DataParser:
    def __init__(self, path):
        self.path = path
        self.dir_path = os.path.dirname(self.path)
        self.decoding_def = locale.getpreferredencoding()
        self.decoding = 'utf-8'

    # def lay_decoder_old(self):
    #     #### .LAY DECODER
    #     try:
    #         with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
    #             lines = file.readlines()
    #     except UnicodeDecodeError:
    #
    #         with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
    #             lines = file.readlines()
    #     lay_numeric = int(lines[2])
    #     out_lay = np.zeros((lay_numeric, 3), dtype=int)
    #     j = 0
    #     for i in range(len(lines)):
    #         if '<Номер, название слоя>' in lines[i]:  # 0 - номер слоя  1 - стороннй ток  2 - стро. ист.
    #             out_lay[j, 0] = int(lines[i + 1].split()[0])
    #             out_lay[j, 1] = int(lines[i + 3].split()[2])
    #             out_lay[j, 2] = int(lines[i + 3].split()[3])
    #             j += 1
    #     # print('.LAY  ', out_lay)
    #     return out_lay

    def lay_decoder(self):
        #### .LAY DECODER
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines = file.readlines()
        except UnicodeDecodeError:

            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines = file.readlines()

        try:

            line = 2  # <Количество слоев> + 1 строка
            lay_numeric = int(lines[line])
            out_lay = np.zeros((lay_numeric, 3), dtype=int)
            # print(f'<Количество слоев> + 1 строка     {lines[line]}')

            line += 2  # <Номер, название слоя>
            # print(f'<Номер, название слоя>     {lines[line]}')

            for layer in range(lay_numeric):
                line += 1  # <Номер, название слоя> + 1 строка
                # print(f'<Номер, название слоя> + 1 строка     {lines[line]}')

                out_lay[layer, 0] = int(lines[line].split()[0])  # 0 - номер слоя

                line += 2  # <газ(0)/не газ(1), и тд + 1 строка
                out_lay[layer, 1] = int(lines[line].split()[2])  # 1 - стороннй ток
                out_lay[layer, 2] = int(lines[line].split()[3])  # 2 - стро. ист.

                extended = False
                if int(lines[line].split()[-1]) == 1:
                    extended = True

                line += 2  # <давление в слое(атм.), плотн.(г/см3), + 1 строка
                if extended is False:
                    line += 2  # следущая частица    <Номер, название слоя>
                elif extended is True:
                    line += 2  # <молекулярный вес[г/моль] + 1 строка

                    line += 2  # следущая частица    <Номер, название слоя>
            return out_lay
        except Exception:
            print('Ошибка в чтении файла .LAY')
            return

    def tok_decoder(self):
        #### .TOK DECODER
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines_tok = file.readlines()
        except UnicodeDecodeError:

            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines_tok = file.readlines()
        out_tok = np.zeros(3, dtype=int)

        try:
            out_tok[0] = lines_tok[2].strip()
            out_tok[1] = lines_tok[8].strip()
            out_tok[2] = lines_tok[6].strip()
            # for i in range(len(lines_tok)):
            #     if '<Начальное поле (0-нет,1-да)>' in lines_tok[i]:
            #         out_tok[0] = int(lines_tok[i + 1])
            #     if '<Внешнее поле (0-нет,1-да)>' in lines_tok[i]:
            #         out_tok[1] = int(lines_tok[i + 1])
            #     if '<Тип задачи (0-Коши 1-Гурса>' in lines_tok[i]:
            #         out_tok[2] = int(lines_tok[i + 1])
            # добавить тение строки гурса
            # print('.TOK  ', out_tok)
            return out_tok

        except Exception:
            print('Ошибка в чтении файла .TOK')
            return

    def pl_decoder(self):
        #### .PL DECODER
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines_pl = file.readlines()
        except UnicodeDecodeError:

            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines_pl = file.readlines()
        try:
            particle_count = int(lines_pl[2])
            layers = int(lines_pl[6])
            line = 8  # <Layer numbers>
            layers_numbers = np.array(lines_pl[line].strip().split(), dtype=int)
            particle_numbers = np.array(lines_pl[4].strip().split(), dtype=int)

            line += 1  # <Particle motion in a layer (vertical-layers, horizontal-particles) 0-No/1-Yes>
            line += particle_count + 1  # <Source in volume (vertical-layers, horizontal-particles) 0-No/1-Yes/2-Random>

            out_volume = {}
            for i in range(particle_count):
                line += 1
                out_volume.update({particle_numbers[i]: np.array(lines_pl[line].strip().split(), dtype=int)})
            line += 2  # <Surface source + 1

            out_surf = {}

            for i in range(particle_count):
                line += 1
                lay_number = int(lines_pl[line].strip())

                key_list = []
                for j in range(layers):
                    line += 1
                    key_list.append(lines_pl[line].strip().split())

                key_list = np.array(key_list, dtype=int)
                out_surf.update({lay_number: key_list})
                line += 1

            # exit on <Current density calculation
            line += 1 + particle_count  # <Ionization inhibition
            line += 1 + particle_count  # <<Ionization source
            line += 1 + particle_count  # <<Elastic scattering

            try:
                line += 1 + particle_count  # <<<Particle number>

                out_boundaries = {}

                for i in range(particle_count):
                    line += 1

                    cur_part = int(lines_pl[line].strip())
                    line += 2  # <Source from the boundaries + 1

                    out_boundaries.update({cur_part: np.array(lines_pl[line].strip().split(), dtype=int)})
                    line += 1

            except:
                print('Старый файл PL')
                out_boundaries = {}
                for i in range(particle_count):
                    out_boundaries.update({particle_numbers[i]: np.zeros(6, dtype=int)})

            # print(lines_pl[line])
            return out_surf, out_volume, out_boundaries, layers_numbers

        except Exception:
            print('Ошибка в чтении файла .PL')
            return
            # with open(rf'{self.path}', 'r', encoding='utf-8') as file:
            #     lines_pl = file.readlines()
            # for line in range(len(lines_pl)):
            #     if '<Количество слоев>' in lines_pl[line]:
            #         pl_numeric = int(lines_pl[line + 1])
            #         out_pl = np.zeros((pl_numeric, pl_numeric), dtype=int)
            #
            #     if '<Частица номер>' in lines_pl[line]:
            #         for i in range(pl_numeric):
            #             for j in range(len(lines_pl[line + 2 + i].split())):
            #                 out_pl[i, j] = int(lines_pl[line + 2 + i].split()[j])
            #
            # # print('.PL\n', out_pl)
            # return out_pl
            # print('.PL\n', out_pl)

    def grid_parcer(self):

        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines = file.readlines()
        except UnicodeDecodeError:

            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines = file.readlines()
        out = np.array(lines[15].split(), dtype=float)
        return out

    def par_decoder(self):
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines = file.readlines()

        try:
            # L[0] '<Количество типов частиц>'
            particles = {}
            part_count = (int(lines[2].strip()))

            string_num = 3  # <Type(1-electron, 2-positron, 3-quantum), Name> - 1
            for numbers in range(part_count):
                string_num += 1  # <Type(1-electron, 2-positron, 3-quantum), Name>
                string_num += 1
                name = lines[string_num].strip().split()[-1]
                particles.update({name: {}})
                particles[name].update({'type': int(lines[string_num].strip().split()[0])})

                string_num += 2  # <Number, charge(el.), mass(g), + 1 string
                particles[name].update({'number': int(lines[string_num].split()[0])})

                string_num += 4  # <Number of processes> + 1 string
                procces = int(lines[string_num].strip())

                string_num += procces * 2 + 1

            return particles

        except Exception:
            print('Ошибка в чтении файла .PAR')
            return

    def remp_source_decoder(self):
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines = file.readlines()

        triggers = ['Volume', 'Volume78', 'Current_x', 'Current_y', 'Current_z', 'Energy', 'Flux', 'Boundaries']
        r = []
        for i, line in enumerate(lines):
            if any([line.strip() == j for j in triggers]):
                r.append(i)
        r.append(len(lines))
        out = {}
        for i in range(len(r) - 1):
            for j in range(r[i], r[i + 1]):
                if lines[j].strip() == '<influence number>':
                    influence_number = int(lines[j + 1].strip())
                    if influence_number not in out.keys():
                        out.update({influence_number: {}})

                if lines[j].strip() == '<influence name>':
                    influence_name = lines[j + 1].strip()
                    out[influence_number].update({'influence name': influence_name})

                if lines[j].strip() == '<particle number>':
                    particle_number = int(lines[j + 1].strip())
                    out[influence_number].update({'particle number': particle_number})

                if lines[j].strip() == '<source name>':
                    name = lines[j + 1].strip()
                    out[influence_number].update({name: {}})

                if lines[j].strip() == '<amplitude>':
                    amplitude = float(lines[j + 1].strip())
                    out[influence_number][name].update({'amplitude': amplitude})

                if lines[j].strip() == '<time function>':
                    count = int(lines[j + 1].strip())
                    time = lines[j + 2].strip().split()
                    func = lines[j + 3].strip().split()
                    out[influence_number][name].update({'count': count})
                    out[influence_number][name].update({'time': np.array(time, dtype=float)})
                    out[influence_number][name].update({'func': np.array(func, dtype=float)})

                if lines[j].strip() == '<spectre>':
                    spectre = lines[j + 1].strip()
                    out[influence_number][name].update({'spectre': spectre})

                if lines[j].strip() == '<spectre number>':
                    spectre_number = lines[j + 1].strip()
                    out[influence_number][name].update({'spectre number': spectre_number})

                if lines[j].strip() == '<distribution>':
                    distribution = lines[j + 1].strip()
                    out[influence_number][name].update({'distribution': distribution})

        return out

    def pech_check(self):
        self.source_path = os.path.normpath((os.path.join(self.path, r'pechs/initials/source')))

        if os.path.exists(self.source_path):
            lag = self.pech_check_utility(self.source_path)
            # mb.showinfo('Info', fr'lag/parameters взят из {os.path.normpath(self.source_path)}')
            print(fr'Параметр задержки был взят из {os.path.normpath(self.source_path)}')
        else:
            ask = mb.askyesno('Проект переноса не найден',
                              f'Путь {os.path.normpath(self.source_path)} не найден.\n'
                              f'Проект переноса не обнаружен.\n'
                              f'Продолжить без проекта переноса?\n\n\n'
                              f'Да - параметр задержки будет равен нулю.\n'
                              f'Нет - выбрать проект переноса.\n')
            if ask is True:
                self.source_path = None
                lag = '0'
            else:
                mb.showinfo('Info', fr'Выберите файл source, находящийся в <pechs/initials/source>')
                self.source_path = fd.askopenfilename(title='Выберите файл source', initialdir=f'{self.path}')
                if self.source_path == '':
                    mb.showinfo('Info', fr'параметр задержки равен 0')
                    self.source_path = None
                    return '0', self.source_path
                lag = self.pech_check_utility(self.source_path)

        return lag, self.source_path

    def pech_check_utility(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        koord = '0'
        for i in lines:
            if 'SOURCE_DIRECTION' in i:
                koord = i.split('=')[-1]
                return f'1 {koord}'

        if koord == '0':
            return koord

    def distribution_reader(self):
        out = []
        for i in os.listdir(self.path + '/'):
            if 'JX' in i or 'JY' in i or 'JZ' in i:
                out.append(i)
        return out

    def temp_spectres_reader(self):
        path = os.path.join(self.path, r'time functions/user configuration/temp.ini')
        out = {}
        if not os.path.exists(path):
            return out
        with open(path, 'r', encoding='utf-8') as file:
            while True:
                line = file.readline().strip()
                if line == '':
                    break
                line = line.split(';')
                out.update({line[0]: (line[1], line[2])})
        return out

    def get_spectre_for_flux(self, part_number, from_layer, to_layer):
        out = {}
        for file in os.listdir(os.path.split(self.path)[0]):
            if file.endswith('.spc'):
                d = file.replace('.spc', '')
                l = d.split('_')
                fl = int(l[0])
                tl = int(l[1])
                pn = int(l[-1])
                if (pn == int(part_number)) and (fl == int(from_layer)) and (tl == int(to_layer)):
                    with open(os.path.join(self.dir_path, file), 'r') as f:
                        for i, line in enumerate(f):
                            if i == 2:
                                number = line.strip()
                                break
                    out.update({file: number})
        return out

    def get_spectre_for_bound(self):
        out = {}
        create_list = ['xmax_part', 'xmin_part', 'ymax_part', 'ymin_part', 'zmax_part', 'zmin_part']
        for file in os.listdir(os.path.split(self.path)[0]):
            if any(file in i for i in create_list):
                try:
                    with open(fr'{os.path.join(self.dir_path, file)}', 'r', encoding=self.decoding) as f:
                        for i, line in enumerate(f):
                            if i == 2:
                                number = line.strip()
                                break
                except:
                    with open(fr'{os.path.join(self.dir_path, file)}', 'r', encoding=self.decoding_def) as f:
                        for i, line in enumerate(f):
                            if i == 2:
                                number = line.strip()
                                break
                out.update({file: number})

        return out

    def elph_reader(self):

        path = os.path.join(os.path.dirname(__file__), 'elph.txt')

        out = np.loadtxt(path, skiprows=1, dtype=float) * 1e-3
        return out

    def return_empty_array(self, shape=(0, 0)):
        return np.zeros(shape)


class SpOneReader:
    def __init__(self, path):
        self.path = path
        self.dir_path = os.path.dirname(self.path)
        self.decoding_def = locale.getpreferredencoding()
        self.decoding = 'utf-8'

        self.sp_type = 1

        self.description = ''

        self.phi_angles = []
        self.phi_parts = []

        self.theta_angles = []
        self.theta_parts = []

        self.energy_angles = []
        self.energy_parts = []

        self.sp_number = 0
        self.sp_power = 0.
        self.sp_part_count = 0

        self.phi_count = 0
        self.theta_count = 0
        self.energy_count = 0

        self.phi_type = 0
        self.theta_type = 0
        self.energy_type = 0

    def start_read(self):
        if not os.path.exists(self.path):
            return
        with open(rf'{self.path}', 'r', encoding='cp1251') as file:
            self.description_reader(file)

            self.phi_reader(file)

            self.theta_reader(file)

            self.energy_reader(file)

    def description_reader(self, file):

        for i in range(13):
            d = file.readline()
            if i == 0:
                self.description = d.strip()
            if i == 2:
                self.sp_number = int(d.strip())
            if i == 4:
                self.sp_power = float(d.strip())
            if i == 8:
                self.sp_part_count = int(d.strip())
            if i == 10:
                d = d.strip().split()
                self.phi_count = int(d[0])
                self.theta_count = int(d[1])
                self.energy_count = int(d[2])

    def phi_reader(self, file):
        line = 0
        while True:
            line += 1
            d = file.readline()

            if line == 1:
                continue

            if line == 2:
                self.phi_type = int(d.strip())

            if self.phi_type == 0:

                if line == 5:
                    for i in range(self.phi_count):
                        d = file.readline()
                        d = d.strip().split()
                        self.phi_angles.append(float(d[0]))
                        self.phi_parts.append(float(d[1]))

                    break

            elif self.phi_type == 1:
                if line == 3:
                    for i in range(self.phi_count):
                        d = file.readline()
                        self.phi_angles.append(float(d.strip()))
                    break

            elif self.phi_type == 3:
                if line == 4:
                    self.phi_angles.append(float(d.strip()))
                if line == 6:
                    self.phi_angles.append(float(d.strip()))
                    break

    def theta_reader(self, file):
        line = 0
        while True:
            line += 1
            d = file.readline()

            if line == 1:
                continue

            if line == 2:
                self.theta_type = int(d.strip())

            if self.theta_type == 0:

                if line == 5:
                    for i in range(self.theta_count):
                        d = file.readline()
                        d = d.strip().split()
                        self.theta_angles.append(float(d[0]))
                        self.theta_parts.append(float(d[1]))

                    break

            elif self.theta_type == 1 or self.theta_type == -1:
                if line == 3:
                    for i in range(self.theta_count):
                        d = file.readline()
                        self.theta_angles.append(float(d.strip()))
                    break

            elif self.theta_type == 3:
                if line == 4:
                    self.theta_angles.append(float(d.strip()))
                if line == 6:
                    self.theta_angles.append(float(d.strip()))
                    break

    def energy_reader(self, file):
        line = 0
        while True:
            line += 1
            d = file.readline()

            if line == 1:
                continue

            if line == 2:
                self.energy_type = int(d.strip())

            if self.energy_type == 0:

                if line == 5:
                    for i in range(self.energy_count):
                        d = file.readline()
                        d = d.strip().split()
                        self.energy_angles.append(float(d[0]))
                        self.energy_parts.append(float(d[1]))
                    break

            elif self.energy_type == 1:
                if line == 3:
                    for i in range(self.energy_count):
                        d = file.readline()
                        self.energy_angles.append(float(d.strip()))
                    break


            elif self.energy_type == 2:

                if line == 5:
                    for i in range(self.energy_count):
                        d = file.readline()
                        d = d.strip().split()
                        self.energy_angles.append((float(d[0]), float(d[1])))
                        self.energy_parts.append(float(d[2]))

                    break

            elif self.energy_type == 3:
                if line == 4:
                    self.energy_angles.append(float(d.strip()))
                if line == 6:
                    self.energy_angles.append(float(d.strip()))
                    break


if __name__ == '__main__':
    # test_file = r'C:\work\Test_projects\pr_test\PROJECT_1.PL'
    # test_file = r'C:\work\Test_projects\wpala\shpala_new.PL'
    # test_file = r'C:\work\Test_projects\wpala\remp_sources'
    test_file = r'C:\work\Test_projects\KAMERA\Ez_Kamera.pl'
    a = DataParser(test_file)
    out_surf, out_volume, out_boundaries, numbers = a.pl_decoder()
    print(numbers)

    p_file = r'C:\work\Test_projects\wpala\pechs\initials\source'
    print(DataParser('').pech_check_utility(p_file))
    # # print(f' surf  {out_surf}')
    # # print(f' vol  {out_volume}')
    # # print(f' bound  {out_boundaries}')
    # x = a.elph_reader()
    # print(x)

    # a = SpOneReader(test_file)
    # a.start_read()
    # print(a.energy_angles)
    # print(a.energy_parts)
