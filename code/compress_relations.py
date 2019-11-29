#!/usr/bin/env python
# coding: utf-8
"""
This script reads a file containing relations as:

Frame \t Subject \t Relation \t Object

and creates a file containing a compressed annotation with the sequence 
of frames for a relation as:

Initial_frame - Final_frame - Id_subject - Id_relation - Id_object

Thus, an example file containing:

0\tperson\tholding\tshell-egg
1\tperson\tholding\tshell-egg
1\tperson\tmoving\tshell-egg
2\tperson\tholding\tshell-egg
2\tperson\tmoving\tshell-egg
3\tperson\tholding\tshell-egg
4\tperson\tholding\tshell-egg
4\tshell-egg\ton\tbowl

generates the following lines:

0-4-1-3-7
1-2-1-4-7
4-4-7-1-17

where objects have the following ids: 1=person, 7=shell-egg, and 17=bowl
and relations have the ids: 1=on, 3=holding, and 4=moving

"""
import sys
import os
import argparse
from os.path import join, dirname, splitext, basename
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import lis
import progressbar
import utils

def load_relations(inputfile):
    dic = {}
    start_frames = []
    with open(inputfile) as fin:
        for i, line in enumerate(fin):
            if line.startswith('Frame'):
                continue # skip header
            idf, sub, rel, obj = line.strip().split()
            idf = int(idf)
            if dic.has_key((sub, rel, obj)):
                if idf == dic[(sub, rel, obj)]['last']+1:
                    dic[(sub, rel, obj)]['last'] += 1
                else:
                    first = dic[(sub, rel, obj)]['first']
                    last = dic[(sub, rel, obj)]['last']
                    dic[(sub, rel, obj)]['contiguous'].append((first, last))
                    dic[(sub, rel, obj)]['first'] = idf
                    dic[(sub, rel, obj)]['last'] = idf
                    start_frames.append((idf, (sub, rel, obj)))
            else:
                dic[(sub, rel, obj)] = {'first':idf, 'last':idf, 'contiguous':[]}
                start_frames.append((idf, (sub, rel, obj)))

        for rel in dic:
            first = dic[rel]['first']
            last = dic[rel]['last']
            dic[rel]['contiguous'].append((first, last))
    logger.info('Found {} relations spread on {} lines of the input file.'.format(len(start_frames), i-1))
    return dic, start_frames
        

def compress_relations(file_input, output=None, class_file='classes.cfg', rels_file='relations.cfg', keep_names=False):
    if not output:
        fname, _ = splitext(basename(file_input))
        output = join(dirname(file_input), fname+'_compressed.txt')

    dcls = utils.load_classes(class_file)
    logger.info('Loaded dictionary with {} objects.'.format(len(dcls)))
    drels = utils.load_classes(rels_file)
    logger.info('Loaded dictionary with {} relations.'.format(len(drels)))
    drels_frames, start_frames = load_relations(file_input)
    logger.info('Compressed to {} lines in output file.'.format(len(start_frames)))

    logger.info('Saving output file...')
    with open(output, 'w') as fout:
        fout.write('Initial_frame - Final_frame - Id_subject - Id_relation - Id_object\n')
        for _, key in sorted(start_frames):
            start, end = drels_frames[key]['contiguous'].pop(0)
            subj, rel, obj = key
            if keep_names:
                fout.write('%d-%d-%s-%s-%s\n' % (start, end, sub, rel, obj))
            else:
                fout.write('%d-%d-%d-%d-%d\n' % (start, end, dcls[subj], drels[rel], dcls[obj]))
    logger.info('File saved at: %s' % output)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_file', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-r', '--relation_file', help='File containing ids and their relations', default='relations.cfg')
    args = parser.parse_args()
    
    compress_relations(args.input, args.output, args.class_file, args.relation_file)
