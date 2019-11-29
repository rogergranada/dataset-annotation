#!/usr/bin/env python
# coding: utf-8
"""
This script reads a file containing relations as:

Frame \t Subject \t Relation \t Object

Or 

Initial_frame - Final_frame - Id_subject - Id_relation - Id_object

and creates a file containing a list of these relations without repetition.
"""
import sys
import os
import argparse
from os.path import join, dirname, splitext, basename
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import filehandler as fh


def show_relations(file_input, output=None, class_file='classes.cfg', rels_file='relations.cfg', keep_names=False):
    if not output:
        fname, _ = splitext(basename(file_input))
        output = join(dirname(file_input), fname+'_list.txt')

    # Load classes for objects from dict {0: 'rel0', 1: 'rel1'}
    do = fh.ConfigFile(class_file).load_classes(cnames=True)
    logger.info('Loaded dictionary with {} objects.'.format(len(do)))
    dr = fh.ConfigFile(rels_file).load_classes(cnames=True)
    logger.info('Loaded dictionary with {} relations.'.format(len(dr)))

    # Check whether the file contains names or ids
    with open(file_input) as fin:
        for line in fin:
            if line[0].isdigit():
                break
    
    arr = line.strip().split('-')
    if len(arr) == 5: 
        #0-15-o1-r-o2
        handler = fh.CompressedFile(file_input)
    else: 
        #0-o1,r,o2
        handler = fh.DecompressedFile(file_input)
    list_rels = handler.list_relations(as_set=True)

    with open(output, 'w') as fout:
        for o1, r, o2 in sorted(list_rels):
            fout.write('{} {} {}\n'.format(o1, r, o2))
    logger.info('File saved at: %s' % output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_file', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-r', '--relation_file', help='File containing ids and their relations', default='relations.cfg')
    parser.add_argument('-n', '--store_names', help='Save names for objects and relations instead of their ids.', action='store_true')
    args = parser.parse_args()
    
    show_relations(args.input, args.output, args.class_file, args.relation_file, args.store_names)
