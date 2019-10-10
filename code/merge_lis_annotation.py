#!/usr/bin/env python
# coding: utf-8
import sys
import os
import argparse
from os.path import join, dirname
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import lis
import progressbar

HOME='/usr/share/datasets/KSCGR/'

def merge(folder_input, output=None):
    if not output:
        output = join(folder_input, 'merged_annotations.txt')

    list_files = [files for _, _, files in os.walk(folder_input)]
    list_files = sorted(list_files)[0]
    with open(output, 'w') as fout:
        fout.write('Frame:\tLabel:\tPoints:\tBounding Box ID:\tFrame path:\n')
        for i, f in enumerate(list_files, start=1):
            lis_file = join(folder_input, f)
            logger.info('Processing file [%d/%d]: %s' % (i, len(list_files), lis_file))
            fann = lis.LIS(lis_file)
            pb = progressbar.ProgressBar(fann.count_lines())
            with fann as flis:
                for arr in flis:
                    #0 \t egg \t (58,241,19,16) \t 0 \t data1/boild-egg/0.jpg
                    fout.write('%s\t%s\t%s\t%s\t%s\n' % (flis.idfr, flis.obj, arr[2], flis.idobj, join(HOME, flis.path)))
                    pb.update()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    args = parser.parse_args()
    
    merge(args.input, output=args.output)
