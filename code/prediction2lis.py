#!/usr/bin/env python
# coding: utf-8
"""
This script converts the predicted bounding boxes in the form:

Frame;xmin;ymin;xmax;ymax;id_class;score

to the LIS annotation in the form:

frame_id \t object \t (x, y, width, height) \t object_id \t path_to_img

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
import progressbar as pbar


def convert_to_lis(file_input, output=None, class_file='classes.cfg', home_path=None):
    if not output:
        fname, _ = splitext(basename(file_input))
        output = join(dirname(file_input), fname+'_lis.txt')

    # Load classes for objects from dict {0: 'rel0', 1: 'rel1'}
    fpred = fh.PredictionFile(file_input)
    do = fh.ConfigFile(class_file).load_classes(cnames=False)
    logger.info('Loaded dictionary with {} objects.'.format(len(do)))

    logger.info('Converting objects to LIS annotation...')
    pb = pbar.ProgressBar(fpred.nb_lines())
    with open(output, 'w') as fout, fpred as fp:
        fout.write('Frame:\tLabel:\tPoints:\tBounding Box ID:\tFrame path:\n')
        for frame, xmin, ymin, xmax, ymax, id_class, _ in fp:
            points = (xmin, ymin, xmax-xmin, ymax-ymin)
            path = join(home_path, str(frame)+'.jpg')
            fout.write('{}\t{}\t{}\t{}\t{}\n'.format(frame, do[id_class], points, id_class, path))
            pb.update()
    print
    logger.info('Saved {} objects'.format(fpred.nb_lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_file', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-p', '--path', help='Path to add to each image.', default='/home/roger/KSCGR/')
    args = parser.parse_args()
    
    convert_to_lis(args.input, args.output, args.class_file, args.path)
