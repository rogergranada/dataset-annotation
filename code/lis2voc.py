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
import ast
from os.path import dirname, join, exists, isdir
from os.path import splitext, basename, dirname
#import xml.etree.cElementTree as ET
from lxml import etree as ET
from PIL import Image


class VOCFile(object):
    def __init__(self, image_file, width=None, height=None):
        self.filename = basename(image_file)
        self.width = width
        self.height = height
        if not width or not height:
            im = Image.open(image_file)
            self.width, self.height = im.size
        self._create_header()

    def _create_header(self):
        """ Create XML with information of the image """
        self.xml = ET.Element('annotations')
        ET.SubElement(self.xml, 'folder').text = 'JPEGImages'
        ET.SubElement(self.xml, 'filename').text = self.filename    
        imsize = ET.SubElement(self.xml, 'size')
        ET.SubElement(imsize, 'width').text = str(self.width)
        ET.SubElement(imsize, 'height').text = str(self.height)
        ET.SubElement(imsize, 'depth').text = '3'
        ET.SubElement(self.xml, 'segmented').text = '0' 

    def add_object(self, name, x, y, w, h):
        """ Add the annotation for an object """
        xmin = str(x)
        ymin = str(y)
        xmax = str(x + w)
        ymax = str(y + h) 
        obj = ET.SubElement(self.xml, "object")
        ET.SubElement(obj, "name").text = name
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = '0'
        ET.SubElement(obj, "difficult").text = '0'
        bbox = ET.SubElement(obj, "bndbox")
        ET.SubElement(bbox, "xmin").text = xmin
        ET.SubElement(bbox, "ymin").text = ymin
        ET.SubElement(bbox, "xmax").text = xmax
        ET.SubElement(bbox, "ymax").text = ymax
    
    def save_xml(self, folderout):
        """ Save the XML corresponding to an image in folderout """
        fname, _ = splitext(self.filename)
        fileout = join(folderout, fname+'.xml')
        tree = ET.ElementTree(self.xml)
        tree.write(fileout, pretty_print=True)


def main(inputfile, folderout):
    if not isdir(folderout):
        os.mkdir(folderout)
    with open(inputfile) as fin:
        last_id = -1
        for line in fin:
            if line.startswith('Frame') or \
               line.startswith('---') or \
               line.startswith('Modified'):
                continue
            #0 \t object \t (52,104,52,43) \t 0 \t data1/boild-egg/0.jpg 
            arr = line.strip().split('\t')
            idfr = int(arr[0])
            obj = arr[1]
            x, y, w, h = map(int, ast.literal_eval(arr[2]))
            idobj = arr[3]
            path = arr[4]

            if last_id == -1:
                xml = VOCFile(path, width=256, height=256)
                xml.add_object(obj, x, y, w, h)
                last_id = idfr
            elif idfr != last_id:
                xml.save_xml(folderout)
                xml = VOCFile(path, width=256, height=256)
                xml.add_object(obj, x, y, w, h)
                last_id = idfr
            else:
                xml.add_object(obj, x, y, w, h)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', metavar='file_input', help='File containing LIS annotation')
    parser.add_argument('output', metavar='folder_output', help='Folder to save the VOC annotation')
    #parser.add_argument('-o', '--output', help='Folder to save the VOC annotation', default=None)
    args = parser.parse_args()

    main(args.inputfile, args.output)
