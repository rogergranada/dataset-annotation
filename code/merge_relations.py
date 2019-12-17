#!/usr/bin/env python
# coding: utf-8
"""
This script merges all files containing relationships between objects. 

The input to the script is the folder containing all annotated files (e.g., `data1-boild_egg.txt`,
`data1-ham_egg.txt`, `data1-kinshi_egg.txt`, ..., `data5-scrambled_egg.txt`) and outputs a 
`merged_relations.txt` file containing the concatenation of all annotations.

These relations follow the ids from `obj.txt` file, which do not consider the background as a 
category.
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import sys
import os
import argparse
from os.path import join, dirname

import filehandler as fh


def check_error(dic, key, nb_line):
    if not dic.has_key(key):
        logger.error('Could not find element in dictionary: {} [LINE: {}]'.format(key, nb_line))
        sys.exit()


def merge_annotation(folder_input, output=None, class_file='classes.cfg', rels_file='relations.cfg'):
    if not output:
        output = join(folder_input, 'merged_relations.txt')

    # Load classes for objects from dict {0: 'rel0', 1: 'rel1'}
    do = fh.ConfigFile(class_file).load_classes(cnames=True)
    logger.info('Loaded dictionary with {} objects.'.format(len(do)))
    dr = fh.ConfigFile(rels_file).load_classes(cnames=True)
    logger.info('Loaded dictionary with {} relations.'.format(len(dr)))

    files = fh.FolderHandler(folder_input)
    with open(output, 'w') as fout:
        fout.write('Frame\tSubject\tRelation\tObject\n')
        for path in files:
            logger.info('Processing file: %s' % path)
            filerels = fh.DecompressedFile(path)
            with filerels as frels:
                for fr, o1, r, o2 in frels:
                    check_error(do, o1, frels.nb_lines)
                    check_error(do, o2, frels.nb_lines)
                    check_error(dr, r, frels.nb_lines)
                    fout.write('%d\t%s\t%s\t%s\n' % (fr, o1, r, o2))
    logger.info('Saved relations in file: %s' % output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-r', '--relation_file', help='File containing ids and their relations', default='relations.cfg')
    args = parser.parse_args()
    
    merge_annotation(args.input, args.output, args.class_file, args.relation_file)
