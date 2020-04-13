#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Convert VOC annotation to LIS annotation. VOC annotation has
the following format for each file in a folder:

<annotation>
    <folder>folder_name</folder>
    <filename>image_file.jpg</filename>
    <size>
        <width>256</width>
        <height>256</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
    <object>
        <name>object_name</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>x</xmin>
            <ymin>y</ymin>
            <xmax>x+w</xmax>
            <ymax>y+h</ymax>
        </bndbox>
    </object>
<annotation>

while LIS annotation contains the following format after the heading 
(spaces are added for a better reading):

frame_id \t object \t (x, y, width, height) \t object_id \t path_to_img
"""
import sys
sys.path.insert(0, '..')
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import os
import argparse
from os.path import join, isdir, splitext, basename, dirname
from lxml import etree as ET
from PIL import Image

import progressbar as pbar
import filehandler as fh


def main(inputfolder, fileoutput):
    if not fileoutput:
        fileoutput = join(inputfolder, '../lis_annotation.txt')
    fileclasses = join(dirname(fileoutput), 'classes.txt')
    
    dclasses = {}
    fhandler = fh.FolderHandler(inputfolder, ext='xml', sort_id=True)
    nb_files = fhandler.nb_files()
    pb = pbar.ProgressBar(nb_files)
    logger.info('Processing %d files!' % nb_files)
    with open(fileoutput, 'w') as fout:
        ##0 \t object \t (52,104,52,43) \t 0 \t data1/boild-egg/0.jpg
        fout.write('Frame:\tLabel:\tPoints:\tBounding Box ID:\tFrame path\n')
        for fname in fhandler:
            id = fhandler.id
            fvoc = fh.VOCXML(fname)
            path = fvoc.image_path()
            objs = fvoc.extract_objects()
            for obj in objs:
                name, dpos = obj
                if not dclasses.has_key(name):
                    dclasses[name] = len(dclasses)
                w = dpos['xmax'] - dpos['xmin']
                h = dpos['ymax'] - dpos['ymin']
                fout.write('%d\t%s\t(%d,%d,%d,%d)\t%d\t%s\n' % (id, name, dpos['xmin'], dpos['ymin'], w, h, dclasses[name], path))
            pb.update()
        fout.write('---\nModified on:\t11.11.2011\t11:11')
    logger.info('Saved output file at: %s' % fileoutput)
    with open(fileclasses, 'w') as fout:
        for cl in dclasses:
            fout.write('%d %s\n' % (dclasses[cl], cl))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfolder', metavar='folder_input', help='Folder containing XML files with VOC annotation')
    parser.add_argument('output', metavar='file_output', help='File to save the LIS annotation')
    args = parser.parse_args()
    main(args.inputfolder, args.output)
