#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script resizes images from the dataset
"""
import sys
sys.path.insert(0, '..')
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import argparse
import os
import cv2
from os.path import realpath, join, exists, dirname

# customized files
import filehandler as fh
import progressbar as pbar

def resize_image(img, size):
    """
    Resize a image to `size`

    Parameters:
    -----------
    img : numpy.ndarray
        image after read by cv2.imread()
    size : int
        new size of the image
    """
    width = int(img.shape[1])
    height = int(img.shape[0])
    new_width = 0
    crop = 0

    if width < height:
        new_width = size
        new_height = (size * height) / width
        crop = new_height - size
        img = cv2.resize(img, (new_width, new_height), 0, 0, cv2.INTER_CUBIC)
        img = img[crop / 2:size + (crop / 2), :]
    else:
        new_height = size
        new_width = (size * width) / height
        crop = new_width - size      
        img = cv2.resize(img, (new_width, new_height), 0, 0, cv2.INTER_CUBIC)
        img = img[:, crop / 2:size + (crop / 2)]
    return img


def resize_file(imgpath, outpath, size):
    """
    Receives the path of an image and resize it to `size`
    
    Parameters:
    -----------
    impath : string
        path to the input image
    outpath : string
        path to the output image
    size : int
        new size of the image
    """
    imgpath = realpath(imgpath)
    outpath = realpath(outpath)
    img = cv2.imread(imgpath)
    img = resize_image(img, size)
    cv2.imwrite(outpath, img)
    return img


def resize_from_file(inputfile, outputfolder, size):
    """
    Receives the path of a file and resize all images in this
    file to size=`size`
    
    Parameters:
    -----------
    input : string
        path to the input file containing multiple images
    output : string
        path to the output folder
    size : int
        new size of the image
    """
    logger.info('Resizing images to: %dx%d' % (size, size))
    if not exists(outputfolder):
        os.makedirs(outputfolder)

    with fh.PathFile(inputfile) as pf:
        pb = pbar.ProgressBar(pf.nb_lines())
        for _ in pf:
            #logger.info('processing file: %s' % impath)
            outpath = join(outputfolder, pf.fname)
            resize_file(pf.path, outpath, size)
            pb.update()
    logger.info('Processed %d files' % pf.nb_lines())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_file', help='Plain text file')
    parser.add_argument('output', help='Folder to save resized images')
    parser.add_argument('-s', '--size', help='Size of the new images', type=int, default=256)
    args = parser.parse_args()
    
    resize_from_file(args.input, args.output, args.size)
