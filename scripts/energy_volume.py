import os
from pathlib import Path
from pymatgen import Structure
"""
Please run this script under the folder: /mp-***
"""


def generate_file(number_of_volume):
    if not number_of_volume:
        number_of_volume = 10
    cwd = Path.cwd()
    os.chdir(cwd)
    with open("e-v.dat", 'w') as f:
        f.write("# {:<20}{:<40}\n".format("cell volume", "energy of cell other than phonon"))
        for i in range(number_of_volume):
            phonon_folder = "phonon-" + str(i).zfill(2)
            contcar_path = cwd / phonon_folder / "equilibrium/CONTCAR"
            oszicar_path = cwd / phonon_folder / "equilibrium/OSZICAR"
            structure = Structure.from_file(contcar_path)
            volume = structure.volume
            #print(contcar_path)
            #print(oszicar_path)
            with open(oszicar_path, 'r') as oszicar:
                lines = oszicar.read().splitlines()
                last_line = lines[-1]
                energy = last_line.split()[2]
            f.write("  {:<20f}{:<40f}\n".format(float(volume), float(energy)))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='generate e-v.dat')
    parser.add_argument('--number', action='store', type=int, help='the total number of phonon calculations.')
    args = parser.parse_args()
    generate_file(number_of_volume=args.number)
