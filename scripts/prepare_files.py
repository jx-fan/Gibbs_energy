from pathlib import Path
import os
import shutil
import math
from pymatgen import Structure

default_equilibrium_calculation_incar = {
    "PREC": "Accurate",
    "IBRION": "2",
    "NSW": "99",
    "NELMIN": "5",
    "ISIF": "2",
    "EDIFF": "1e-08",
    "EDIFFG": "-1e-08",
    "ISMEAR": "0",
    "ALGO": "Normal",
    "LREAL": ".FALSE.",
    "ADDGRID": ".TRUE.",
    "LWAVE": ".FALSE.",
    "LCHARG": ".FALSE.",
    "NPAR": "4"
}
default_displacement_calculation_incar = {
    "PREC": "Accurate",
    "IBRION": "-1",
    "NELMIN": "5",
    "NELM": "100",
    "EDIFF": "1e-08",
    "ISMEAR": "0",
    "ALGO": "Normal",
    "LREAL": ".FALSE.",
    "ADDGRID": ".TRUE.",
    "LWAVE": ".FALSE.",
    "LCHARG": ".FALSE.",
    "NPAR": "4"
}


def write_incar(path, option, **kwargs):
    option.update(kwargs)
    incar = open(path, 'w')
    for k, v in option.items():
        incar.write("{:>10} = {:<15}\n".format(k, v))
    incar.close()


def generate_scaled_poscar(structure_path, scale_index=0.2, delta=5):
    structure = Structure.from_file(structure_path)
    volume = structure.volume
    print("Original POSCAR volume: {:0.3f} A^3".format(volume))
    structure_sequence = list(range(-delta, delta+1))  # -delta, -delta+1,..., -1, 1,..., delta-1, delta
    structure_sequence.remove(0)
    volume_list = [(1+i*scale_index/delta)*volume for i in structure_sequence]
    for i in range(len(volume_list)):
        structure.scale_lattice(volume_list[i])
        save_path = Path('./phonon-{}/equilibrium'.format(str(i).zfill(2)))
        structure.to(fmt='poscar', filename=save_path/"POSCAR")
        print("Generated POSCAR for: phonon-0{}. Volume: {:0.3f} A^3"
              .format(i, volume_list[i]))


def prepare_phonon(number):
    if not number:
        number = 10
    if not (number % 2) == 0:
        raise SystemExit('It has to be even number!')
    cwd = Path.cwd()
    os.chdir(cwd)
    equ_folder = Path("./equilibrium")
    if not equ_folder.exists():
        equ_folder.mkdir()
    files = [f for f in cwd.iterdir() if f.is_file()]
    for file_name in files:
        shutil.move(src=file_name.name, dst=equ_folder)
    # Copy KPOINTS, POTCAR, jobscript, write INCAR, generate POSCAR with different volumes
    for i in range(number):
        folder_name = "phonon-" + str(i).zfill(2)
        phonon_equ_path = Path(folder_name)/"equilibrium"
        if not phonon_equ_path.exists():
            phonon_equ_path.mkdir(parents=True)
            print("Created folder: phonon-{}".format(str(i).zfill(2)))
        else:
            print("phonon-{} already exists.".format(str(i).zfill(2)))
        for file in ["KPOINTS", "POTCAR", "jobscript"]:
            shutil.copy(src=equ_folder / file, dst=phonon_equ_path / file)
        write_incar(path=phonon_equ_path / "INCAR", option=default_equilibrium_calculation_incar)
    generate_scaled_poscar(equ_folder/"CONTCAR", delta=int(number/2))


def prepare_disp(supercell):
    if not supercell:
        supercell = 2
    cwd = Path.cwd()
    os.chdir(cwd)
    poscar_files = list(cwd.glob('POSCAR-*'))
    print("Number of displacements: {}".format(len(poscar_files)))
    counter = 0
    for i in range(1, len(poscar_files)+1):
        folder_name = "disp-" + str(i).zfill(3)
        if not Path(folder_name).exists():
            Path(folder_name).mkdir()
            counter += 1
        for file in ["KPOINTS", "POTCAR", "jobscript"]:
            shutil.copy(src=Path("./equilibrium") / file, dst=Path(folder_name) / file)
        with open(Path(folder_name)/"KPOINTS", 'r') as f:
            lines = f.readlines()
            mesh = lines[3].split()
            reduced_mesh = [math.ceil(int(x)/supercell) for x in mesh]
            lines[3] = ' '.join(map(str, reduced_mesh)) + "\n"
        with open(Path(folder_name)/"KPOINTS", 'w') as f:
            f.writelines(lines)
        write_incar(path=Path(folder_name) / "INCAR", option=default_displacement_calculation_incar)
        shutil.move(src="POSCAR-" + str(i).zfill(3), dst=Path(folder_name)/"POSCAR")
        print("Finished setup for {}".format(folder_name))
    print("Generated {} displacement folders.".format(counter))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='prepare files for phonon calculations.')
    parser.add_argument('step', choices=["phonon", "disp"], type=str,
                        help="set the calculation step.")
    parser.add_argument('--number', type=int, help="Generate a even number of folders.")
    parser.add_argument('--supercell', type=int, help="Enter the size of the supercell.")
    args = parser.parse_args()
    if args.step == "phonon":
        prepare_phonon(number=args.number)
    elif args.step == "disp":
        prepare_disp(supercell=args.supercell)
