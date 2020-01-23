#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script converts the VOC name files and structure folder to KSCGR structure folder,
i.e., convert the structure of a single folder to several folders for KSCGR annotation.

VOC folder has the format:

VOC/
- JPEGImages/
  - 000001.jpg
  - 000002.jpg
  - ...


while KSCGR folders are in the format:

KSCGR/
- data1/
  - boild-egg/
    - 0.jpg
    - 1.jpg
    - ...
  - ham-egg/
  - kinshi-egg/
  - omelette/
  - scramble-egg/
- data2/
  - boild-egg/
  - ham-egg/
  - ...
-...

We use a mapping file (`map_paths.txt`) to convert from one type to the other. 
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import os
import sys
import shutil
import argparse
from os.path import splitext, basename, isdir, join, dirname

import filehandler as fh
import progressbar as pbar

def main(vocfile, mapfile, output=None):
    """ Convert VOC paths to KSCGR paths """
    if not output:
        fname, _ = splitext(basename(vocfile))
        output = join(dirname(vocfile), fname+'_kscgr.txt')

    # load mapping
    dmap = fh.MapFile(mapfile).load_dictionary(key='voc')
    logger.info('Loaded mapping for {} paths'.format(len(dmap)))          

    flis = fh.LisFile(vocfile)
    pb = pbar.ProgressBar(flis.nb_lines())
    with flis as fin, open(output, 'w') as fout:
        for arr in fin:
            if not dmap.has_key(arr[-1]):
                logger.warning('Could not map file! Key do not exist. {} [LINE: {}]'.format(arr[-1], flis.nb_line)) #test flis.fname
            else:
                path = dmap[arr[-1]]
                idfr, _ = splitext(basename(path))
                fout.write('{}\t{}\t{}\t{}\t{}\n'.format(idfr, arr[1], arr[2], arr[3], path))
            pb.update()
    logger.info('File saved at: {}'.format(output))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', metavar='input', help='Path to the file containing paths of the VOC dataset.')
    parser.add_argument('mapfile', metavar='map_paths', help='Path to the file containing the mapping between annotations.')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    args = parser.parse_args()
    main(args.inputfile, args.mapfile, args.output)

