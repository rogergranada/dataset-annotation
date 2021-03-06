#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script converts the KSCGR name files and structure folder to VOC structure folder,
i.e., convert the structure of folders to a single folder with increasingly sorted names
for VOC annotation.

KSCGR folders are in the format:

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

VOC folder has the format:

VOC/
- JPEGImages/
  - 000001.jpg
  - 000002.jpg
  - ...

We convert to VOC format due to faster-rcnn.pytorch format to train and test data. 
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import os
import sys
import shutil
import argparse
from os.path import splitext, basename, isdir, join, dirname

def main(kscgrfile, vocfolder):
    """ Convert KSCGR folder format to VOC format """
    if isdir(vocfolder):
        folderout = join(vocfolder, 'JPEGImages')
        if not isdir(folderout):
            os.mkdir(folderout)
    else:
        logger.error("'%s' is not a valid folder" % vocfolder)
        sys.exit(0)
    fout_paths = join(vocfolder, 'paths.txt')
    fout_map = join(dirname(kscgrfile), 'map_paths.txt')
    with open(kscgrfile) as fin, \
         open(fout_paths, 'w') as fout, \
         open(fout_map, 'w') as fout_map:
        for i, line in enumerate(fin, start=1):
            path = line.strip().split()[0]
            namefile, ext = splitext(basename(path))
            fname = str(i).zfill(6)
            pathout = join(folderout, fname+'.jpg')
            fout.write('%s\n' % pathout)
            shutil.copy2(path, pathout)
            fout_map.write('%s : %s\n' % (path, pathout))
            if namefile == '0':
                logger.info('Renaming: %s -> %s' % (path, pathout))
    logger.info('All files copied into %s' % folderout)
    logger.info('Saved map_paths.txt at: %s' % fout_map)
    logger.info('Saved paths.txt at: %s' % fout_paths)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('inputfile', metavar='input', help='Path to the file containing paths of the KSCGR dataset.')
    argparser.add_argument('vocfolder', metavar='voc', help='Path to the folder where images are recorded.')
    args = argparser.parse_args()
    main(args.inputfile, args.vocfolder)

