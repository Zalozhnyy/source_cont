import numpy as np
import locale


class DataParcer:
    def __init__(self, path):
        self.path = path
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
            line = 9  # <Движение частицы в слое (вертикаль-слои, горизонталь-частицы) 0-нет/1-да>
            line += 2 * (particle_count + 1)  # <Объемный источник (вертикаль-слои, горизонталь-частицы) 0-нет/1-да>
            line += 1  # <Частица номер>

            out_pl = {}

            for i in range(particle_count):
                line += 1
                lay_number = int(lines_pl[line].strip())

                key_list = []
                for j in range(layers):
                    line += 1
                    key_list.append(lines_pl[line].split())

                key_list = np.array(key_list, dtype=int)
                out_pl.update({lay_number: key_list})
                line += 1
            return out_pl

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
            L = []
            L.append(int(lines[2].strip()))

            string_num = 6
            for numbers in range(L[0]):
                L.append(int(lines[string_num + 1].split()[0]))
                string_num += 4  # <Количество процессов>
                string_num += 2 * int(lines[string_num + 1].strip()) + 1
                string_num += 4  # переход к следующему кластеру

            return L[0], L[1:]

        except Exception:
            print('Ошибка в чтении файла .PL')
            return

    def remp_source_decoder(self):
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines = file.readlines()

        out_dict = {}
        value = {}
        for i, line in enumerate(lines):

            if '<source name>' in line:
                key = lines[i + 1].strip()
                if 'Current' in key or 'Sigma' in key:
                    key = 'Current and Sigma'
            if '<amplitude>' in line:
                value.update({'amplitude': float(lines[i + 1].strip())})
            if '<time function>' in line:
                t = lines[i + 2].split()
                t = [float(i) for i in t]
                value.update({'time': t})
                f = lines[i + 3].split()
                f = [float(i) for i in f]
                value.update({'value': f})

                out_dict.update({key: value})

        return out_dict


if __name__ == '__main__':
    test_file = r'C:\Users\Никита\Dropbox\work_cloud\source_cont\entry_data\remp_sources'
    x = DataParcer(test_file).remp_source_decoder()

    print(x)
