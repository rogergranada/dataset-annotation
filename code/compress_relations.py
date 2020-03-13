#!/usr/bin/env python
# coding: utf-8
"""
This script reads a file containing relations as:

Frame \t Subject \t Relation \t Object

and creates a file containing a compressed annotation with the sequence 
of frames for a relation as:

Initial_frame - Final_frame - Id_subject - Id_relation - Id_object

Thus, an example file containing:

0\tperson\tholding\tshell-egg
1\tperson\tholding\tshell-egg
1\tperson\tmoving\tshell-egg
2\tperson\tholding\tshell-egg
2\tperson\tmoving\tshell-egg
3\tperson\tholding\tshell-egg
4\tperson\tholding\tshell-egg
4\tshell-egg\ton\tbowl

generates the following lines:

0-4-1-3-7
1-2-1-4-7
4-4-7-1-17

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

import filehandler as fh


def compress_relations(file_input, output=None, class_file='classes.cfg', rels_file='relations.cfg', keep_names=False):
    if not output:
        fname, _ = splitext(basename(file_input))
        output = join(dirname(file_input), fname+'_compressed.txt')

    # Load classes for objects from dict {0: 'rel0', 1: 'rel1'}
    do = fh.ConfigFile(class_file).load_classes(cnames=True)
    logger.info('Loaded dictionary with {} objects.'.format(len(do)))
    dr = fh.ConfigFile(rels_file).load_classes(cnames=True)
    logger.info('Loaded dictionary with {} relations.'.format(len(dr)))

    df = fh.DecompressedFile(file_input)
    dcomp = df.group_relations()
    logger.info('Found {} relations spread on {} lines of the input file.'.format(len(df.start_frames), df.nb_line-1))
    logger.info('Compressed to {} lines in output file.'.format(len(df.start_frames)))

    logger.info('Saving output file...')
    with open(output, 'w') as fout:
        if keep_names:
            fout.write('Initial_frame-Final_frame Subject Relation Object\n')
        else:
            fout.write('Initial_frame-Final_frame-Subject-Relation-Object\n')
        for _, key in sorted(df.start_frames):
            start, end = dcomp[key]['contiguous'].pop(0)
            subj, rel, obj = key
            if keep_names:
                fout.write('%d-%d %s %s %s\n' % (start, end, subj, rel, obj))
            else:
                fout.write('%d-%d-%d-%d-%d\n' % (start, end, do[subj], dr[rel], do[obj]))
    logger.info('File saved at: %s' % output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_file', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-r', '--relation_file', help='File containing ids and their relations', default='relations.cfg')
    parser.add_argument('-n', '--store_names', help='Save names for objects and relations instead of their ids.', action='store_true')
    args = parser.parse_args()
    
    compress_relations(args.input, args.output, args.class_file, args.relation_file, args.store_names)
