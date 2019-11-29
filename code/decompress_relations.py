#!/usr/bin/env python
# coding: utf-8
"""
This script reads a file containing relations as:

Initial_frame - Final_frame - Id_subject - Id_relation - Id_object

and creates a file containing a decompressed annotation with the sequence 
of frames for each relation as:

Frame \t Subject \t Relation \t Object

Thus, an example file containing:

0-4-1-3-7
1-2-1-4-7
4-4-7-1-17

generates the following lines:

0\tperson\tholding\tshell-egg
1\tperson\tholding\tshell-egg
1\tperson\tmoving\tshell-egg
2\tperson\tholding\tshell-egg
2\tperson\tmoving\tshell-egg
3\tperson\tholding\tshell-egg
4\tperson\tholding\tshell-egg
4\tshell-egg\ton\tbowl

where objects have the following ids: 1=person, 7=shell-egg, and 17=bowl
and relations have the ids: 1=on, 3=holding, and 4=moving

"""
import sys
import os
import argparse
from os.path import join, dirname, splitext, basename
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from collections import defaultdict

import filehandler as fh

def check_error(do, dr, o1, r, o2):
    if not do.has_key(o1):
        logger.error('Missing object in dictionary: %s' % o1)
        sys.exit(0)
    elif not dr.has_key(r):
        logger.error('Missing relation in dictionary: %s' % r)
        sys.exit(0)
    elif not do.has_key(o2):
        logger.error('Missing object in dictionary: %s' % o2)
        sys.exit(0)
    return


def save_aligned_with_objects(drels, object_file, do, dr, output, cnames=False, screen=True):
    """ Save only relations that contain the object in the frame """
    flis = fh.LisFile(object_file)
    with open(output, 'w') as fout, flis as fobjs:
        fout.write('Frame\tSubject\tRelation\tObject\n')
        for idfr, vobjs in fobjs.objects_in_frame():
            # vobjs = ['pan', 'bowl', 'shell_egg']
            if drels.has_key(idfr):
                arr = drels[idfr]
                for o1, r, o2 in arr:
                    check_error(do, dr, o1, r, o2)
                    if not cnames:
                        o1, r, o2 = do[o1], dr[r], do[o2]
                        if o1 not in vobjs or o2 not in vobjs:
                            if screen:
                                print 'Frame {} does not contain some of the elements {}: {}'.format(idfr, (do[o1], do[o2]), vobjs)
                            else:
                                logger.warning('Frame {} does not contain some of the elements {}: {}'.format(idfr, (do[o1], do[o2]), vobjs))
                            continue
                    fout.write('%d\t%s\t%s\t%s\n' % (idfr, o1, r, o2))
            else:
                fout.write('%d\tNone\tNone\tNone\n' % idfr)
    return


def save_aligned_no_objects(drels, do, dr, output, cnames=False, screen=True):
    """ Save all relations from `drels` in a file """
    with open(output, 'w') as fout:
        fout.write('Frame\tSubject\tRelation\tObject\n')
        last = max(drels.keys())
        for idfr in range(last+1):
            if drels.has_key(idfr):
                for o1, r, o2 in drels[idfr]:
                    check_error(do, dr, o1, r, o2)
                    if not cnames:
                        o1, r, o2 = do[o1], dr[r], do[o2]
                    fout.write('%d\t%s\t%s\t%s\n' % (idfr, o1, r, o2))
            else:
                fout.write('%d\tNone\tNone\tNone\n' % idfr)
    return


def decompress_relations(file_input, output=None, class_file='classes.cfg', rels_file='relations.cfg', object_file=None):
    if not output:
        fname, _ = splitext(basename(file_input))
        output = join(dirname(file_input), fname+'_decompressed.txt')

    # Load relations as {idf1: [(s,r,o),(s,r,o)...], idf2: [(s,r,o)]...}
    drels = defaultdict(list)
    fc = fh.CompressedFile(file_input)
    with fc as fin:
        for start, end, o1, r, o2 in fin:
            for j in range(start, end+1):
                drels[j].append((o1, r, o2))
        class_names = fc.cnames
    logger.info('Found {} lines in compressed input file.'.format(fc.nb_lines))

    # Load classes for objects from dict {0: 'rel0', 1: 'rel1'}
    do = fh.ConfigFile(class_file).load_classes(cnames=class_names)
    logger.info('Loaded dictionary with {} objects.'.format(len(do)))
    dr = fh.ConfigFile(rels_file).load_classes(cnames=class_names)
    logger.info('Loaded dictionary with {} relations.'.format(len(dr)))

    logger.info('Uncompressing and saving output file...')
    if object_file:
        save_aligned_with_objects(drels, object_file, do, dr, output, cnames=class_names, screen=True)
    else:
        save_aligned_no_objects(drels, do, dr, output, cnames=class_names, screen=True)
    logger.info('File saved at: %s' % output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_file', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-r', '--relation_file', help='File containing ids and their relations', default='relations.cfg')
    parser.add_argument('-f', '--obj_file', default=None,
                        help='File containing bounding boxes of objects to assure relations only for existent objects')
    args = parser.parse_args()
    
    decompress_relations(args.input, args.output, args.class_file, args.relation_file, args.obj_file)
