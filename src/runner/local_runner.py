#!/usr/bin/env python2

from __future__ import print_function

import re
import os
import sys
import pprint

import graph

def main():
    g, nodes = graph.build_graph(sys.stdin)
    execution_order = graph.topological_sort(g)

    for level in execution_order:
        for item in level:
            data = nodes[item]
            for command in data.commands_list:
                print("{}".format(command), file=sys.stderr)
                if os.system(command):
                    raise Exception("failed at: {}".format(item))

if __name__ == '__main__':
    main()
