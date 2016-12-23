#!/usr/bin/env python2

from __future__ import print_function

import re
import os
import sys
import pprint

from makefile import Makefile

class Node:
    def __init__(self, target_name):
        self.target_name = target_name
        self.commands_list = []

    def __repr__(self):
        return "{}".format("\n".join(self.commands_list)) or "<none>"

def build_graph(data):
    started = False
    read_commands = (False, None) # (command reading mode, target name)
    graph = {}
    nodes = {}

    lqueue = []

    for line in data:
        line = line.rstrip()

        if read_commands[0]:
            _, line_type = Makefile.identify(line)

            if line_type == Makefile.Lines.RemakeDone:
                read_commands = (False, None)
            elif line_type:
                raise Exception("unexpected line type")
            else:
                nodes[read_commands[1]].commands_list += [line]

            continue

        if not started:
            target_name, _ = Makefile.identify(line)
            if target_name and target_name != "Makefile":
                started = True
                lqueue = [target_name]
                graph[target_name] = ['(root)'] # create the root
                nodes[target_name] = Node(target_name)

            continue

        target_name, line_type = Makefile.identify(line)

        if not target_name: continue

        if line_type == Makefile.Lines.TargetStart:
            if target_name not in graph:
                graph[target_name] = []
                nodes[target_name] = Node(target_name)

            graph[target_name] += [lqueue[-1]]
            lqueue.append(target_name)
        elif line_type == Makefile.Lines.TargetEnd:
            lqueue.pop()
        elif line_type == Makefile.Lines.PruningFile:
            graph[target_name] += [lqueue[-1]]
        elif line_type == Makefile.Lines.MustRemake:
            read_commands = (True, target_name)

    return (graph, nodes)

def main():
    graph, nodes = build_graph(sys.stdin)
    pprint.pprint(graph)
    pprint.pprint(nodes)

if __name__ == '__main__':
    main()
