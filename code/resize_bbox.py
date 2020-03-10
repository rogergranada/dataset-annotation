#!/usr/bin/python
#-*- coding: utf-8 -*-
""" 
Convert the bounding box annotation for images in a certain size (e.g., 256x256) 
to images with a different size (e.g., 416x416). The input file must have the LIS 
format as:

```
Path xmin,ymin,xmax,ymax,class_id xmin,ymin,xmax,ymax,class_id
``` 
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import argparse
from os.path import join, dirname, splitext, basename

import filehandler as fh
import progressbar as pbar

def main(inputfile, size_in, size_out):
    """
    Convert annotation from size_in to size_out images.
    """  
    fname, _ = splitext(basename(inputfile))
    foutname = fname+'_'+str(size_out)+'.txt'
    foutput = join(dirname(inputfile), foutname)

    flis = fh.LisFile(inputfile)
    pb = pbar.ProgressBar(flis.nb_lines())
    with flis as flis, open(foutput, 'w') as fout:
        for arr in flis:
            x_out = int((float(flis.x)/size_in) * size_out)
            y_out = int((float(flis.y)/size_in) * size_out)
            w_out = int((float(flis.w)/size_in) * size_out)
            h_out = int((float(flis.h)/size_in) * size_out)
            #86 \t person \t (0,51,49,64) \t 0 \t /home/roger/KSCGR/data1/boild-egg/rgb256/86.jpg
            fout.write('%d\t%s\t(%d,%d,%d,%d)\t%d\t%s\n' % (flis.idfr, flis.obj, x_out, y_out, w_out, h_out, flis.idobj, flis.fname))
            pb.update()
    logger.info('Converted %d lines' % flis.nb_lines())
    logger.info('Saved output file as: %s' % foutput)
                

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('inputfile', metavar='annotated_file', help='Path to the file containing annotations')
    argparser.add_argument('-i', '--input_size', help='Size of the image in original annotation', default=256, type=int)
    argparser.add_argument('-o', '--output_size', help='Size of the image in output annotation', default=480, type=int)
    args = argparser.parse_args()

    main(args.inputfile, args.input_size, args.output_size)

