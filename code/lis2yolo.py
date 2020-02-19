#!/usr/bin/python
#-*- coding: utf-8 -*-
""" 
Script to convert from LIS annotation to keras-yolo3 annotation. LIS annotation has the form:

```
id_frame \t label \t (x,y,w,h) \t bbox_id \t path
```

The output is the keras-yolov3 annotation in the format:

```
Path xmin,ymin,xmax,ymax,class_id xmin,ymin,xmax,ymax,class_id
``` 

It is important to note that files for YOLOv3 must have 416x416 pixels. Thus, we convert from
256x256 to 416x416 pixels each bounding box.
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import argparse
from PIL import Image
import os
import ast
from os.path import join

import utils
import progressbar as pbar
from filehandler import FolderHandler, LisFile

SIZE_KSCGR = 256
SIZE_YOLO = 416


def convert_size(xmin, xmax, ymin, ymax, size_in=256, size_out=416):
    """ Convert bounding boxes from images in `size_in` to images in `size_out` """
    xmin_out = int((float(xmin)/size_in) * size_out)
    ymin_out = int((float(ymin)/size_in) * size_out)
    xmax_out = int((float(xmax)/size_in) * size_out)
    ymax_out = int((float(ymax)/size_in) * size_out)
    return xmin_out, xmax_out, ymin_out, ymax_out


def change_annotation_file(file_lis, fout, dclasses):
    """
    Change annotation from original LIS annotation as:
        id_frame \t label \t (x,y,w,h) \t bbox_id \t path
    To keras-yolov3 annotation as:
        Path xmin,ymin,xmax,ymax,class_id xmin,ymin,xmax,ymax,class_id
    """ 
    last_index = 0
    with LisFile(file_lis) as flis:
        pb = pbar.ProgressBar(flis.nb_frames())
        for img, objs in flis.iterate_frames():
            path = join(flis.path, img)
            positions = ''
            for obj, xmin, ymin, w, h in objs:
                xmax = xmin+w
                ymax = ymin+h
                xmin, xmax, ymin, ymax = convert_size(xmin, xmax, ymin, ymax, SIZE_KSCGR, SIZE_YOLO)
                class_id = dclasses[obj]
                positions += ' %d,%d,%d,%d,%d' % (xmin, ymin, xmax, ymax, class_id)
            #print path, positions
            fout.write('%s%s\n' % (path, positions))
            pb.update()
        #pb.stop()
    return dclasses
                

def main(folder_annotation, output, cfg_file):
    """
    Convert from LIS annotation to keras-yolov3 annotation
    Save annotation in `yolo_annotation.txt` and class ids in `classes.txt`
    """  
    dclasses = utils.load_classes(cfg_file, no_background=True)
    if not output:
        output = folder_annotation
    foutput = join(output, 'yolo_annotation.txt')
    fclasses = join(output, 'classes.txt')

    with open(foutput, 'w') as fout, open(fclasses, 'w') as fclout:
        fdh = FolderHandler(folder_annotation)
        for path in fdh:
            dclasses = change_annotation_file(path, fout, dclasses)
        sorted_classes = sorted(dclasses.items(), key=lambda kv: kv[1])
        for k, v in sorted_classes:
            fclout.write('%s\n' % k)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('annotation_folder', metavar='folder_annotation', help='Path to the folder containing annotations')
    argparser.add_argument('-o', '--output', help='Folder to save annotation and class labels', default=None)
    argparser.add_argument('-c', '--classes', help='File containing classes', default='classes.cfg')
    args = argparser.parse_args()

    main(args.annotation_folder, args.output, args.classes)

