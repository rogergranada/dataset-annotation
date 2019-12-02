#!/usr/bin/env python
# coding: utf-8
"""
This script merges all files containing LIS annotation. As LIS annotation is
separated by any video, this script merges all files using a single dictionary
to keep track of all ids and labels.

The input to the script is the folder containing all annotated files (e.g., data1-boild_egg.txt,
data1-ham_egg.txt, data1-kinshi_egg.txt, ..., data5-scrambled_egg.txt) and outputs a lis_merged.txt
file containing the concatenation of all annotations.
"""
import sys
import os
import argparse
from os.path import join, dirname
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import lis
import progressbar
import utils


def merge_lis(folder_input, output=None, cfg_file='classes.cfg', home_path=None):
    if not output:
        output = join(folder_input, 'lis_merged.txt')

    dclasses = utils.load_classes(cfg_file)
    list_files = [files for _, _, files in os.walk(folder_input)]
    list_files = sorted(list_files[0])

    with open(output, 'w') as fout:
        fout.write('Frame:\tLabel:\tPoints:\tBounding Box ID:\tFrame path:\n')
        for i, f in enumerate(list_files, start=1):
            if not f.endswith('txt'): continue
            lis_file = join(folder_input, f)
            logger.info('Processing file [%d/%d]: %s' % (i, len(list_files), lis_file))
            fann = lis.LIS(lis_file)
            with fann as flis:
                for arr in flis:
                    obj = flis.obj
                    #0 \t egg \t (58,241,19,16) \t 0 \t data1/boild-egg/0.jpg
                    if obj == 'None':
                        logger.warning('None found in file: %s' % lis_file)
                    elif not obj in dclasses:
                        logger.error('Class `%s` does not exist in dictionary' % obj)
                        sys.exit(0)
                    fout.write('%s\t%s\t%s\t%s\t%s\n' % (flis.idfr, obj, flis.bbox, flis.idobj, join(home_path, flis.path, flis.fname)))
            logger.info('End of processing: %d frames' % flis.idfr)
    logger.info('File saved at: %s' % output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-c', '--config_file', help='File containing ids and classes', default='classes.cfg')
    parser.add_argument('-p', '--home_path', help='Path to add to images', default='/usr/share/datasets/KSCGR/')
    args = parser.parse_args()
    
    merge_lis(args.input, args.output, args.config_file, args.home_path)
