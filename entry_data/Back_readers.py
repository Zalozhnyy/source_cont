import numpy as np
import os


# class Data_parcer:

def lay_decoder():
    #### .LAY DECODER
    with open(r'KUVSH.LAY', 'r') as file:
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
    print('.LAY  ', out_lay)
    return out_lay


def tok_decoder():
    #### .TOK DECODER
    with open(r'KUVSH.TOK', 'r') as file:
        lines_tok = file.readlines()
    out_tok = np.zeros(2, dtype=int)
    for i in range(len(lines_tok)):
        if '<Начальное поле (0-нет,1-да)>' in lines_tok[i]:
            out_tok[0] = int(lines_tok[i + 1])
        if '<Внешнее поле (0-нет,1-да)>' in lines_tok[i]:
            out_tok[1] = int(lines_tok[i + 1])
    print('.TOK  ', out_tok)
    return out_tok


def pl_decoder():
    #### .PL DECODER
    with open(r'KUVSH.PL', 'r') as file:
        lines_pl = file.readlines()
    for i in range(len(lines_pl)):
        if '<Количество слоев>' in lines_pl[i]:
            pl_numeric = int(lines_pl[i+1])
            out_pl = np.zeros((pl_numeric, pl_numeric), dtype=int)

        if '<Частица номер>' in lines_pl[i]:
            for k in range(pl_numeric):

                out_pl[k, 0] = int(lines_pl[i + 2 + k].split()[0])
                out_pl[k, 1] = int(lines_pl[i + 2 + k].split()[1])
                out_pl[k, 2] = int(lines_pl[i + 2 + k].split()[2])
                out_pl[k, 3] = int(lines_pl[i + 2 + k].split()[3])
                out_pl[k, 4] = int(lines_pl[i + 2 + k].split()[4])
                out_pl[k, 5] = int(lines_pl[i + 2 + k].split()[5])
    print('.PL\n', out_pl)
    return out_pl


if __name__ == '__main__':
    pl_decoder()
