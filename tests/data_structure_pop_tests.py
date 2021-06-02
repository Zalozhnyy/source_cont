import pytest

from dataclasses import dataclass
import numpy as np
import os
import pickle
from typing import Dict

from source_Project_reader import DataParser
from source_utility import TreeDataStructure

pl_file_test = '''Описание взаимодействия частиц и слоев
<Number of particles>
2
<Particle numbers>
1  2  
<Number of layers>
2
<Layer numbers>
0  1  
<Particle motion in a layer (vertical-layers, horizontal-particles) 0-No/1-Yes>
1  0  
1  0  
<Source in volume (vertical-layers, horizontal-particles) 0-No/1-Yes/2-Random>
1  0  
1  0  
<Surface source (vertical - from layer, horizontal - into layer) 0-No/1-Yes/2-Random>
<Particle number>
1
0  1  
0  0  
<Particle number>
2
0  1  
0  0  
<Current density calculation (vertical-layers, horizontal-particles) 0-No/1-Yes>
1  0  
1  0  
<Ionization inhibition (vertical-layers, horizontal-particles) 0-No/1-Yes>
1  0  
1  0  
<Ionization source (vertical-layers, horizontal-particles) 0-No/1-Yes>
1  0  
1  0  
<Elastic scattering (vertical-layers, horizontal-particles) 0-No/1-Yes>
0  0  
0  0  
<Particle number>
1
<Source from the boundaries of the region(X,Y,Z;-X,-Y,-Z) 0-No/1-Yes>
1 1 1 1 1 1
<Particle number>
2
<Source from the boundaries of the region(X,Y,Z;-X,-Y,-Z) 0-No/1-Yes>
1 1 1 1 1 1

'''

par_file_test = '''Описание частиц
<Number of particle types>
2

<Type(1-electron, 2-positron, 3-quantum), Name>
1 Электрон_X
<Number, charge(el.), mass(g), self-consistency(0-No, 1-Yes), braking(0-No, 1-Yes), scattering(0-No, 1-Yes)>
1    -1    9.108e-28    1    1    0
<Kinetic еnergy Barrier(MeV)>
1e-06
<Number of processes>
7
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
4  0  2  1  2
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
7  0  1  1  0
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
8  0  1  1  0
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
9  0  1  1  0
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
10  0  2  1  1
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
11  0  0  0  0
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
12  0  0  0  0

<Type(1-electron, 2-positron, 3-quantum), Name>
1 Электрон_G
<Number, charge(el.), mass(g), self-consistency(0-No, 1-Yes), braking(0-No, 1-Yes), scattering(0-No, 1-Yes)>
2    -1    9.108e-28    1    1    0
<Kinetic еnergy Barrier(MeV)>
1e-06
<Number of processes>
7
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
4  0  2  1  2
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
7  0  1  1  0
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
8  0  1  1  0
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
9  0  1  1  0
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
10  0  2  1  1
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
11  0  0  0  0
<Process number, process(0-No, 1-Yes), number of particles born(0-2), numbers of particles born>
12  0  0  0  0

'''

lay_file_test = '''
<Number of layers>
2

<Number, layer name>
0   air
<p/p N, conduct. N, ext. J (0-no,1-yes), ext. sec. el. (0-no,1-yes), extra opt. (0-no,1-yes)>
1     5     0     0     1
<material(N), density (g/cm**3), temp.[C], diel. const, magnetic perm., conductivity>
3     1.24e-05     20     1     1     0
<molecular weight[g/mole], atoms in molecule[], average core charge[el.], ionization cost[eV]>
0     0     0     34

<Number, layer name>
1   Fe
<p/p N, conduct. N, ext. J (0-no,1-yes), ext. sec. el. (0-no,1-yes), extra opt. (0-no,1-yes)>
1     0     0     0     0
<material(N), density (g/cm**3), temp.[C], diel. const, magnetic perm., conductivity>
1     7.8     20     1     1     3.4e+17

'''


@dataclass
class ProjectData:
    PL_surf: dict
    PL_vol: dict
    PL_bound: dict
    layer_numbers: dict
    LAY: dict
    PPN: dict
    PAR: dict


class PreviousProjectLoader:
    """
    Класс предназначен для сопоставления данных из загрузки и проектных данных.
    Осуществляет удаление из БД несуществующих в преокте абстракций.
    """

    def __init__(self, path: str, project_data: list):
        self.loaded_flag = False
        self.path = path

        self.global_tree_db = {}
        self._marple, self._micro_electronics = {}, {}
        self.PAR, self.LAY, self.PL_surf, self.PL_vol, self.PL_bound, self.layer_numbers = project_data

        self.__start_reading()

    def __reform_flux_spectres(self, obj: TreeDataStructure):

        for f_key in obj.get_first_level_keys():
            for s_key in obj.get_second_level_keys(f_key):
                if 'Flu' in s_key:
                    sp_old = obj.get_last_level_data(f_key, s_key, 'spectre')
                    num_old = obj.get_last_level_data(f_key, s_key, 'spectre numbers')

                    obj.insert_third_level(f_key, s_key, 'spectre',
                                           [sp for sp in sp_old if DataParser(self.path).spc_non_empty(sp)])
                    obj.insert_third_level(f_key, s_key, 'spectre numbers',
                                           [num for sp, num in zip(sp_old, num_old) if
                                            DataParser(self.path).spc_non_empty(sp)])

    def get_db_and_lag(self):
        lag = self.global_tree_db[list(self.global_tree_db.keys())[0]].get_share_data('lag')
        return self.global_tree_db, lag

    def __delete_particles(self, db):
        delete_part_list = set()

        for f_key in db.get_first_level_keys():
            if 'Sigma' not in f_key and 'Current' not in f_key and 'Energy' not in f_key:
                part = db.get_share_data('particle number')

                if type(part) is set:
                    part = list(part)

                if type(part) is list:
                    for part_number in part:
                        if all([part_number != self.PAR[k]['number'] for k in self.PAR.keys()]):
                            delete_part_list.add(f_key)

                # условие нужно для подержки старых версий баз данных, после сохранения они переходят в новый формат
                elif type(part) is int:
                    if all([part != self.PAR[k]['number'] for k in self.PAR.keys()]):
                        delete_part_list.add(f_key)

        for dk in delete_part_list:
            db.delete_first_level(dk)

    def __start_reading(self):
        if not os.path.exists(os.path.join(self.path, 'Sources.pkl')):
            print('Загрузка невозможна. Файл Sources.pkl не найден')
            return

        try:
            with open(os.path.join(self.path, 'Sources.pkl'), 'rb') as f:
                self.global_tree_db = pickle.load(f)
        except Exception:
            print('Ошибка при попытке прочитать бинарный файл сохранения. Загрузка невозможна.')
            return

        for i in self.global_tree_db.items():
            self.__delete_particles(i[1])

        for i in self.global_tree_db.items():
            """Удаляем источники, которых нет в текущих файлах проекта, но есть в загрузке"""
            self.__tree_db_delete_old(i[1])
            # self.__reform_flux_spectres(i[1])

        self._marple, self._micro_electronics = DataParser(self.path).load_marple_data_from_remp_source()
        self.loaded_flag = True

    def __tree_db_delete_old(self, obj):
        try:
            part_number_tuple = obj.get_share_data('particle number')
        except KeyError:
            part_number_tuple = None

        # удаление из базы данных несуществующих частиц
        delete_part_list = set()

        """удаление источников energy для совместимости старых source.pkl удалить при добавлении источника energy"""
        for f_key in obj.get_first_level_keys():
            if f_key == 'Energy':
                delete_part_list.add(f_key)

        if len(delete_part_list) != 0:
            for f_key in delete_part_list:
                if len(obj.get_second_level_keys(f_key)) == 0:
                    obj.replace_legacy_energy_to_sigma({})
                else:
                    for key2 in obj.get_second_level_keys(f_key):
                        name = obj.get_last_level_data(f_key, key2, 'name').replace('Energy', 'Sigma')
                        energy_type = 'Sigma'
                        distribution = obj.get_last_level_data(f_key, key2, 'name')

                        insert_dict = {name: {
                            'name': name,
                            'energy_type': energy_type,
                            'distribution': distribution
                        }
                        }

                        obj.replace_legacy_energy_to_sigma(insert_dict)

        if part_number_tuple is None and len(delete_part_list) == 0:
            return

        db_s_keys = set()

        for f_key in obj.get_first_level_keys():
            for s_key in obj.get_second_level_keys(f_key):
                db_s_keys.add(s_key)

        for f_key in obj.get_first_level_keys():
            if self.PAR is None:
                continue
            if f_key not in self.PAR.keys() and f_key != 'Current' and f_key != 'Sigma':
                delete_part_list.add(f_key)

        for f_key in delete_part_list:
            obj.delete_first_level(f_key)

        for key in db_s_keys:
            if 'Current' in key:
                cur_lay = np.where(self.layer_numbers == int(key.split('_')[-1]))
                self.__delete_source_safely((lambda: self.LAY[cur_lay, 1] == 0), obj, key)
            if 'Sigma' in key:
                cur_lay = np.where(self.layer_numbers == int(key.split('_')[-1]))
                self.__delete_source_safely(lambda: (self.LAY[cur_lay, 2] == 0), obj, key)
            if 'Flu' in key:
                from_l = np.where(self.layer_numbers == int(key.split('_')[-2]))
                to_l = np.where(self.layer_numbers == int(key.split('_')[-1]))
                part_number = int(key.split('_')[-3])
                self.__delete_source_safely(lambda: (self.PL_surf[part_number][to_l, from_l] == 0), obj, key)
            if 'Volume78' == key.split('_')[0]:
                vol_lay = np.where(self.layer_numbers == int(key.split('_')[-1]))
                part_number = int(key.split('_')[-2])
                self.__delete_source_safely(lambda: (self.PL_vol[part_number][vol_lay] == 0), obj, key)
            if 'Volume' == key.split('_')[0]:
                vol_lay = np.where(self.layer_numbers == int(key.split('_')[-1]))
                part_number = int(key.split('_')[-2])
                self.__delete_source_safely(lambda: self.PL_vol[part_number][vol_lay] == 0, obj, key)
            if 'Boundaries' in key:
                boundaries_decode = {0: 'X', 1: 'Y', 2: 'Z', 3: '-X', 4: '-Y', 5: '-Z'}
                bo_lay_k = key.split('_')[-1]
                part_number = int(key.split('_')[-2])
                for i in boundaries_decode.items():
                    if i[1] == bo_lay_k:
                        bo_lay = i[0]
                        break
                self.__delete_source_safely(lambda: (self.PL_bound[part_number][bo_lay] == 0), obj, key)

        delete_f_level_set = set()
        for f_key in obj.get_first_level_keys():  # удаляем пустые сущности частиц
            if len(obj.get_first_level_value(f_key)) == 0 and f_key != 'Current' and f_key != 'Sigma':
                delete_f_level_set.add(f_key)

        for f_key in delete_f_level_set:
            obj.delete_first_level(f_key)

    def __delete_source_safely(self, statment, data_object, key):
        try:
            if statment():
                data_object.delete_second_level(key)

        except Exception as e:
            print(e)
            print(f'Ошибка удаления источника {key}')


def get_all_sources(db: Dict[str, TreeDataStructure]):
    sources = []
    for primary_key in db.keys():
        for fk in db[primary_key].get_first_level_keys():
            for sk in db[primary_key].get_second_level_keys(fk):
                sources.append(sk)
    return sources


def get_all_particles(db: Dict[str, TreeDataStructure]):
    particles = []
    for primary_key in db.keys():
        for fk in db[primary_key].get_first_level_keys():
            particles.append(fk)
    return particles


def init_test_data():
    ex = DataParser(None)

    surf, vol, bound, layer_numbers = ex.pl_decoder(pl_file_test.split('\n'))
    lay, ppn = ex.lay_decoder(lay_file_test.split('\n'))
    par = ex.par_decoder(par_file_test.split('\n'))

    data = ProjectData(surf, vol, bound, layer_numbers, lay, ppn, par)

    return data


def test_delete_flux_source():
    with open('Sources.pkl', 'rb') as f:
        loaded_db = pickle.load(f)

    pkl_sources = get_all_sources(loaded_db)

    d = init_test_data()
    part_number = 1
    from_layer = 1
    to_layer = 0

    deleted_source = f'Flu_e_{part_number}_{from_layer}_{to_layer}'

    d.PL_surf[part_number][to_layer, from_layer] = 0

    ex = PreviousProjectLoader(os.path.dirname(__file__),
                               [d.PAR, d.LAY, d.PL_surf, d.PL_vol, d.PL_bound, d.layer_numbers])
    read_data_sources = get_all_sources(ex.global_tree_db)

    assert deleted_source not in read_data_sources
    assert deleted_source in pkl_sources


def test_delete_volume_source():
    with open('Sources.pkl', 'rb') as f:
        loaded_db = pickle.load(f)

    pkl_sources = get_all_sources(loaded_db)

    d = init_test_data()
    part_number = 1
    layer = 0

    deleted_source = f'Volume_{part_number}_{layer}'

    d.PL_vol[part_number][d.layer_numbers[layer]] = 0

    ex = PreviousProjectLoader(os.path.dirname(__file__),
                               [d.PAR, d.LAY, d.PL_surf, d.PL_vol, d.PL_bound, d.layer_numbers])
    read_data_sources = get_all_sources(ex.global_tree_db)

    assert deleted_source not in read_data_sources
    assert deleted_source in pkl_sources


def test_delete_boundaries_source():
    boundaries_decode = {0: 'X', 1: 'Y', 2: 'Z', 3: '-X', 4: '-Y', 5: '-Z'}
    with open('Sources.pkl', 'rb') as f:
        loaded_db = pickle.load(f)

    pkl_sources = get_all_sources(loaded_db)

    d = init_test_data()
    part_number = 1
    direction = 0

    deleted_source = f'Boundaries_{part_number}_{boundaries_decode[direction]}'

    d.PL_bound[part_number][direction] = 0

    ex = PreviousProjectLoader(os.path.dirname(__file__),
                               [d.PAR, d.LAY, d.PL_surf, d.PL_vol, d.PL_bound, d.layer_numbers])
    read_data_sources = get_all_sources(ex.global_tree_db)

    assert deleted_source not in read_data_sources
    assert deleted_source in pkl_sources


def test_delete_particle():
    with open('Sources.pkl', 'rb') as f:
        loaded_db = pickle.load(f)

    pkl_particles = get_all_particles(loaded_db)

    d = init_test_data()
    delete_key = list(d.PAR.keys())[-1]
    d.PAR.pop(delete_key)

    ex = PreviousProjectLoader(os.path.dirname(__file__),
                               [d.PAR, d.LAY, d.PL_surf, d.PL_vol, d.PL_bound, d.layer_numbers])
    read_data_particles = get_all_particles(ex.global_tree_db)

    assert pkl_particles != read_data_particles

