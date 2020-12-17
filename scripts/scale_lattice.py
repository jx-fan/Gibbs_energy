from pymatgen import Structure


def generate_poscar(structure_path, scale_index=0.2, delta=5):
    structure = Structure.from_file(structure_path)
    volume = structure.volume
    print("The original volume: {} A^3".format(volume))
    structure_sequence = list(range(-delta, delta+1)) # -delta, -delta+1,..., -1, 1,..., delta-1, delta
    structure_sequence.remove(0)
    volume_list = [(1+i*scale_index/delta)*volume for i in structure_sequence]
    print("Scaled volume: {}".format(volume_list))
    for i in range(len(volume_list)):
        structure.scale_lattice(volume_list[i])
        save_path = './phonon-0' + str(i) + '/equilibrium'
        structure.to(fmt='poscar', filename=save_path+'/POSCAR')
        print("Generated POSCAR for phonon-0{}".format(i))


generate_poscar(structure_path="equilibrium/CONTCAR")