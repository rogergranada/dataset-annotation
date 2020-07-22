#!/usr/bin/env python
# coding: utf-8
"""
From a file containing Decompressed relations, this script generates 
a set of files containing SPLITS percentage of the dataset. Thus, a
file containing 100 frames, this script creates a folder `10/` containing
a file with the same name of the input file, but containing only 10% of 
the total of frames. Thus, the file contains 10 frames. The same is valid
for `20/`, `30/`, `50/` and `70/`. The last containing 70% of the frames.
 
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
    """ Save the selected sampling frames in the output file. 

        Parameters:
        -----------
        fileoutput: string
            path where the content is saved
        sampling: array
            list containing the selected indexes to be saved
        idx2rels: dict
            dictionary containing the id of the frame as key and
            the relationship as value
    """ 
    logger.info('Saving splitted observations at: {}'.format(fileoutput)) 
    with open(fileoutput, 'w') as fout:
        fout.write('Frame\tSubject\tRelation\tObject\n')
        id = 0
        for idfr in sorted(sampling):
            for s, r, o in idx2rels[idfr]:
                fout.write('{}\t{}\t{}\t{}\n'.format(id, s, r, o))
            id += 1
 

def split_file(path, folders):
    """ Create the set of splits for a single file.
        
        Parameters:
        -----------
        path: string
            path to the input Decompressed file
        folders: dict 
            dictionary containing the id of the split as key
            and the path to the folder where the split is 
            saved as value.
    """
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


def split_from_folder(folder_input, output=None):
    """ Read a folder containing Decompressed files and 
        create a split dataset for each file.

        Parameters:
        -----------
        folder_input: string
            path to the folder containing Decompressed files
        output: string (optional)
            path to the folder where the files containing splits
            are saved.
    """
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
        split_file(path, folders)
    logger.info('Finished successfully!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    args = parser.parse_args()
    
    split_from_folder(args.input, args.output)
