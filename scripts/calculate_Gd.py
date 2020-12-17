from pathlib import Path
import os
from pymatgen import Structure

cwd = Path.cwd()
os.chdir(cwd)
structure = Structure.from_file(cwd/"equilibrium/POSCAR")
number_of_atoms = structure.num_sites
print("The total number of atoms in this structure: {}".format(number_of_atoms))
with open("gibbs-temperature.dat",'r') as f:
    file_lines=f.readlines()
    G_0 = file_lines[0].split()[1]
    new_file_lines = []
    for i in file_lines:
        G_T=i.split()[1]
        G_d=(float(G_T) - float(G_0))/number_of_atoms
        new_line = i.strip('\n')+"{:>20f}\n".format(G_d)
        new_file_lines.append(new_line)
with open("gibbs-temperature-new.dat", 'w') as f:
    f.writelines(new_file_lines)