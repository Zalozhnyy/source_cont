import os
import numpy as np
import locale

import re


def get_project_files_dict(prj_path: str):
    try:
        with open(prj_path, 'r', encoding=f'utf-8') as file:
            lines = file.readlines()

    except UnicodeDecodeError:
        with open(prj_path, 'r', encoding=f'{locale.getpreferredencoding()}') as file:
            lines = file.readlines()

    project_dir = os.path.dirname(prj_path)

    out = {}
    for i in range(len(lines)):
        if '<Grd name>' in lines[i]:
            out.setdefault('GRD', lines[i + 1].strip())
        if '<Tok name>' in lines[i]:
            out.setdefault('TOK', lines[i + 1].strip())
        if '<Layers name>' in lines[i]:
            out.setdefault('LAY', lines[i + 1].strip())
        if '<Particles-Layers name>' in lines[i]:
            out.setdefault('PL', None if 'NONE' in lines[i + 1].strip() else lines[i + 1].strip())
        if '<Particles name>' in lines[i]:
            out.setdefault('PAR', None if 'NONE' in lines[i + 1].strip() else lines[i + 1].strip())

    for item, value in out.items():
        if value is not None:
            out[item] = os.path.join(project_dir, value)

    return out


# def permission_denied_test():
#     test_complete = True
#
#     try:
#         test_file = os.path.join(os.path.dirname(__file__), 'permission_denied_test')
#
#         with open(test_file, 'w') as file:
#             file.write('test string')
#
#     except PermissionError:
#         # mb.showerror('Предупреждение', 'Программа не имеет доступа к файловой системе.\n'
#         #                                'Запустите программу от имени администратора')
#         test_complete = False
#
#     finally:
#         if os.path.exists(test_file):
#             os.remove(test_file)
#
#     return test_complete


def pl_decoder(pl_path: str):
    #### .PL DECODER
    try:
        with open(pl_path, 'r', encoding=f'utf-8') as file:
            lines_pl = file.readlines()

    except UnicodeDecodeError:
        with open(pl_path, 'r', encoding=f'{locale.getpreferredencoding()}') as file:
            lines_pl = file.readlines()

    try:
        particle_count = int(lines_pl[2])
        layers = int(lines_pl[6])
        line = 8  # <Layer numbers>
        layers_numbers = np.array(lines_pl[line].strip().split(), dtype=int)
        particle_numbers = np.array(lines_pl[4].strip().split(), dtype=int)

        return particle_numbers, layers_numbers

    except Exception:
        print('Ошибка в чтении файла .PL')
        return None, None


def lay_decoder(lay_path: str):
    #### .LAY DECODER
    try:
        with open(rf'{lay_path}', 'r', encoding=f'utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:

        with open(rf'{lay_path}', 'r', encoding=f'{locale.getpreferredencoding()}') as file:
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
        return None


def par_decoder(par_path: str):
    try:
        with open(par_path, 'r', encoding=f'utf-8') as file:
            lines = file.readlines()

    except UnicodeDecodeError:
        with open(par_path, 'r', encoding=f'{locale.getpreferredencoding()}') as file:
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
        return None


def check_russian_symbols(string: str):
    r = re.compile("[а-яА-Я]")
    res = re.findall(r, string)
    return False if not res else True


def main_test(prj_file_path: str):
    parameters_path_dict = get_project_files_dict(prj_file_path)

    exceptions_messages = {
        'permission_denied':
            'Программа не имеет доступа к файловой системе. Запустите программу от имени администратора',

        'same_layers_numbers_pl_lay_files':
            'Не совпадает количество слоёв в файле PL и LAY. '
            'Запустите интерфейс редактирования файлов LAY/PL для исправления данной ошибки.',

        'same_particles_numbers_pl_lay_files':
            'Не совпадает количество частиц в файле PL и PAR. '
            'Запустите интерфейс редактирования файлов PAR/PL для исправления данной ошибки.',

        'russian_symbols_in_path':
            'Обнаружены русские символы в пути проекта. Возможны ошибки. Удалите русские символы из пути к проекту.',

    }

    # типы возвращаемых массивов nd.array
    if parameters_path_dict['PL'] is None:
        test_passed = {
            'same_layers_numbers_pl_lay_files': True,
            'same_particles_numbers_pl_lay_files': True
        }
        return test_passed, exceptions_messages

    pl_particle, pl_layers = pl_decoder(parameters_path_dict['PL'])
    par_particle = np.array([i['number'] for i in par_decoder(parameters_path_dict['PAR']).values()])
    lay_layers = lay_decoder(parameters_path_dict['LAY'])[:, 0]

    test_passed = {
        # 'permission_denied':
        #     permission_denied_test(),
        'same_layers_numbers_pl_lay_files':
            False if lay_layers.shape != pl_layers.shape else np.all(lay_layers == pl_layers),
        'same_particles_numbers_pl_lay_files':
            False if par_particle.shape != pl_particle.shape else np.all(par_particle == pl_particle),
        'russian_symbols_in_path': not check_russian_symbols(prj_file_path)
    }

    return test_passed, exceptions_messages


if __name__ == '__main__':
    path = r'C:\Users\Zalozhnyy_N\Dropbox\work_cloud\grant\PROJECT_1\PROJECT_1.PRJ'
    main_test(path)
