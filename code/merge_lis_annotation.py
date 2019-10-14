#!/usr/bin/env python
# coding: utf-8
import sys
import os
import argparse
from os.path import join, dirname
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import lis
import progressbar

HOME='/usr/share/datasets/KSCGR/'
DIC_CLASSES = {'person': 0, 'egg': 1, 'beaten egg': 2, 'boiled egg': 3, 'egg crepe': 4,'ham egg': 5, 
               'kinshi egg': 6, 'scramble egg': 7, 'omelette': 8, 'ham': 9, 'pan': 10, 'frying pan': 11, 
               'pan handle': 12, 'pan lid': 13, 'bowl': 14, 'cutting board': 15, 'dishcloth': 16,
               'glass': 17, 'hashi': 18, 'knife': 19, 'milk carton': 20, 'oil bottle': 21, 'plate': 22, 
               'saltshaker': 23, 'spoon': 24, 'turner': 25}

def merge_lis(folder_input, output=None):
    if not output:
        output = join(folder_input, 'files_merged.txt')

    list_files = [files for _, _, files in os.walk(folder_input)]
    list_files = sorted(list_files[0])

    with open(output, 'w') as fout:
        fout.write('Frame:\tLabel:\tPoints:\tBounding Box ID:\tFrame path:\n')
        for i, f in enumerate(list_files, start=1):
            lis_file = join(folder_input, f)
            logger.info('Processing file [%d/%d]: %s' % (i, len(list_files), lis_file))
            fann = lis.LIS(lis_file)
            with fann as flis:
                for arr in flis:
                    obj = flis.obj
                    #0 \t egg \t (58,241,19,16) \t 0 \t data1/boild-egg/0.jpg
                    if flis.obj == 'boild egg':
                        obj = 'boiled egg'
                    elif flis.obj == 'egg crepe ':
                        obj = 'egg crepe'
                    elif flis.obj == 'oil bottle ':
                        obj = 'oil bottle'
                    elif flis.obj == 'pan handler':
                        obj = 'pan handle'
                    elif flis.obj == 'bootle oil':
                        obj = 'pan handle'
                    fout.write('%s\t%s\t%s\t%s\t%s\n' % (flis.idfr, obj, flis.bbox, DIC_CLASSES[obj], join(HOME, flis.path)))
            logger.info('End of processing: %d frames' % flis.idfr)
    logger.info('File saved at: %s' % output)

    
def check_labels(fileinput):
    dic = {}
    fann = lis.LIS(fileinput)
    pb = progressbar.ProgressBar(fann.count_lines())
    with fann as flis:
        for _ in flis:
            dic[flis.obj] = ''
            pb.update()
    print sorted(dic)
    print len(dic.keys()), 'labels'

def check_wrong(inputfile):
    with open(inputfile) as fin:
        for i, l in enumerate(fin):
            if i > 2102810 and i < 2102819:
                print l
            if i > 2102819:
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    args = parser.parse_args()
    
    merge_lis(args.input, output=args.output)
    #check_labels(args.input)
    check_wrong(join(args.input, 'files_merged.txt'))
