#!/usr/bin/env python
# coding: utf-8
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import os
import sys
import ast
#import lxml.etree as ET

from os.path import exists, join, splitext, dirname, basename, realpath

def is_file(inputfile):
    """ Check whether the ``inputfile`` corresponds to a file """
    inputfile = realpath(inputfile)
    if not isfile(inputfile):
        logger.error('Input is not a file!')
        sys.exit(0)
    return inputfile


def is_folder(inputfolder):
    """ Check whether the ``inputfolder`` corresponds to a folder """
    inputfolder = realpath(inputfolder)
    if not isdir(inputfolder):
        logger.error('Argument %s is not a folder!' % inputfolder)
        sys.exit(0)
    return inputfolder


def filename(path, extension=True, string=False):
    fname, ext = splitext(basename(path))
    if string:
        return '%s%s' % (fname, ext)
    if extension:
        return fname, ext
    return fname

def mkdir_from_file(path):
    """ Create a folder with the same name of the file (without extension)"""
    path = realpath(path)
    dirfile = dirname(path)
    fname, ext = filename(path)
    dirout = join(dirfile, fname)
    if exists(dirout):
        logger.warning('Folder %s already exists!' % dirout)
    else:
        os.makedirs(dirout)
    return dirout


class FolderHandler(object):
    """ Class to deal with folders """
    def __init__(self, inputfolder, ext='txt', sort_id=False):
        self.inputfolder = inputfolder
        self.ext = ext
        self.sort_id = sort_id
        self.id = -1
        self.dfiles = {}
        self.files = []
        self.exist_folder()
        self._load_paths()

    def __iter__(self):
        if self.sort_id:
            for id in sorted(self.dfiles):
                self.id = id
                yield self.dfiles[id]
        else:
            for path in sorted(self.files):
                yield path

    def _load_paths(self):
        for root, dirs, files in os.walk(self.inputfolder, topdown=False):
            for name in files:
                fname, ext = splitext(name)
                if ext[1:] == self.ext:
                    path = join(root, name)
                    if self.sort_id:
                        self.dfiles[int(fname)] = path
                    else:
                        self.files.append(path)
        return self

    def exist_folder(self):
        if not exists(self.inputfolder):
            logger.error('{} is not a valid folder'.format(self.inputfile))
            sys.error()
        return

    def nb_files(self):
        if self.sort_id:
            return len(self.dfiles)
        return len(self.files)
# End of FileHandler class


class FileHandler(object):
    """ Super class with shared functions """
    def __init__(self, inputfile):
        self.inputfile = inputfile
        self.path = ''
        self.fname = ''

    def __enter__(self):
        self.exist_file()
        self.fin = open(self.inputfile)
        return self

    def __exit__(self, *args):
        self.fin.close()

    @property
    def filename(self):
        return basename(self.inputfile)

    def exist_file(self):
        if not exists(self.inputfile):
            logger.error('{} is not a valid file'.format(self.inputfile))
            sys.exit()
        return

    def nb_lines(self):
        with open(self.inputfile) as fin:
            for i, _ in enumerate(fin, start=1): pass
        return i

    def imgpath(self):
        return join(self.path, self.fname)

    def nb_frames(self):
        last_idf = -1
        counter = 0
        with open(self.inputfile) as fin:
            for line in fin:
                if not line[0].isdigit(): continue
                idf = int(line.split('\t')[0])
                if idf != last_idf:
                    last_idf = idf
                    counter += 1
        return counter
# End of FileHandler class


class LisFile(FileHandler):
    """ LIS file has the form:
        Frame:\tLabel:\tPoints:\tBounding Box ID:\tFrame path
        E.g.:

        0\tbowl\t(53,118,46,46)\t17\t0.jpg
        0\tfrying_pan\t(100,88,86,105)\t14\t0.jpg
        0\tham\t(62,179,36,33)\t12\t0.jpg
        0\tknife\t(32,104,24,65)\t22\t0.jpg
    """

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
        for self.nb_line, line in enumerate(self.fin, start=1):
            arr = line.strip().split('\t')
            if not line[0].isdigit():
                if 'data' in line:
                    self.path = 'data' + arr[-1].split('data')[1]
                continue
            self.idfr = int(arr[0])
            self.obj = arr[1]
            self.x, self.y, self.w, self.h = map(int, ast.literal_eval(arr[2]))
            self.bbox = arr[2]
            self.idobj = int(arr[3])
            self.fname = arr[4]
            yield arr

    def _add_element(self, ids, pos):
        if ids:
            if pos:
                objs = (self.idobj, self.x, self.y, self.w, self.h)
            else:
                objs = self.idobj
        else:
            if pos:
                objs = (self.dobj, self.x, self.y. self.w, self.h)
            else:
                objs = self.dobj
        return objs

    def objects_in_frame(self, ids=False, pos=False):
        last_id = -1
        objs = []
        for _ in enumerate(self):
            if self.idfr != last_id and last_id != -1:
                last_id = self.idfr
                yield self.idfr-1, objs
                objs = [self._add_element(ids, pos)]
            else:
                last_id = self.idfr
                objs.append(self._add_element(ids, pos))
        yield self.idfr, objs

    def iterate_frames(self):
        last_id = -1
        objs = []
        fname = ''
        for _ in enumerate(self):
            if self.idfr != last_id and last_id != -1:
                last_id = self.idfr
                yield fname, objs
                objs = [(self.obj, self.x, self.y, self.w, self.h)]
            else:
                fname = self.fname
                last_id = self.idfr
                objs.append((self.obj, self.x, self.y, self.w, self.h))
        yield fname, objs

    def id(self):
        id, _ = splitext(basename(self.fname))
        return int(id)

    def count_lines(self):
        """ Number of lines of the file - decreases the header and footer """
        with open(self.inputfile) as fin:
            for i, _ in enumerate(fin, start=1): pass
        return i-3
# End of LisFile class


def error_line(i, line):
    logger.error('Malformed line in input file! [LINE: {}]'.format(i))
    logger.error('{}'.format(line))
    sys.exit()


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
        line = line.strip()
        arr = line.split()
        if len(arr) == 1:
            arr = line.split('-')
            if len(arr) != 5: error_line(i, line)
            start, end = int(arr[0]), int(arr[1])
        else:
            frames = arr[0].split('-')
            if len(frames) != 2: error_line(i, line)
            start, end = map(int, frames)
        if start >= end:
            logger.error('START frame is greater than END frame: ({} - {}) [LINE: {}]'.format(start, end, i))
            sys.exit()
        if arr[2].isdigit():
            return start, end, int(arr[2]), int(arr[3]), int(arr[4])
        self.cnames = True
        return start, end, arr[1], arr[2], arr[3]

    def list_relations(self, as_set=True):
        rels = []
        self.__enter__()
        for _, _, o1, r, o2 in self:
            rels.append((o1, r, o2))
        if as_set:
            return set(rels)
        return rels
# End of CompressedFile class


class DecompressedFile(FileHandler):
    """ Decompressed file has the form:
        Frame \t Subject \t Relation \t Object
        E.g.: 

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
        self.nb_line = 0
        self.start_frames = []
        self.dic = {}

    def __iter__(self):
        objs = []
        for self.nb_line, line in enumerate(self.fin):
            if not line or not line[0].isdigit():
                if 'Path:' in line:
                    self.path = line.strip().split('Path: ')[-1]
                continue
            arr = self.check_line(self.nb_lines, line)
            yield arr

    def group_relations(self):
        self.__enter__()
        for self.nb_line, line in enumerate(self.fin):
            if not line or not line[0].isdigit(): continue
            arr = self.check_line(self.nb_lines, line)
            idf, sub, rel, obj = arr[0], arr[1], arr[2], arr[3]
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
        if len(arr) < 4 or len(arr) > 5:
            logger.error('Malformed line in input file! [LINE: {}]'.format(i))
            sys.exit()
        frame = int(arr[0])
        if len(arr) == 4:
            return frame, arr[1], arr[2], arr[3]
        return frame, arr[1], arr[2], arr[3], arr[4]


    def iterate_frames(self):
        triplets = []
        self.__enter__()
        last_id =0
        for self.nb_line, line in enumerate(self.fin):
            if not line or not line[0].isdigit(): continue
            arr = self.check_line(self.nb_lines, line)
            idf, sub, rel, obj = arr[0], arr[1], arr[2], arr[3]
            if idf != last_id:
                yield idf-1, triplets
                triplets = []
                triplets.append((sub, rel, obj))
            else:
                triplets.append((sub, rel, obj))
            last_id = idf
        yield idf, triplets

    def list_relations(self, as_set=True):
        rels = []
        self.__enter__()
        for arr in self:
            rels.append((arr[1], arr[2], arr[3]))
        if as_set:
            return set(rels)
        return rels
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

        The option `background=True` considers the background as id=0
        Otherwise, the id of person starts at zero id=0.
    """
    def __init__(self, inputfile, background=True):
        super(ConfigFile, self).__init__(inputfile)
        self.background = background

    def load_classes(self, cnames=False, as_set=False):
        """ cnames : class names instead of ids """
        self.__enter__()
        self.dcls = {}
        for line in self.fin:
            arr = line.strip().split()
            if cnames:
                if self.background:
                    self.dcls[arr[1]] = int(arr[0])
                elif arr[1] == '__background__': 
                    continue
                else:
                    self.dcls[arr[1]] = int(arr[0])-1
            else:
                if self.background:
                    self.dcls[int(arr[0])] = arr[1]
                elif arr[1] == '__background__': 
                    continue
                else:
                    self.dcls[int(arr[0])-1] = arr[1]
        if as_set:
            return set(self.dcls.keys())
        return self.dcls
# End of ConfigFile class


class PredictionFile(FileHandler):
    """ Prediction file has the form:

        Frame;xmin;ymin;xmax;ymax;id_class;score

        where `score' is a value between 0 and 1.
    """
    def __init__(self, inputfile):
        super(PredictionFile, self).__init__(inputfile)

    def __iter__(self):
        for self.nb_lines, line in enumerate(self.fin):
            if not line or not line[0].isdigit(): continue
            yield self.check_line(self.nb_lines, line)

    def check_line(self, i, line):
        arr = line.strip().split(';')
        if len(arr) != 7:
            logger.error('Malformed line in input file! [LINE: {}]'.format(i))
            sys.exit()
        arr[:-1] = map(int, arr[:-1])
        return arr
# End of PredictionFile class


class MapFile(FileHandler):
    """ Map_paths file has the form:

        path_KSCGR : path_VOC

    """
    def __init__(self, inputfile):
        super(MapFile, self).__init__(inputfile)

    def __iter__(self):
        for self.nb_lines, line in enumerate(self.fin):
            yield self.check_line(self.nb_lines, line)

    def check_line(self, i, line):
        arr = line.strip().split(' : ')
        if len(arr) != 2:
            logger.error('Malformed line in input file! [LINE: {}]'.format(i))
            sys.exit()
        return arr

    def load_dictionary(self, key='kscgr'):
        self.map = {}
        self.__enter__()
        for kscgr, voc in self:
            if key == 'kscgr':
                self.map[kscgr] = voc
                if not self.path:
                    self.path = 'data'.join(kscgr.split('data')[:-1])
            else:
                self.map[voc] = kscgr
                if not self.path:
                    self.path = voc.split('JPEGImages')[0]
        return self.map
# End of MapFile class


class VOCXML(object):
    def __init__(self, xml_file):
        tree = ET.parse(xml_file)
        self.root = tree.getroot()

    def image_path(self):
        for child in self.root:
            if child.tag == 'path':
                path = child.text
        return path

    def extract_objects(self):
        objs = []
        for child in self.root:
            if child.tag == 'object':
                for obj in child:
                    if obj.tag == 'name':
                        name = obj.text
                    elif obj.tag == 'bndbox':
                        dpos = {}
                        for pos in obj:
                            dpos[pos.tag] = int(pos.text)
                        objs.append((name, dpos))
        return objs
                            


class VOCFile(object):
    def __init__(self, image_file, width=None, height=None):
        self.filename = basename(image_file)
        self.width = width
        self.height = height
        if not width or not height:
            im = Image.open(image_file)
            self.width, self.height = im.size
        self._create_header()

    def _create_header(self):
        """ Create XML with information of the image """
        self.xml = ET.Element('annotations')
        ET.SubElement(self.xml, 'folder').text = 'JPEGImages'
        ET.SubElement(self.xml, 'filename').text = self.filename    
        imsize = ET.SubElement(self.xml, 'size')
        ET.SubElement(imsize, 'width').text = str(self.width)
        ET.SubElement(imsize, 'height').text = str(self.height)
        ET.SubElement(imsize, 'depth').text = '3'
        ET.SubElement(self.xml, 'segmented').text = '0' 

    def add_object(self, name, x, y, w, h):
        """ Add the annotation for an object """
        # VOC cannot have xmin or ymin equals zero
        if x <= 0: 
            w -= x-1
            x = 1
        if y <= 0: 
            h -= y-1
            y = 1
        xmin = x
        ymin = y
        xmax = x + w
        ymax = y + h 
        if xmax > 256:
            xmax = 256
        if ymax > 256:
            ymax = 256

        obj = ET.SubElement(self.xml, "object")
        ET.SubElement(obj, "name").text = name
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = '0'
        ET.SubElement(obj, "difficult").text = '0'
        bbox = ET.SubElement(obj, "bndbox")
        ET.SubElement(bbox, "xmin").text = str(xmin)
        ET.SubElement(bbox, "ymin").text = str(ymin)
        ET.SubElement(bbox, "xmax").text = str(xmax)
        ET.SubElement(bbox, "ymax").text = str(ymax)
    
    def save_xml(self, folderout):
        """ Save the XML corresponding to an image in folderout """
        fname, _ = splitext(self.filename)
        fileout = join(folderout, fname+'.xml')
        tree = ET.ElementTree(self.xml)
        tree.write(fileout, pretty_print=True)
# End of VOCFile class

class PathFile(FileHandler):
    """ Path file has the form:
        Frame path <SPACE> [Class]
        E.g.:

        /home/user/0.jpg 0
        /home/user/1.jpg 0
        /home/user/2.jpg 1
        /home/user/3.jpg 1
    """

    def __init__(self, inputfile):
        super(PathFile, self).__init__(inputfile)
        self.path = ''
        self.idfr = -1
        self.x = -1
        self.fname = None

    def __iter__(self):
        """ Iterate on file yielding the array with all line content"""
        for self.nb_line, line in enumerate(self.fin, start=1):
            arr = line.strip().split()
            self.path = arr[0]
            self.fname = basename(arr[0])
            bname, _ = splitext(self.fname)
            self.idfr = int(bname)
            yield arr
# End of PathFile class

class PddlTypes(object):
    def __init__(self, inputfile):
        self.dic = {}
        with open(inputfile) as fin:
            for line in fin:
                line = line.strip()
                if not (line.startswith('(') or line.startswith(')')):
                    arr = line.split(' - ')
                    objs, label, var = arr
                    label = label.replace('_', '-')
                    for obj in objs.split():
                        obj = obj.replace('_', '-')
                        self.dic[obj] = (label, var)

    def __getitem__(self, obj):
        return self.dic[obj]
# End of PddlTypes class








