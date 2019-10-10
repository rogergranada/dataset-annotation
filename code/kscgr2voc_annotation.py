#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script converts the KSCGR name files from LIS annotation to the VOC paths of the
mapping file. Before executing this script, `kscgr2voc_dataset.py` should be executed
to generate the mapping file.
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

def main(lis_file, map_file, output=None):
    """ Convert KSCGR paths to VOC paths. `lis_file` contains the concatenation
        of all annotated files, i.e., all images concatenated.        
    """
    if not output:
        output = join(dirname(lis_file), 'voc_paths.txt')

    dpaths = {}
    with open(map_file) as fin:
        for line in fin:
            path_kscgr, path_voc = line.strip().split(' : ')
            dpaths[path_kscgr] = path_voc

    lis_annotation = lis.LIS(lis_file)
    pb = progressbar.ProgressBar(lis_annotation.count_lines())
    with open(lis_annotation) as flis, open(output, 'w') as fout:
        for content in flis:
            #0	egg	(58,241,19,16)	0	/home/roger/KSCGR/data3/boild-egg/rgb256/0.jpg
            fout.write('%s\t%s\t%s\t%s\t%s\n' % (flis.idfr, flis.obj, content[2], flis.idobj, dpaths[flis.path]))
            pb.update()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('lis_file', metavar='lis_annotation', help='Path to the file containing the LIS annotation.')
    argparser.add_argument('map_file', metavar='map_file', help='Path to the file containing the mapping between KSCGR and VOC.')
    argparser.add_argument('-o', '--output', help='Path to the file where the new annotation is recorded.', default=None)
    args = argparser.parse_args()
    main(args.lis_file, args.map_file, output=args.output)

