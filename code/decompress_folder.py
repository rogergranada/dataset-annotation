#!/usr/bin/env python
# coding: utf-8
"""
This script reads a folder and decompress all files inside the folder

"""
import sys
import os
import argparse
from os.path import join, basename
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import filehandler as fh
import decompress_relations as dr 


def decompress_data(folder_input, output=None, class_file='classes.cfg', rels_file='relations.cfg'):
    if not output:
        output = join(folder_input, 'decompressed.tmp')
        output = fh.mkdir_from_file(output)

    # load files
    compfiles = fh.FolderHandler(folder_input)
    for file_input in compfiles:
        foutput = join(output, basename(file_input))
        dr.decompress_relations(file_input, output=foutput, class_file=class_file, rels_file=rels_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Folder containing relations')
    parser.add_argument('-o', '--output', help='Output folder', default=None)
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-r', '--relation_file', help='File containing ids and their relations', default='relations.cfg')
    args = parser.parse_args()
    
    decompress_data(args.input, args.output, args.class_file, args.relation_file)
