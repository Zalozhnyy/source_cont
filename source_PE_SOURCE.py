import os
import sys

sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd

from loguru import logger

import numpy as np

from source_SpectreConfigure import SpectreConfigure
from source_Dialogs import ProgressBar
from source_Project_reader import SubtaskDecoder


@logger.catch()
class PeSource:
    def __init__(self, path, parent):
        super().__init__()

        self.path = path
        self.parent = parent

        self.Energy0 = []
        self.EnergyP = []
        self.spectre_path = ''

        self.N = 0

        self.target_ori = []
        self.source_ori = []

        self.photon_values = None

        self.sub = SubtaskDecoder(self.path)

    def delta_R(self, DOT0, DOT1):
        r = ((DOT0[0] - DOT1[0]) ** 2 + (DOT0[1] - DOT1[1]) ** 2 + (DOT0[2] - DOT1[2]) ** 2) ** 0.5
        return r

    def ro_air(self, h, h0):
        """Density calc formula. Altitude (h) [km]"""
        ro = 1.23 * 10 ** -3 * np.exp(-(h + h0) / 7)
        return ro

    def koord_param(self, x1, x2, t):  # D1-источник  D2- короббка
        x = x1 + (x2 - x1) * t
        return x

    def _tables(self):
        """Find directory pechs/materials and get photon data."""

        materials_path = os.path.normpath(os.path.join(self.path, 'materials'))

        try:
            if os.path.exists(materials_path):
                print(f'{materials_path} exist')
                photon_values_dir = os.path.join(materials_path, 'mat-air/photon/xtbl.23')
                # electron_values_dir = os.path.join(mat_air_path, 'mat-air/electron/xtbl.23')

            else:
                mb.showerror('Dir', f'Директория {materials_path} не найдена.')
                raise Exception(f'Директория {materials_path} не найдена.')

        except Exception:
            ask = mb.askyesno('xtbl path', 'Выбрать файл "xtbl.23" напрямую?')

            if ask is True:
                materials_path = fd.askopenfilename(title='Выберите файл "xtbl.23" для фотонов',
                                                    filetypes=(("xtbl", "*.23*"), ("all files", "*.*")))

                photon_values_dir = materials_path
            else:
                return

        # electron_values = np.loadtxt(electron_values_dir, skiprows=18)
        photon_values = np.loadtxt(photon_values_dir, skiprows=18)

        # electron_values = 10 ** electron_values
        self.photon_values = 10 ** photon_values

    def geometry_calculations(self):

        PT = np.linspace(0, 1, self.N)

        for i in range(len(self.X)):
            self.X[i] = self.koord_param(self.source_ori[0], self.target_ori[0], PT[i])
            self.Y[i] = self.koord_param(self.source_ori[1], self.target_ori[1], PT[i])
            self.Z[i] = self.koord_param(self.source_ori[2], self.target_ori[2], PT[i])
            pr_k = np.array((self.X[i], self.Y[i], self.Z[i]))
            self.R[i] = self.delta_R(self.source_ori, pr_k)

    def density_calculations(self):
        for i in range(self.N):  # расчет плотности
            if i == 0:
                self.ro[i] = self.ro_air(0, self.source_ori[2])
            else:
                if self.source_ori[2] > self.target_ori[2]:
                    self.ro[i] = self.ro_air(0, self.Z[i])
                else:
                    self.ro[i] = self.ro_air(self.Z[i] - self.Z[0], self.source_ori[2])

    def energy_reduction_calculation(self, energy, energy_part):

        Energy_reduction = np.empty(0)
        Energy_reduction = np.append(Energy_reduction, energy_part)

        KSI = np.interp(energy * 10 ** 6, self.photon_values[:, 0], self.photon_values[:, 1])
        lam = KSI * self.ro  # cm**2/g * g/cm**3 ------- 1/cm

        for i in range(1, self.N):
            val = Energy_reduction[i - 1] * np.exp(
                -(self.R[i] * 10 ** 5 - self.R[i - 1] * 10 ** 5) * lam[i])

            Energy_reduction = np.append(Energy_reduction, val)

        Energy_reduction[-1] = Energy_reduction[-1] / (4 * np.pi * (self.R[-1] * 10 ** 5) ** 2)

        # print(f'{energy}   :  {Energy_reduction[0]} --- {Energy_reduction[-1]}')

        return Energy_reduction[-1]

    def create_arrays(self):
        self.X = np.zeros(self.N, dtype=float)
        self.Y = np.zeros(self.N, dtype=float)
        self.Z = np.zeros(self.N, dtype=float)
        self.R = np.zeros(self.N, dtype=float)
        self.ro = np.zeros(self.N, dtype=float)

        self.sum_dol = np.zeros((len(self.Energy0), self.N), dtype=float)
        self.out_spectre = np.zeros((len(self.Energy0), 2), dtype=float)

    def save(self):
        mb.showinfo('SAVE', 'Выберите место сохранения ослабленного спектра.')
        save_path = fd.asksaveasfilename(title=f'Выберите место сохранения ослабленного спектра',
                                         initialdir=self.path,
                                         filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))

        if save_path == '':
            return

        if self.sp_ds.spectre_type == 5 and self.sp_ds.five_spectre_type == 0:
            save_array = np.column_stack((self.sp_ds.old_data[:, 1] * 1e3, self.out_spectre[:, 1]))

            header = f'SP_TYPE=DISCRETE\n' \
                     f'[DATA]'

        elif self.sp_ds.spectre_type == 5 and self.sp_ds.five_spectre_type == 1:
            save_array = np.column_stack((self.sp_ds.old_data[:, 2] * 1e3, self.out_spectre[:, 1]))

            header = f'SP_TYPE=CONTINUOUS\n' \
                     f'[DATA]\n' \
                     f'{self.sp_ds.old_data[0, 0]}'

        elif self.sp_ds.spectre_type == 'DISCRETE':
            save_array = self.out_spectre[:, :]

            header = f'SP_TYPE=DISCRETE\n' \
                     f'[DATA]'

        elif self.sp_ds.spectre_type == 'CONTINUOUS':
            save_array = np.column_stack((self.sp_ds.old_data[1:, 0], self.out_spectre[:, 1]))

            header = f'SP_TYPE=CONTINUOUS\n' \
                     f'[DATA]\n' \
                     f'{self.sp_ds.old_data[0, 0]}'
        else:
            return

        # print(save_array)
        np.savetxt(save_path, save_array, header=header, comments='', delimiter='\t',
                   fmt=['%.3g', '%.6g'])
        mb.showinfo('Сохранено', f'Сохранено в {save_path}')

    def main_calculation(self):

        if self.sub.subtask_struct is None:

            top_level_root = tk.Toplevel(self.parent)
            top_level_root.grab_set()

            ex = SpectreConfigure(self.path, top_level_root)
            ex.grid(sticky='NWSE')

            ex.spectre_type_combobox_values = ['Упрощённый перенос ИИ',
                                               'Дискретный',
                                               'Непрерывный']
            ex.spetre_type_cobbobox.configure(value=[val for val in ex.spectre_type_combobox_values])
            print('subtask Не обнаружен')

            return

        else:

            source = ('0',
                      '0',
                      self.sub.subtask_struct['altitude'])

            source = list(map(float, source))
            source = [i * 10 ** -5 for i in source]

            target = (self.sub.subtask_struct['source_position']['x'],
                      self.sub.subtask_struct['source_position']['y'],
                      0)

            target = list(map(float, target))
            target[-1] = float(self.sub.subtask_struct['altitude']) + float(
                self.sub.subtask_struct['source_position']['z'])
            target = [i * 10 ** -5 for i in target]

            self.source_ori = np.array(source)
            self.target_ori = np.array(target)

            self.R0 = ((self.target_ori[0] - self.source_ori[0]) ** 2 +
                       (self.target_ori[1] - self.source_ori[1]) ** 2 +
                       (self.target_ori[2] - self.source_ori[2]) ** 2) ** 0.5

            if self.R0 == 0:
                mb.showerror('Ошибка', 'Местоположение объекта совпадает с местоположением источника.')
                return
            mb.showinfo('SUBTASK', 'Обнаружен файл локальной задачи.\nВыберите спектр для ослабления.')

            print(f'source {self.source_ori}')
            print(f'object {self.target_ori}')

            spectre_path = fd.askopenfilename(title=f'Выберите спектр типа 5 или переноса',
                                              initialdir=self.path,
                                              filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))

            if spectre_path == '':
                self.spectre_path = spectre_path
                return

            self.spectre_path = spectre_path

            self.sp_ds = SpectreDataWithConvertation(self.spectre_path)

            if self.sp_ds.data is None:
                return

            ar = self.sp_ds.data

            self.Energy0 = ar[:, 0]
            self.EnergyP = ar[:, 1]

            if self.source_ori[-1] == self.target_ori[-1]:
                mb.showerror('SUBTASK info', 'Высота источника и объекта совпадают')

            self.N = int(round(self.R0) / 4000 * 2000000)
            if self.N < 1000:
                self.N = 1000
            print(f'ШАГ {self.R0 / 4000}')
            print(f'Число ячеек {self.N}')

            self._tables()
            if self.photon_values is None:
                return
            self.create_arrays()

            print('Расчёт начат')

            self.geometry_calculations()

            self.density_calculations()

            pb = ProgressBar(self.parent)
            one_step = 100 / self.Energy0.shape[0]

            for i in range(self.Energy0.shape[0]):
                er = self.energy_reduction_calculation(self.Energy0[i], self.EnergyP[i])
                self.out_spectre[i, 0], self.out_spectre[i, 1] = self.Energy0[i], er

                pb.update_progress(one_step)

            pb.update_directly(100)
            pb.onExit()

            print('Расчёт завершен')

            self.save()


class SpectreDataWithConvertation:
    def __init__(self, path):
        self.spectre_path = path

        self.spectre_type = None

        self.data = None
        self.old_data = None
        self.five_spectre_type = None

        self.spectre_type_identifier()

    def spectre_type_identifier(self):
        with open(self.spectre_path, 'r') as file:
            lines = file.readlines()

        if 'SP_TYPE=CONTINUOUS' in lines[0]:
            self.spectre_type = 'CONTINUOUS'

        elif 'SP_TYPE=DISCRETE' in lines[0]:
            self.spectre_type = 'DISCRETE'

        else:
            try:
                self.spectre_type = int(lines[6].strip())
                if self.spectre_type != 5:
                    print('Спектр не подходит')
                    mb.showerror('Ошибка','тип спектра не подходит.')
                    self.data = None
                    return
            except:
                print('Тип спектра не опознан')
                self.data = None
                return

        self.start_read()

    def start_read(self):

        if self.spectre_type == 5:
            self.data = np.loadtxt(self.spectre_path, skiprows=16, dtype=float)

            self.old_data = self.data.copy()

            if self.data.shape[1] == 5:
                self.data = self.data[:, 1:3]
                self.five_spectre_type = 0
            elif self.data.shape[1] == 7:
                self.data = self.data[:, 3:5]
                self.five_spectre_type = 1

        if self.spectre_type == 'DISCRETE':
            self.data = np.loadtxt(self.spectre_path, skiprows=2, dtype=float)

        if self.spectre_type == 'CONTINUOUS':
            self.data = np.loadtxt(self.spectre_path, skiprows=3, dtype=float)

            with open(self.spectre_path, 'r') as file:
                lines = file.readlines()

            start = (lines[2].strip())

            self.data = np.insert(self.data, 0, [start, None], axis=0)

            self.old_data = self.data.copy()

            self.data = np.zeros((self.old_data.shape[0] - 1, 2), dtype=float)

            for i in range(1, self.old_data.shape[0]):
                self.data[i - 1, 0] = (self.old_data[i - 1, 0] + self.old_data[i, 0]) / 2
                self.data[i - 1, 1] = self.old_data[i, 1]


if __name__ == '__main__':

    def destr():
        root.quit()
        root.destroy()


    root = tk.Tk()

    try:
        print(f'Проект {projectfilename}')
        ini = os.path.normpath(os.path.dirname(projectfilename))
    except:
        mb.showerror('error', 'Проект не выбран')
        destr()
        exit()

    ex = PeSource(ini, root)

    ex.main_calculation()

    destr()
    root.mainloop()
