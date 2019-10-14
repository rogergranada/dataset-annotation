#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script creates train, validation, trainval and test files.
In KSCGR we use all images from data3 as validation and data6 and data7
as testing set. Thus, training set is composed by data1, data2, data4 and data5.
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import os
import sys
import shutil
import argparse
from os.path import splitext, basename, isdir, join, dirname

import lis
import progressbar

def main(lis_file, map_file):
    """   
    """
    TRAIN = ['data1', 'data2', 'data4', 'data5']
    VAL = ['data3']
    TEST = ['data6', 'data7'] #TODO: Annotate test files

    ftrain = join(dirname(lis_file), 'train.txt')
    ftrainval = join(dirname(lis_file), 'trainval.txt')
    fval = join(dirname(lis_file), 'val.txt')
    ftest = join(dirname(lis_file), 'test.txt')

    dpaths = {}
    with open(map_file) as fin:
        for line in fin:
            path_kscgr, path_voc = line.strip().split(' : ')
            dpaths[path_kscgr] = path_voc

    lis_annotation = lis.LIS(lis_file)
    dtra, dval, dtrv, dtst = {}, {}, {}, {}
    with lis_annotation as flis:
        last_path = ''
        for content in flis:
            path = '/'.join(content[4].split('/')[1:7])
            if path != last_path:
                logger.info('Processing: /%s' % path)
                last_path = path
            data = content[4].split('/')[5]
            fname, _ = splitext(basename(dpaths[content[4]]))
            fname = int(fname)
            if data in TRAIN: dtra[fname] = ''
            if data in TRAIN or data in VAL: dtrv[fname] = ''
            if data in VAL: dval[fname] = ''
            if data in TEST: dtst[fname] = ''

    with open(ftrain, 'w') as fout:
        for fname in sorted(dtra):
            fout.write('%s\n' % str(fname).zfill(6))
    with open(ftrainval, 'w') as fout:
        for fname in sorted(dtrv):
            fout.write('%s\n' % str(fname).zfill(6))
    with open(fval, 'w') as fout:
        for fname in sorted(dval):
            fout.write('%s\n' % str(fname).zfill(6))
    #with open(ftest, 'w') as fout:
    #    for fname in sorted(dtst):
    #        fout.write('%s\n' % str(fname).zfill(6))

    # REMOVE after annotating TEST files
    with open(ftest, 'w') as fout:
        for i in range(fname+1, fname+55783):
            fout.write('%s\n' % str(i).zfill(6))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('lis_file', metavar='lis_annotation', help='Path to the file containing the LIS annotation.')
    argparser.add_argument('map_file', metavar='map_file', help='Path to the file containing the mapping between KSCGR and VOC.')
    args = argparser.parse_args()
    main(args.lis_file, args.map_file)

