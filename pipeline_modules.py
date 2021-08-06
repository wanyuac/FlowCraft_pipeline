#! /usr/bin/env python
"""
Shared functions for scripts in this repository. These functions were initially developed for
spades_runner.py.

Copyright (C) 2021 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
First version: 6 Aug 2021; the latest update: 6 Aug 2021
"""

def import_readsets(r):
    Readset = namedtuple("Readset", ["r1", "r2"])  # One genome per object
    readsets = dict()
    if not os.path.exists(r):
        print("Error: Input file " + r + " is not accessible.", file = sys.stderr)
        sys.exit(1)
    with open(r, "r") as f:
        lines = f.read().splitlines()
        for line in lines:
            try:
                i, r_1, r_2 = line.split("\t")
            except ValueError:
                print("Error: line '%s' in the readset specification file cannot be correctly parsed." % line, file = sys.stderr)
                sys.exit(1)
            readsets[i] = Readset(r1 = r_1, r2 = r_2)
    return readsets


def write_job_script(script, k, i, out, scheduler):
    """ Returns the path of the output script """
    filename_ext = ".sge" if scheduler == "SGE" else ".pbs"
    f_name = os.path.join(out, "job_list_" + str(i) + filename_ext)  # In the future, the filename extension will be determined by the job scheduler.
    print("Write %i tasks into script %s" % (k, f_name))
    with open(f_name, "w") as f:
        f.write(script)
    return f_name


def check_dir(d):
    if not os.path.exists(d):
        os.mkdir(d)
    return
