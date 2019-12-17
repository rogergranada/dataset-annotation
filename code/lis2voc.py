#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Convert LIS annotation to VOC annotation. LIS annotation has
the following format after the heading (spaces are added for
a better reading):

frame_id \t object \t (x, y, width, height) \t object_id \t path_to_img

On the other hand, VOC has an XML format described as:

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
"""
import sys
sys.path.insert(0, '..')
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import os
import argparse
from os.path import join, isdir, splitext, basename
from lxml import etree as ET
from PIL import Image

import progressbar as pbar
import filehandler as fh


def main(inputfile, folderout):
    if not isdir(folderout):
        os.mkdir(folderout)

    fann = fh.LisFile(inputfile)
    pb = pbar.ProgressBar(fann.count_lines())
    with fann as flis:
        last_id = -1
        for v in flis:
            idf = flis.id()
            #0 \t object \t (52,104,52,43) \t 0 \t data1/boild-egg/0.jpg 
            if last_id == -1:
                last_id = idf
                xml = fh.VOCFile(flis.fname, width=256, height=256)
                xml.add_object(flis.obj, flis.x, flis.y, flis.w, flis.h)
            elif idf != last_id:
                last_id = idf
                xml.save_xml(folderout)
                xml = fh.VOCFile(flis.fname, width=256, height=256)
                xml.add_object(flis.obj, flis.x, flis.y, flis.w, flis.h)
            else:
                xml.add_object(flis.obj, flis.x, flis.y, flis.w, flis.h)
            pb.update()
        xml.save_xml(folderout)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', metavar='file_input', help='File containing LIS annotation')
    parser.add_argument('output', metavar='folder_output', help='Folder to save the VOC annotation')
    args = parser.parse_args()
    main(args.inputfile, args.output)
