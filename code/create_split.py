#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script creates a random split of training and validation sets.
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import argparse
from os.path import dirname, join
import random

import utils

SIZE_TRAIN=0.8 # 80 percent of the dataset

def split_train_test(vfiles, size_train, perc=True):
    """ Split dataset into train and test sets. When perc=True,
        the value of `size_train` must be between 0 and 1
    """
    random_list = vfiles[:]
    random.shuffle(random_list)
    if perc:
        sizev = len(random_list)
        size_train = int(sizev*size_train)
    vtrain = random_list[:size_train]
    vtest = random_list[size_train:]
    return vtrain, vtest


def main(inputfile, dirout=None):
    if not dirout:
        dirout = dirname(inputfile)
    vnames = utils.images_from_file(inputfile, extension=False)
    vtrain, vtest = split_train_test(vnames, SIZE_TRAIN, perc=True)
    with open(join(dirout, 'train.txt'), 'w') as fout:
        for idfile in vtrain:
            fout.write('%s\n' % idfile)
    with open(join(dirout, 'test.txt'), 'w') as fout:
        for idfile in vtest:
            fout.write('%s\n' % idfile)
    

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('inputfile', metavar='file_input', help='Path to the file containing paths of the dataset.')
    argparser.add_argument('-o', '--output', help='Path to the folder where train and test files are saved.', default=None)
    args = argparser.parse_args()
    main(args.inputfile, args.output)

