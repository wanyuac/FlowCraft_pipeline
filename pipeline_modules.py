#!/usr/bin/env python
"""
Shared functions for scripts in this repository. These functions were initially developed for
run_spades.py.

Copyright (C) 2021 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
First version: 6 Aug 2021; the latest update: 19 Oct 2021
"""
import os
import sys
from collections import namedtuple


def check_files(i, files):
    """ Check existance of all files in the input list 'files' """
    success = True
    for f in files:
        if not os.path.exists(f):
            print(f"Error: file {f} of sample {i} does not exist.", file = sys.stderr)
            success = False
    return success


def import_readsets(r):
    Readset = namedtuple('Readset', ['r1', 'r2'])  # One genome per object
    readsets = dict()
    if not os.path.exists(r):
        print("Error: Input file " + r + " is not accessible.", file = sys.stderr)
        sys.exit(1)
    with open(r, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if line != '':
                try:
                    i, r_1, r_2 = line.split('\t')
                except ValueError:
                    print("Error: line '%s' in the readset specification file cannot be correctly parsed." % line, file = sys.stderr)
                    sys.exit(1)
                if check_files(i, [r_1, r_2]):
                    readsets[i] = Readset(r1 = r_1, r2 = r_2)
                else:
                    print(f"Error: sample {i} is ignored due to missing read file(s).", file = sys.stderr)
    n = len(readsets)
    if n > 0:
        print(f"{n} read set(s) have/has been imported.")    
    else:
        print("Error: no read set was imported. Exit.", file = sys.stderr)
        sys.exit(1)
    return readsets


def import_assemblies(a):
    assemblies = dict()
    if not os.path.exists(a):
        print(f"Error: Input file {a} is not accessible.", file = sys.stderr)
    with open(a, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if line != '':
                try:
                    i, p = line.split('\t')
                except ValueError:
                    print(f"Error: line {line} in the assembly specification file cannot be correctly parsed.", file = sys.stderr)
                if check_files(i, [p]):
                    assemblies[i] = p  # Add the file path for isolate i to the dictionary
                else:
                    print(f"Error: sample {i} is ignored due to its missing assembly file.", file = sys.stderr)
    n = len(assemblies)
    if n > 0:
        print(f"{n} assemblies have been imported.")
    else:
        print("Error: no assembly was imported. Exit.", file = sys.stderr)
        sys.exit(1)
    return assemblies


def write_job_script(script, k, i, out, scheduler):
    """
    Returns the path of the output script
    k: number of tasks in the current script; i: the index of the current script.
    """
    if scheduler == 'SGE':
        filename_ext = '.sge'
    elif scheduler == 'PBS':
        filename_ext = '.pbs'
    else:
        filename_ext = '.sh'
    f_name = os.path.join(out, 'job_list_' + str(i) + filename_ext)  # In the future, the filename extension will be determined by the job scheduler.
    print("Write %i tasks into script %s" % (k, f_name))
    with open(f_name, 'w') as f:
        f.write(script)
    return f_name


def check_dir(d):
    if not os.path.exists(d):
        os.mkdir(d)
    return
