#!/usr/bin/env python2

from __future__ import print_function

import re
import os
import sys

from makefile import Makefile

class Node:
    def __init__(self):
        pass

def build_graph(data):
    started = False
    graph = {}
    nodes = {}

    lqueue = []

    for line in data:
        line = line.rstrip()

        if not started:
            target_name = Makefile.Strings.target(line)
            if target_name and target_name != "Makefile":
                started = True
                lqueue = [target_name]
                graph[target_name] = [] # create the root!
                nodes[target_name] = Node()

            continue

        

    return (graph, nodes)

def main():
    graph, nodes = build_graph(sys.stdin)
    print(graph)
    print(nodes)

if __name__ == '__main__':
    main()
