import numpy as np
import locale


class DataParcer:
    def __init__(self, path):
        self.path = path
        self.decoding_def = locale.getpreferredencoding()
        self.decoding = 'utf-8'

    def lay_decoder(self):
        #### .LAY DECODER
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines = file.readlines()
        except UnicodeDecodeError:

            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines = file.readlines()
        lay_numeric = int(lines[2])
        out_lay = np.zeros((lay_numeric, 3), dtype=int)
        j = 0
        for i in range(len(lines)):
            if '<Номер, название слоя>' in lines[i]:  # 0 - номер слоя  1 - стороннй ток  2 - стро. ист.
                out_lay[j, 0] = int(lines[i + 1].split()[0])
                out_lay[j, 1] = int(lines[i + 3].split()[2])
                out_lay[j, 2] = int(lines[i + 3].split()[3])
                j += 1
        # print('.LAY  ', out_lay)
        return out_lay

    def tok_decoder(self):
        #### .TOK DECODER
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines_tok = file.readlines()
        except UnicodeDecodeError:

            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines_tok = file.readlines()
        out_tok = np.zeros(3, dtype=int)

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

    def pl_decoder(self):
        #### .PL DECODER
        try:
            with open(rf'{self.path}', 'r', encoding=f'{self.decoding}') as file:
                lines_pl = file.readlines()
        except UnicodeDecodeError:

            with open(rf'{self.path}', 'r', encoding=f'{self.decoding_def}') as file:
                lines_pl = file.readlines()

        particle_count = int(lines_pl[2])
        layers = int(lines_pl[6])
        line = 9  # <Движение частицы в слое (вертикаль-слои, горизонталь-частицы) 0-нет/1-да>
        line += 2 * (particle_count + 1)  # <Объемный источник (вертикаль-слои, горизонталь-частицы) 0-нет/1-да>
        line += 2  # <Частица номер> + 1

        out_pl = {}
        lay_number = int(lines_pl[line].strip())
        line += 1
        for i in range(particle_count):
            key_list = []
            for j in range(layers):
                key_list.append(lines_pl[line].split())
                line += 1

            key_list = np.array(key_list, dtype=int)
            out_pl.update({lay_number: key_list})
            line += 2

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
        return out_pl

    def grid_parcer(self):
        #### .PL DECODER
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


if __name__ == '__main__':
    x = DataParcer(r'C:\Users\Никита\Dropbox\work_cloud\source_cont\entry_data\KUVSH.PL').pl_decoder()

    for key in x.keys():
        print(x.get(key))
