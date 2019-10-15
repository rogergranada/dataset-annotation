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

import lis
import progressbar

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
        # VOC cannot have xmin or ymin equals zero
        if x <= 0: 
            w -= x-1
            x = 1
        if y <= 0: 
            h -= y-1
            y = 1
        xmin = x
        ymin = y
        xmax = x + w
        ymax = y + h 
        if xmax > 256:
            xmax = 256
        if ymax > 256:
            ymax = 256

        obj = ET.SubElement(self.xml, "object")
        ET.SubElement(obj, "name").text = name
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = '0'
        ET.SubElement(obj, "difficult").text = '0'
        bbox = ET.SubElement(obj, "bndbox")
        ET.SubElement(bbox, "xmin").text = str(xmin)
        ET.SubElement(bbox, "ymin").text = str(ymin)
        ET.SubElement(bbox, "xmax").text = str(xmax)
        ET.SubElement(bbox, "ymax").text = str(ymax)
    
    def save_xml(self, folderout):
        """ Save the XML corresponding to an image in folderout """
        fname, _ = splitext(self.filename)
        fileout = join(folderout, fname+'.xml')
        tree = ET.ElementTree(self.xml)
        tree.write(fileout, pretty_print=True)
# End of VOCFile class


def main(inputfile, folderout):
    if not isdir(folderout):
        os.mkdir(folderout)

    fann = lis.LIS(inputfile)
    pb = progressbar.ProgressBar(fann.count_lines())
    with fann as flis:
        last_id = -1
        for v in flis:
            idf = flis.id()
            #0 \t object \t (52,104,52,43) \t 0 \t data1/boild-egg/0.jpg 
            if last_id == -1:
                last_id = idf
                xml = VOCFile(flis.path, width=256, height=256)
                xml.add_object(flis.obj, flis.x, flis.y, flis.w, flis.h)
            elif idf != last_id:
                last_id = idf
                xml.save_xml(folderout)
                xml = VOCFile(flis.path, width=256, height=256)
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
