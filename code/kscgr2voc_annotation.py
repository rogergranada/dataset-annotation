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
    #pb = progressbar.ProgressBar(lis_annotation.count_lines())
    with lis_annotation as flis, open(output, 'w') as fout:
        last_path = ''
        for i, content in enumerate(flis, start=2):
            #0	egg	(58,241,19,16)	0	/home/roger/KSCGR/data3/boild-egg/0.jpg
            path = '/'.join(content[4].split('/')[1:7])
            if path != last_path:
                logger.info('Processing: /%s' % path)
                last_path = path
            #if content[4] == '/usr/share/datasets/KSCGR/data5/':
            #    print i
            #    break
            fout.write('%s\t%s\t%s\t%s\t%s\n' % (flis.idfr, flis.obj, content[2], flis.idobj, dpaths[content[4]]))
    logger.info('File containing new paths saved at: %s' % output)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('lis_file', metavar='lis_annotation', help='Path to the file containing the LIS annotation.')
    argparser.add_argument('map_file', metavar='map_file', help='Path to the file containing the mapping between KSCGR and VOC.')
    argparser.add_argument('-o', '--output', help='Path to the file where the new annotation is recorded.', default=None)
    args = argparser.parse_args()
    main(args.lis_file, args.map_file, output=args.output)

