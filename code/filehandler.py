#!/usr/bin/env python
# coding: utf-8
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import sys
import ast

from os.path import exists

class FileHandler(object):
    def __init__(self, inputfile):
        self.inputfile = inputfile

    def __enter__(self):
        self.exist_file()
        self.fin = open(self.inputfile)
        return self

    def __exit__(self, *args):
        self.fin.close()

    def exist_file(self):
        if not exists(self.inputfile):
            logger.error('{} is not a valid file'.format(self.inputfile))
            sys.error(0)
        return
# End of FileHandler class


class LisFile(FileHandler):
    def __init__(self, inputfile):
        super(LisFile, self).__init__(inputfile)
        self.path = ''
        self.idfr = -1
        self.obj = None
        self.x = -1
        self.y = -1
        self.w = -1
        self.h = -1
        self.idobj = -1
        self.fname = None

    def __iter__(self):
        """ Iterate on file yielding the array with all line content"""
        for line in self.fin:
            arr = line.strip().split('\t')
            if not line[0].isdigit():
                if arr[-1].startswith('data'):
                    self.path = arr[-1]
                continue
            self.idfr = int(arr[0])
            self.obj = arr[1]
            self.x, self.y, self.w, self.h = map(int, ast.literal_eval(arr[2]))
            self.bbox = arr[2]
            self.idobj = arr[3]
            self.fname = arr[4]
            yield arr

    def objects_in_frame(self):
        last_id = -1
        objs = []
        for _ in enumerate(self):
            if self.idfr != last_id and last_id != -1:
                last_id = self.idfr
                yield self.idfr-1, objs
                objs = [self.obj]
            else:
                last_id = self.idfr
                objs.append(self.obj)
        yield self.idfr, objs

    def id(self):
        id, _ = splitext(basename(self.fname))
        return int(id)

    def count_lines(self):
        """ Number of lines of the file - decreases the header and footer """
        with open(self.inputfile) as fin:
            for i, _ in enumerate(fin, start=1): pass
        return i-3
# End of LisFile class


class CompressedFile(FileHandler):
    """ Compressed file has the form:
        Initial_frame-Final_frame-Subject-Relation-Object
        E.g. 

            0-4-1-3-7
            1-2-1-4-7
            4-4-7-1-17

        where objects have the following ids: 
            1=person, 7=shell-egg, and 17=bowl
        and relations have the ids: 
            1=on, 3=holding, and 4=moving
    """
    def __init__(self, inputfile):
        super(CompressedFile, self).__init__(inputfile)
        self.cnames = False
        self.nb_lines = 0

    def __iter__(self):
        objs = []
        for self.nb_lines, line in enumerate(self.fin):
            if not line or not line[0].isdigit(): continue
            start, end, o1, r, o2 = self.check_line(self.nb_lines, line)
            yield start, end, o1, r, o2

    def check_line(self, i, line):
        arr = line.strip().split('-')
        if len(arr) != 5:
            logger.error('Malformed line in input file! [LINE: {}]'.format(i))
            sys.exit(0)
        start, end = int(arr[0]), int(arr[1])
        if start >= end:
            logger.error('START frame is greater than END frame: ({} - {}) [LINE: {}]'.format(start, end, i))
            sys.exit(0)
        if arr[2].isdigit():
            return start, end, int(arr[2]), int(arr[3]), int(arr[4])
        self.cnames = True
        return start, end, arr[2], arr[3], arr[4]
# End of CompressedFile class


class DecompressedFile(FileHandler):
    """ Decompressed file has the form:
        Frame \t Subject \t Relation \t Object
        E.g. 

            0\tperson\tholding\tshell-egg
            1\tperson\tholding\tshell-egg
            1\tperson\tmoving\tshell-egg
            2\tperson\tholding\tshell-egg
            2\tperson\tmoving\tshell-egg
            3\tperson\tholding\tshell-egg
            4\tperson\tholding\tshell-egg
            4\tshell-egg\ton\tbowl
    """
    def __init__(self, inputfile):
        super(DecompressedFile, self).__init__(inputfile)
        self.nb_lines = 0
        self.start_frames = []
        self.dic = {}

    def group_relations(self):
        self.__enter__()
        for self.nb_lines, line in enumerate(self.fin):
            if not line or not line[0].isdigit(): continue
            idf, sub, rel, obj = self.check_line(self.nb_lines, line)
            if self.dic.has_key((sub, rel, obj)):
                if idf == self.dic[(sub, rel, obj)]['last']+1:
                    self.dic[(sub, rel, obj)]['last'] += 1
                else:
                    first = self.dic[(sub, rel, obj)]['first']
                    last = self.dic[(sub, rel, obj)]['last']
                    self.dic[(sub, rel, obj)]['contiguous'].append((first, last))
                    self.dic[(sub, rel, obj)]['first'] = idf
                    self.dic[(sub, rel, obj)]['last'] = idf
                    self.start_frames.append((idf, (sub, rel, obj)))
            else:
                self.dic[(sub, rel, obj)] = {'first':idf, 'last':idf, 'contiguous':[]}
                self.start_frames.append((idf, (sub, rel, obj)))

        for rel in self.dic:
            first = self.dic[rel]['first']
            last = self.dic[rel]['last']
            self.dic[rel]['contiguous'].append((first, last))
        return self.dic

    def check_line(self, i, line):
        arr = line.strip().split('\t')
        if len(arr) != 4:
            logger.error('Malformed line in input file! [LINE: {}]'.format(i))
            sys.exit(0)
        frame = int(arr[0])
        return frame, arr[1], arr[2], arr[3]
# End of DecompressedFile class


class ConfigFile(FileHandler):
    """ Configuration file has the form:
        Id_Object Object
        E.g. 

            0 __background__
            1 person
            2 baked_egg
            3 boiled_egg

        where Objects can also be relations.
    """
    def __init__(self, inputfile):
        super(ConfigFile, self).__init__(inputfile)

    def load_classes(self, cnames=False, as_set=False):
        """ cnames : class names instead of ids """
        self.__enter__()
        self.dcls = {}
        for line in self.fin:
            arr = line.strip().split()
            if cnames:
                self.dcls[arr[1]] = int(arr[0])
            else:
                self.dcls[int(arr[0])] = arr[1]
        if as_set:
            return set(self.dcls.keys())
        return self.dcls
# End of ConfigFile class
