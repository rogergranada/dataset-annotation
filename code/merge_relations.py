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

import progressbar
import filehandler as fh


def merge_annotation(folder_input, output=None):
    if not output:
        output = join(folder_input, 'merged_relations.txt')

    files = fh.FolderHandler(folder_input)
    with open(output, 'w') as fout:
        fout.write('Frame\tSubject\tRelation\tObject\n')
        for path in files:
            filerels = fh.DecompressedFile(path)
            with filerels as frels:
                for fr, o1, r, o2 in frels:
                    fout.write('%d\t%s\t%s\t%s\n' % (fr, o1, r, o2))
            logger.info('Recorded file: %s' % path)
    logger.info('Saved relations in file: %s' % output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    args = parser.parse_args()
    
    merge_annotation(args.input, args.output)
