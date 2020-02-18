#!/usr/bin/env python
# coding: utf-8
"""
This script reads a file containing objects as:

id_frame \t object_name \t (x,y,w,h) \t id_object \t path_to_image

where `(x,y,w,h)` is a bounding box annotated for 256x256 squared image. 
The generated file contains the same annotation but with a bounding box
resized to the original 640x480 image. 

This conversion has the drawback of cutting the edges of objects that are
not presented in 256x256 images.
"""
import sys
import os
import argparse
from os.path import join, dirname, splitext, basename
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import filehandler as fh
import progressbar as pbar


def convert_bounding_box(file_input, output=None):
    if not output:
        fname, _ = splitext(basename(file_input))
        output = join(dirname(file_input), fname+'_original.txt')

    
    df = fh.LisFile(file_input)
    pb = pbar.ProgressBar(df.nb_frames())
    header = False
    with df as fin, open(output, 'w') as fout:
        for idfr, obj, _, idobj, path in df:
            if idfr == '0' and not header:
                fout.write('Frame:\tLabel:\tPoints:\tBounding Box ID:\tFrame path: %s\n' % df.path)
                header = True
            #print idfr, obj, df.x, df.y, df.w, df.h, idobj, path
            x = 80 + (df.x * 1.875)
            y = df.y * 1.875
            w = df.w * 1.875
            h = df.h * 1.875
            fout.write('%s\t%s\t(%d,%d,%d,%d)\t%s\t%s\n' % (idfr, obj, x, y, w, h, idobj, path))
            #pb.update()
        fout.write('---\nModified on:\t10.1.2019\t16:43')
    logger.info('File saved at: %s' % output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_file', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    args = parser.parse_args()
    
    convert_bounding_box(args.input, args.output)
