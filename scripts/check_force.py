from pathlib import Path
import os
import numpy as np
import argparse
import matplotlib.pyplot as plt


def check_force_converge(force=None, plot=False):
    if not force:
        force = 1e-5
    cwd = Path.cwd()
    os.chdir(cwd)
    natoms = None
    maxforces_list = []
    avgforces_list = []

    try:
        outcar = open("OUTCAR", 'r')
    except:
        raise SystemExit("{}\nCan't find OUTCAR!\n".format(cwd))
    lines = outcar.readlines()

    for line in lines:
        if "NIONS" in line:
            natoms = int(line.split()[-1])
    if not natoms:
        raise SystemExit("{}\nCan't find NIONS tag in OUTCAR!\n".format(cwd))

    for index, line in enumerate(lines):
        if "TOTAL-FORCE" in line:
            atom_force = [list(map(float, lines[index+i].split()[-3:])) for i in range(2, 2+natoms)]
            maxforce = np.amax(np.abs(atom_force))
            maxforces_list.append(maxforce)
            norm = np.linalg.norm(atom_force, axis=1)
            avgforce = sum(norm)/natoms
            avgforces_list.append(avgforce)

    if not maxforces_list:
        print("{}\nFailed to start the job!\n".format(cwd))
    elif maxforces_list[-1] < force:
        print("{}\nForce converged. Start force: max = {:0.6f}, avg = {:0.6f} | "
              "Final force: max = {:0.6f}, avg = {:0.6f}\n"
              .format(cwd, maxforces_list[0], avgforces_list[0],
                      maxforces_list[-1], avgforces_list[-1]))
    else:
        print("{}\nForce unconverged. Start force: max = {:0.6f}, avg = {:0.6f} | "
              "Final force: max = {:0.6f}, avg = {:0.6f}\n"
              .format(cwd, maxforces_list[0], avgforces_list[0],
                      maxforces_list[-1], avgforces_list[-1]))

    if plot:
        iteration = len(maxforces_list)
        x = range(iteration)
        y = [np.nan if i == 0 else i for i in maxforces_list]
        plt.scatter(x, np.log10(y))
        plt.plot(x, np.log10(y))
        plt.xlabel("Ionic Step")
        plt.ylabel(r"$log(|F_{max}|)$")
        plt.savefig("force.png")


parser = argparse.ArgumentParser(description='check if force converged.')
parser.add_argument('--force', type=float)
parser.add_argument('--plot', action='store_true')
args = parser.parse_args()
check_force_converge(force=args.force, plot=args.plot)
