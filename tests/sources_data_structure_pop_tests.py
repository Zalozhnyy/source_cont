import sys
sys.path.append('../')

import pytest

from dataclasses import dataclass
import os
import pickle
from typing import Dict

from source_Project_reader import DataParser
from source_utility import TreeDataStructure, PreviousProjectLoader


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
    ex.start_reading(tests=True)
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

