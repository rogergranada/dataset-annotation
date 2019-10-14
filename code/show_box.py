#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script draws bouding boxes on an image in order to show their position. It receives as input
or an image with the corners of the bounding box as minimum X value (xmin), minimum Y value (ymin), 
maximum X value (xmax) and maximum Y value (ymax). For exemple:

```
$ show_box.py image.jpg 10 10 50 100
```
or a file containing the path to the image followed by a sequence of bounding boxes as:

```
path_to_image.jpg xmin,ymin,xmax,ymax,class xmin,ymin,xmax,ymax,class xmin,ymin,xmax,ymax,class
```
where `class` is the id of the class representing the bounding box. The resulting image will contain
all bounding boxes in the line. When using this option, the user must pass `--txt` as argument as:

```
$ show_box.py file_with_images.txt --txt
```
"""

import argparse
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import colors
import numpy as np
import ast


def draw_box(img, boundaries):
    im = np.array(Image.open(img), dtype=np.uint8)
    fig, ax = plt.subplots(1)
    ax.imshow(im)
   
    xmin, ymin, xmax, ymax = boundaries
    rect = patches.Rectangle((xmin, ymin), xmax-xmin, ymax-ymin, linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect)
    plt.show()


def draw_from_file(fileinput):
    with open(fileinput) as fin:
        for line in fin:
            arr = line.strip().split()
            img = arr[0]
            im = np.array(Image.open(img), dtype=np.uint8)
            fig, ax = plt.subplots(1)
            ax.imshow(im)

            for i, pos_label in enumerate(arr[1:]):
                pos_label = ast.literal_eval(pos_label)
                xmin, ymin, xmax, ymax, class_id = pos_label
                cname = colors.cnames.keys()[i]
                rect = patches.Rectangle((xmin, ymin), xmax-xmin, ymax-ymin, 
                                         linewidth=1, edgecolor=cname, facecolor='none')
                ax.add_patch(rect)
            plt.show()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('imgfile', metavar='image', help='Path to the image')
    argparser.add_argument('-t', '--txt', help='In case imgfile is a text file containing multiple boxes', action='store_true')
    argparser.add_argument('-x', '--xmin_value', help='Pixel top left of the box in X', type=int, default=0)
    argparser.add_argument('-y', '--ymin_value', help='Pixel top left of the box in Y', type=int, default=0)
    argparser.add_argument('-X', '--xmax_value', help='Pixel bottom right of the box in X', type=int, default=0)
    argparser.add_argument('-Y', '--ymax_value', help='Pixel bottom right of the box in Y', type=int, default=0)
    args = argparser.parse_args()

    if args.txt:
        draw_from_file(args.imgfile)
    else:
        draw_box(args.imgfile, [args.xmin_value, args.ymin_value, args.xmax_value, args.ymax_value])

