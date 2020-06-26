#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Create a video with images and the bounding box annotation.
"""
import sys
sys.path.insert(0, '..')
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import os
import argparse
import cv2
import numpy as np
from os.path import join, isdir, splitext, basename, dirname, exists
from matplotlib import colors

import progressbar as pbar
import filehandler as fh

BBOX_COLOR = [57,255,20]


def create_video_from_file(inputfile, outputfile, file_classes='classes.cfg'):
    do = fh.ConfigFile(file_classes).load_classes(cnames=True)
    img_array = []
    
    if not outputfile:
        fname, _ = splitext(basename(inputfile))
        fnameout= join(dirname(inputfile), fname+'.avi')

    fann = fh.LisFile(inputfile)
    pb = pbar.ProgressBar(fann.nb_frames())
    metadata = False
    with fann as flis:
        for fname, objs in flis.iterate_frames():
            if exists(fname):
                img = cv2.imread(fname)
                if not metadata:
                    height, width, layers = img.shape
                    size = (width, height)
                    metadata = True

                for label, xmin, ymin, w, h in objs:
                    id = do[label]
                    cname = colors.cnames.keys()[id]
                    xmax = xmin + w
                    ymax = ymin + h
                    cv2.rectangle(img, (xmin,ymin), (xmax,ymax), BBOX_COLOR, 1)
                    cv2.putText(img, label, (xmin-10,ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BBOX_COLOR, 1)
                img_array.append(img)
            else:
                logger.info('{} not a file.'.format(fname))

                
            pb.update()
    out = cv2.VideoWriter(fnameout, cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', metavar='file_input', help='File containing LIS annotation.')
    parser.add_argument('-o', '--output', help='File to save the video.', default=None)
    parser.add_argument('-c', '--classes', help='File containing classes of the dataset.', default='classes.cfg')
    args = parser.parse_args()
    create_video_from_file(args.inputfile, args.output, args.classes)
