#!/usr/bin/env python
# coding: utf-8
"""

"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import sys
import os
import argparse
from os.path import join, dirname, isdir
import random

import filehandler as fh

SPLITS = [10, 20, 30, 50, 70]

def save_file(fileoutput, sampling, idx2rels):
    logger.info('Saving splitted observations at: {}'.format(fileoutput)) 
    with open(fileoutput, 'w') as fout:
        fout.write('Frame\tSubject\tRelation\tObject\n')
        id = 0
        for idfr in sorted(sampling):
            for s, r, o in idx2rels[idfr]:
                fout.write('{}\t{}\t{}\t{}\n'.format(id, s, r, o))
            id += 1
 

def split_file(path, split, folders):
    filerels = fh.DecompressedFile(path)
    idx2rels = {}
    with filerels as frels:
        fname_in = frels.filename
        for idfr, arr in frels.iterate_frames():
            idx2rels[idfr] = arr
    
    for split in sorted(folders):
        perc = int(len(idx2rels)*split/100)
        logger.info('Creating split with {}%: {}*0.{} = {} observations'.format(split, len(idx2rels), split, perc))
        indexes = list(idx2rels.keys())
        sampling = random.choices(indexes, k=perc)

        fileoutput = join(folders[split], fname_in)
        save_file(fileoutput, sampling, idx2rels)


def split_data(folder_input, output=None):
    if not output:
        output = join(folder_input, 'splits.tmp')
        output = fh.mkdir_from_file(output)
    
    # create folders
    folders = {}
    for split in SPLITS:
        folder_out = join(output, str(split))
        folder_out = fh.mkdir_from_file(folder_out)
        folders[split] = folder_out

    files = fh.FolderHandler(folder_input)
    for path in files:
        logger.info('Processing file: %s' % path)
        split_file(path, split, folders)
    
    logger.info('Finished successfully!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    args = parser.parse_args()
    
    split_data(args.input, args.output)
