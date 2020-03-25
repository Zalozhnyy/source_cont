import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import numpy as np
import os


from utility import  config_read


class PeSource(tk.Toplevel):
    def __init__(self, parent=None, name='Gursa_N'):
        super().__init__(parent)

        self.name = name
        self.spectr = []
        self.spectr_cont = []
        self.Energy0 = []
        self.EnergyP = []
        self.spectr_path = ''
        self.Spektr_output = []
        self.calc_state = 0

        self.generate = 0
        self.generate_val = tk.StringVar()
        self.func_val = []
        self.dol_val = []
        self.entry_func = []
        self.entry_dol = []

        self.grab_set()
        self.focus()

        self.child_window()
        print(repr(self))


    def child_window(self):
        self.title('PE source')
        self.geometry('800x300')

        rows = 0
        while rows < 30:
            self.rowconfigure(rows, weight=0, minsize=3)
            self.columnconfigure(rows, weight=0, minsize=3)
            rows += 1

        x_y_z = ['X', 'Y', 'Z']
        label_names = ['Координаты источника (км)', 'Координаты объекта (км)', 'Число ячеек сетки']
        self.entry_koord_ist_val = [tk.StringVar() for _ in range(3)]
        self.entry_koord_obj_val = [tk.StringVar() for _ in range(3)]
        self.entry_koord_ist_val[0].set('0')
        self.entry_koord_ist_val[1].set('0')
        self.entry_koord_ist_val[2].set('40')
        self.entry_koord_obj_val[0].set('0')
        self.entry_koord_obj_val[1].set('0')
        self.entry_koord_obj_val[2].set('60')
        self.entry_grid_value = tk.StringVar()
        self.entry_grid_value.set('1000')
        tk.Entry(self, textvariable=self.entry_grid_value, width=9).grid(row=3, column=1)

        for i in range(3):
            entry_koord_ist = tk.Entry(self, textvariable=self.entry_koord_ist_val[i], width=9)
            entry_koord_ist.grid(row=1, column=1 + i, padx=1, pady=2)
            tk.Label(self, text=x_y_z[i]).grid(row=0, column=1 + i)
            tk.Label(self, text=label_names[i]).grid(row=1 + i, column=0, sticky='W')
        for i in range(3):
            entry_koord_ist = tk.Entry(self, textvariable=self.entry_koord_obj_val[i], width=9)
            entry_koord_ist.grid(row=2, column=1 + i, padx=1, pady=2)

        self.button_browse_spectr = tk.Button(self, text='Browse',
                                              command=self.take_spectr, state='normal')
        self.button_browse_spectr.grid(row=1, column=5, padx=5)
        self.button_rasch = tk.Button(self, text='Calc', command=self.main, state='disabled')
        self.button_rasch.grid(row=5, column=0)

        self.button_generate = tk.Button(self, text='Сгенерировать', command=self.ent)
        self.button_generate.grid(row=5, column=3, columnspan=3)
        self.generate_entry = tk.Entry(self, textvariable=self.generate_val, width=5)
        self.generate_entry.grid(row=5, column=2)

        self.spectr_type = tk.IntVar()

        self.radio_cont = tk.Radiobutton(self, text='CONTINUOUS', variable=self.spectr_type, value=0)
        self.radio_cont.grid(row=1, column=6, sticky="W")
        radio_dis = tk.Radiobutton(self, text='DISCRETE', variable=self.spectr_type, value=1)
        radio_dis.grid(row=2, column=6, sticky="W")
        self.spectr_type.set(0)

    def take_spectr(self):
        if self.generate == 0:
            path = fd.askopenfilename(title='Выберите файл spectr',
                                      filetypes=(("all files", "*.*"), ("txt files", "*.txt*")))
            # path = 'spectr_3_49_norm_na_1.txt'
            with open(path, 'r', encoding='utf-8') as file_handler:
                i = 0
                s = []
                if self.spectr_type.get() == 0:
                    for line in file_handler:
                        i += 1
                        if 'SP_TYPE=DISCRETE' in line:
                            mb.showerror('Spectr error', 'Выбран спектр DISCRETE')
                            break
                        if i < 3: continue
                        if len(line.split()) < 2:
                            # print(type(s))
                            line = line + '0'
                            s.append(line.split())
                        else:
                            s.append(line.split())

                    out = np.array(s, dtype=float)
                    self.spectr_cont = np.copy(out)
                    for i in range(len(out) - 1):
                        out[i, 0] = (out[i, 0] + out[i + 1, 0]) / 2
                        out[i, 1] = out[i + 1, 1]
                    out = np.delete(out, np.s_[-1:], 0)
                elif self.spectr_type.get() == 1:
                    for line in file_handler:
                        if 'SP_TYPE=CONTINUOUS' in line:
                            mb.showerror('Spectr error', 'Выбран спектр CONTINUOUS')
                            break
                    out = np.loadtxt(path, skiprows=2)

                self.button_rasch.configure(state='normal')
                self.spectr = out

            self.button_rasch.configure(state='normal')
            # print(self.spectr)

    def ent(self):

        if len(self.entry_func) > 0:
            for ent in self.entry_func:
                ent.destroy()
            self.entry_func.clear()

            for ent in self.entry_dol:
                ent.destroy()
            self.entry_dol.clear()

        self.func_val.clear()
        self.dol_val.clear()

        tk.Label(self, text='Energy , кЭв').grid(row=6, column=1)
        tk.Label(self, text='Доля').grid(row=6, column=2)
        self.func_val = [tk.StringVar() for _ in range(int(self.generate_val.get()))]
        self.dol_val = [tk.StringVar() for _ in range(int(self.generate_val.get()))]

        for i in range(int(self.generate_val.get())):
            self.entry_func.append(tk.Entry(self, width=9, textvariable=self.func_val[i], justify='center'))
            self.entry_func[i].grid(row=8 + i, column=1, pady=2)
            self.entry_dol.append(tk.Entry(self, width=9, textvariable=self.dol_val[i], justify='center'))
            self.entry_dol[i].grid(row=8 + i, column=2, pady=2)

        self.generate = 1

        self.button_browse_spectr.configure(state='disabled')
        self.button_rasch.configure(state='normal')

        if len(self.entry_dol) == 1:
            self.spectr_type.set(1)
            self.radio_cont.configure(state='disabled')
        else:
            self.radio_cont.configure(state='normal')

    def delta_R(self, DOT0, DOT1):
        r = ((DOT0[0] - DOT1[0]) ** 2 + (DOT0[1] - DOT1[1]) ** 2 + (DOT0[2] - DOT1[2]) ** 2) ** 0.5
        return r

    def ro_air(self, h, h0):
        ro = 1.23 * 10 ** -3 * np.exp(-(h + h0) / 7)
        return ro

    def koord(self, x1, y1, z1):
        A = np.array((x1, y1, z1), dtype=float)
        return A

    def koord_param(self, x1, x2, t):  # D1-источник  D2- короббка
        x = x1 + (x2 - x1) * t
        return x

    def main(self):

        self.M2 = self.koord(self.entry_koord_ist_val[0].get(),
                             self.entry_koord_ist_val[1].get(),
                             self.entry_koord_ist_val[2].get())
        self.M1 = self.koord(self.entry_koord_obj_val[0].get(),
                             self.entry_koord_obj_val[1].get(),
                             self.entry_koord_obj_val[2].get())
        try:
            if any([val < 0 for val in self.M2]) or any([val < 0 for val in self.M1]):
                mb.showerror('Koord error', 'Введите положительные значения')
                raise Exception
        except Exception:
            print(self.M2)
            print(self.M1)
            return print('Введите положительные значения')

        N = int(self.entry_grid_value.get())

        # Блок чтения ручной генерации
        if self.generate == 1:

            if self.spectr_type.get() == 1:

                out = np.zeros((len(self.func_val), 2), dtype=float)
                for i in range(len(self.func_val)):
                    out[i, 0] = float(self.func_val[i].get())
                    out[i, 1] = float(self.dol_val[i].get())

                self.spectr = out

            elif self.spectr_type.get() == 0:

                out = np.zeros((len(self.func_val), 2), dtype=float)
                for i in range(len(self.func_val)):
                    out[i, 0] = float(self.func_val[i].get())
                    out[i, 1] = float(self.dol_val[i].get())

                self.spectr_cont = np.copy(out)

                for i in range(len(out) - 1):
                    out[i, 0] = (out[i, 0] + out[i + 1, 0]) / 2
                    out[i, 1] = out[i + 1, 1]

                out = np.delete(out, np.s_[-1:], 0)

                self.spectr = out

        # __________________________________

        self.Energy0 = self.spectr[:, 0] * 10 ** -3  # энергия должна быть в МэВ
        self.EnergyP = self.spectr[:, 1]

        self.Spektr_output = np.zeros((len(self.Energy0), 2), dtype=float)

        # БЛОК ЧТЕНИЯ ТАБЛИЦ ПОСТОЯННЫХ

        materials_path = os.path.join(config_read()[0], 'pechs\materials')

        try:
            if os.path.exists(materials_path):
                print(f'{materials_path} exist')
                photon_values_dir = os.path.join(materials_path, 'mat-air/photon/xtbl.23')
                # electron_values_dir = os.path.join(materials_path, 'mat-air/electron/xtbl.23')

            else:
                mb.showerror('Dir',f'Директория {materials_path} не найдена.')
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
        photon_values = 10 ** photon_values

        sum_dol = np.zeros((len(self.Energy0), N), dtype=float)

        for j in range(len(self.Energy0)):

            Lx = self.M1[0] - self.M2[0]
            Ly = self.M1[1] - self.M2[1]
            Lz = self.M1[2] - self.M2[2]
            dx = Lx / N
            dy = Ly / N
            dz = Lz / N
            PT = np.linspace(0, 1, N)

            R0 = ((self.M1[0] - self.M2[0]) ** 2 + (self.M1[1] - self.M2[1]) ** 2 + (
                    self.M1[2] - self.M2[2]) ** 2) ** 0.5

            X = np.zeros(N, dtype=float)
            Y = np.zeros(N, dtype=float)
            Z = np.zeros(N, dtype=float)
            R = np.zeros(N, dtype=float)
            ro = np.zeros(N, dtype=float)

            for i in range(len(X)):
                X[i] = self.koord_param(self.M2[0], self.M1[0], PT[i])
                Y[i] = self.koord_param(self.M2[1], self.M1[1], PT[i])
                Z[i] = self.koord_param(self.M2[2], self.M1[2], PT[i])
                pr_k = np.array((X[i], Y[i], Z[i]))
                R[i] = self.delta_R(self.M2, pr_k)

            for i in range(N):  # расчет плотности
                if i == 0:
                    ro[i] = self.ro_air(0, self.M2[2])
                else:
                    if self.M2[2] > self.M1[2]:
                        ro[i] = self.ro_air(0, Z[i])
                    else:
                        ro[i] = self.ro_air(Z[i] - Z[0], self.M2[2])

            Energy_reduction = np.zeros(N, dtype=float)
            lam = np.zeros(N, dtype=float)
            Energy_reduction[0] = self.EnergyP[j]
            sum_dol[j, 0] = self.EnergyP[j]

            KSI = np.interp(self.Energy0[j] * 10 ** 6, photon_values[:, 0], photon_values[:, 1])

            for i in range(N):
                lam[i] = KSI * ro[i]  # cm**2/g * g/cm**3 ------- 1/cm
            for i in range(1, N):
                Energy_reduction[i] = Energy_reduction[i - 1] * np.exp(
                    -(R[i] * 10 ** 5 - R[i - 1] * 10 ** 5) * lam[i])
                sum_dol[j, i] = Energy_reduction[i]

            self.Spektr_output[j, 1] = Energy_reduction[-1] * (4 * np.pi * (R0 * 10 ** 5) ** 2) ** -1

        sum_dol_out = sum_dol.sum(axis=0)

        for i in range(1, N):
            sum_dol_out[i] = sum_dol_out[i] * (4 * np.pi * (R[i] * 10 ** 5) ** 2) ** -1


        if self.spectr_type.get() == 1:
            self.Spektr_output[:, 0] = self.Energy0 * 10 ** 3

        elif self.spectr_type.get() == 0:
            self.Spektr_output[:, 0] = self.spectr_cont[1:, 0]
            for i in range(len(self.Spektr_output) - 1, 0, -1):
                self.Spektr_output[i, 1] = self.Spektr_output[i - 1, 1]

        self.pe_source_graph = np.column_stack((R[1:], sum_dol_out[1:]))
        # print(self.pe_source_graph)

        self.calc_state = 1

        self.destroy()

    # def name_transfer(self):
    #     if self.spectr_type.get() == 1:
    #         type = 'DISCRETE'
    #     elif self.spectr_type.get() == 0:
    #         type = 'CONTINUOUS'
    #     return type
