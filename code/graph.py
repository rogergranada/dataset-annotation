#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Create a graph for creating the PDDL file.

"""
import sys
sys.path.insert(0, '..')
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import os
import argparse
from os.path import join, isdir, splitext, basename, dirname

import progressbar as pbar

class Graph(object):
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, name):
        self.nodes[name] = ''

    def add_edge(self, from_node, to_node, name):
        if not from_node in self.nodes:
            logger.error('Graph do not contain node: {}'.format(from_node))
            logger.error('Cannot add edge: ({}, {})'.format(from_node, to_node))
            return
        if not from_node in self.nodes:
            logger.error('Graph do not contain node: {}'.format(from_node))
            logger.error('Cannot add edge: ({}, {})'.format(from_node, to_node))
            return
        if from_node in self.edges:
            if to_node in self.edges[from_node]:
                self.edges[from_node][to_node].append(name)
            else:
                self.edges[from_node][to_node] = [name]
        else:
            self.edges[from_node] = {to_node: [name]}

    def has_edge(from_node, to_node):
        if from_node in self.nodes and to_node in self.nodes:
            if from_node in self.edges and to_node in self.edges[from_node]:
                return True
        return False

    def __iter__(self):
        for from_node in self.edges:
            for to_node in self.edges[from_node]:
                for rel in self.edges[from_node][to_node]:
                    yield (from_node, to_node, rel)

    def adjacency(self, node):
        if node in self.nodes and node in self.edges:
            return self.edges[node]
        return None


    def __str__(self):
        content = ''
        for from_node in self.edges:
            for to_node in self.edges[from_node]:
                for rel in self.edges[from_node][to_node]:
                    content += from_node+' -> '+to_node+' ('+rel+')\n'
        return content
