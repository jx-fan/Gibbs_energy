# Purpose
python scripts for conducting Quasi harmonic approximation phonon calculations using phonopy: https://phonopy.github.io/phonopy/qha.html

# File system
The arrangement of the file system is consistent with the calculations under phonondb: http://phonondb.mtl.kyoto-u.ac.jp/ph20151124/index.html

|-- equilibrium
|-- phonon-00
|   |-- FORCE_SETS
|   |-- POSCAR
|   |-- SPOSCAR
|   |-- mesh.yaml
|   |-- phonopy.yaml
|   |-- phonopy_disp.yaml
|   |-- disp-001
|   |   |-- CHG
|   |   |-- CHGCAR
|   |   |-- CONTCAR
|   |   |-- DOSCAR
|   |   |-- EIGENVAL
|   |   |-- IBZKPT
|   |   |-- INCAR
|   |   |-- KPOINTS
|   |   |-- OSZICAR
|   |   |-- OUTCAR
|   |   |-- PCDAT
|   |   |-- POSCAR
|   |   |-- POTCAR
|   |   |-- REPORT
|   |   |-- WAVECAR
|   |   |-- XDATCAR
|   |   |-- jobscript
|   |   |-- vasp.log
|   |   `-- vasprun.xml
|   |-- disp-002
|   |   ...
|   ...
|   `-- thermal_properties.yaml
|-- phonon-01
...
...


# workflow
1. Submit phonon equilibrium calculations
2. Check force convergence by running: python3 scripts/check_force.py
3. (optional) Copy CONTCAR to POSCAR and resubmit jobs if unconverged
4. Prepare file system for different crystal volumes by running: python3 scripts/prepare_files.py phonon --number NUMBER_OF_VOLUMES
5. Generate POSCAR files for each phonon-** folder
6. Create POSCAR with different volume: python3 scripts/scale_lattice.py PATH_TO_CONTCAR
7. Generate supercell with displacements phonopy -d --dim="a b c" (<a b c> is the size of the supercell)
8. Set up disp-*** folders: python3 scripts/prepare_files.py disp and submit jobs
9. Generate FORCE_STES: phonopy -f disp-*/vasprun.xml 1> /dev/null; echo "Finish generating FORCE_SETS for ${i}."
10. Generate thermal_properties.yaml: phonopy -t ../mesh.conf 1> /dev/null; echo "Finish generating thermal_properties.yaml for ${i}."
11. Prepare e-v.dat file. python3 scripts/energy_volume.py --number NUM_OF_VOLUME
12. Calculate Gibbs energy up to 2000 K: phonopy-qha --tmax 2000 e-v.dat phonon-0*/thermal_properties.yaml
13. Calculate Gibbs energy difference: python3 scripts/calculate_Gd.py
