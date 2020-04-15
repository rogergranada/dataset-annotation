#!/usr/bin/env python
# coding: utf-8
"""
This script merges all files containing bounding boxes of objects. 

The input to the script is the folder containing all annotated files (e.g., `data1-boild_egg.txt`,
`data1-ham_egg.txt`, `data1-kinshi_egg.txt`, ..., `data5-scrambled_egg.txt`) and outputs a 
`merged_bboxes.txt` file containing the concatenation of all annotations.

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


def merge_annotation(folder_input, output=None, class_file='classes.cfg'):
    if not output:
        output = join(folder_input, 'merged_bboxes.txt')

    # Load classes for objects from dict {0: 'rel0', 1: 'rel1'}
    do = fh.ConfigFile(class_file).load_classes(cnames=True)
    logger.info('Loaded dictionary with {} objects.'.format(len(do)))

    files = fh.FolderHandler(folder_input)
    with open(output, 'w') as fout:
        fout.write('Frame\tLabel\tPoints\tBounding Box ID\tFrame path:\n')
        for path in files:
            logger.info('Processing file: %s' % path)
            filelis = fh.LisFile(path)
            with filelis as flis:
                for arr in flis:
                    check_error(do, flis.obj, flis.nb_line)
                    # 0	table	(0,112,101,142)	29	0.jpg
                    fout.write('%s\t%s\t%s\t%s\t%s\n' % (arr[0], arr[1], arr[2], arr[3], join(flis.path, arr[4])))
    logger.info('Saved bounding boxes in file: %s' % output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    args = parser.parse_args()
    
    merge_annotation(args.input, args.output, args.class_file)
