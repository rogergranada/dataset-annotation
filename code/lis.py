#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Class to deal with LIS annotation. LIS annotation has
the following format after the heading (spaces are added for
a better reading):

frame_id \t object \t (x, y, width, height) \t object_id \t path_to_img
"""
import sys
sys.path.insert(0, '..')
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import ast
from os.path import splitext, basename

class LIS(object):
    def __init__(self, inputfile):
        self.inputfile = inputfile
        self.idfr = -1
        self.obj = None
        self.x = -1
        self.y = -1
        self.w = -1
        self.h = -1
        self.idobj = -1
        self.fname = None


    def __enter__(self):
        self.fin = open(self.inputfile)
        line = self.fin.next()
        self.header = line.split('Frame path:')[0]+'Frame path:'
        self.path = line.split('Frame path:')[1].strip()
        return self


    def __iter__(self):
        """ Iterate on file yielding the array with all line content"""
        for line in self.fin:
            if line.startswith('Frame') or \
               line.startswith('---') or \
               line.startswith('Modified'):
                continue
            arr = line.strip().split('\t')
            self.idfr = int(arr[0])
            self.obj = arr[1]
            self.x, self.y, self.w, self.h = map(int, ast.literal_eval(arr[2]))
            self.bbox = arr[2]
            self.idobj = arr[3]
            self.fname = arr[4]
            yield arr


    def id(self):
        id, _ = splitext(basename(self.fname))
        return int(id)


    def count_lines(self):
        """ Number of lines of the file - decreases the header and footer """
        with open(self.inputfile) as fin:
            for i, _ in enumerate(fin, start=1): pass
        return i-3


    def __exit__(self, *args):
        self.fin.close()
# End of LIS class

