#!/usr/bin/env python2

from __future__ import print_function

import re
import os
import sys
import pprint

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
            target_name, _ = Makefile.Strings.target(line)
            if target_name and target_name != "Makefile":
                started = True
                lqueue = [target_name]
                graph[target_name] = [] # create the root!
                nodes[target_name] = Node()

            continue

        target_name, line_type = Makefile.Strings.target(line)

        if not target_name: continue

        if line_type == Makefile.LineTypes.TargetStart:
            if target_name not in graph:
                graph[target_name] = []
                nodes[target_name] = Node()

            graph[target_name] += [lqueue[-1]]
            lqueue.append(target_name)
        elif line_type == Makefile.LineTypes.TargetEnd:
            lqueue.pop()
        elif line_type == Makefile.LineTypes.PruningFile:
            graph[target_name] += [lqueue[-1]]

    return (graph, nodes)

def main():
    graph, nodes = build_graph(sys.stdin)
    pprint.pprint(graph)
    pprint.pprint(nodes)

if __name__ == '__main__':
    main()
