#!/usr/bin/env python2

from __future__ import print_function

import re
import os
import sys
import pprint
import argparse
import multiprocessing as mp
import subprocess as sub

def run_command(command_list):
    for command in command_list:
        print(command, file=sys.stderr)
        if sub.call(command, shell=True):
            raise Exception("command failed: {}".format(command))

import graph

def run(processes=1):
    g, nodes = graph.build_graph(sys.stdin)
    execution_order = graph.topological_sort(g)

    pool = mp.Pool(processes=processes)

    for level in execution_order:
        pool.map(run_command, [nodes[n].commands_list for n in level])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--jobs', '-j', metavar='jobs', dest='jobs', type=int,
                        default=1,
                        help='Number of jobs that must be run simultaneously.')

    args = parser.parse_args()
    run(processes=args.jobs)
