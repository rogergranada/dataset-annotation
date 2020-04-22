#!/usr/bin/env python
# coding: utf-8
"""
This script calculates the Cohen's Kappa [1] agreement between two annotators. 
Both input files must have LIS annotation corresponding to the same video, 
i.e., the same number of frames. 

[1] Cohen, Jacob. A Coefficient of Agreement for Nominal Scales. 
    Educational and Psychological Measurement, 20(1), pp. 37-46,
    https://doi.org/10.1177/001316446002000104, 1960.
"""
import sys
import os
import argparse
from os.path import join, dirname
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from sklearn.metrics import cohen_kappa_score
from scipy.spatial.distance import cosine, euclidean

import filehandler as fh
import progressbar as pbar

def intersection(list1, list2):
    unique1 = []
    unique2 = list2[:]
    intersect = []
    for el in list1:
        if el in unique2:
            id = unique2.index(el)
            del(unique2[id])
            intersect.append(el)
        else:
            unique1.append(el)
    return unique1, unique2, intersect


def align_lists(list1, list2):
    """ Align objects of both lists.

        E.g. input: 
        list_A = ['A', 'B', 'C']
        list_B = ['B', 'C', 'D']
        output:
        list_A = ['A', 'B', 'C', 'None']
        list_B = ['B', 'C', 'None', 'D']
    """
    unique1 = []
    unique2 = list2[:]
    intersect = []
    for el in list1:
        if el in unique2:
            id = unique2.index(el)
            del(unique2[id])
            intersect.append(el)
        else:
            unique1.append(el)
    # align 
    list1 = intersect[:]
    list2 = intersect[:]
    for u1 in unique1:
        list1.append(u1)
        list2.append(0)
    for u2 in unique2:
        list1.append(0)
        list2.append(u2)
    return list1, list2


def stats_of_agreement(lis_1, lis_2):
    """ Show some stats about the agreement """
    annotator1 = []
    annotator2 = []
    both_annotators = []
    with fh.LisFile(lis_1) as flis1, \
         fh.LisFile(lis_2) as flis2:
    
        if flis1.nb_frames() != flis2.nb_frames():
            logger.error('Files do not contain the same number of frames.')
        else:
            for frame_objs1, frame_objs2 in zip(flis1.objects_in_frame(ids=True), flis2.objects_in_frame(ids=True)):
                idfr, objs1 = frame_objs1
                idfr, objs2 = frame_objs2
                objs1, objs2, both = intersection(objs1, objs2)
                annotator1.extend(objs1)
                annotator2.extend(objs2)
                both_annotators.extend(both)
    print('Only annotator 1:', len(annotator1))
    print('Only annotator 2:', len(annotator2))
    print('Both annotators :', len(both_annotators))
    print('Total annotation:', len(annotator1) + len(annotator2) + len(both_annotators))


def cohens_kappa(lis_1, lis_2):
    """ Calculate the Cohen's Kappa agreement """
    annotator1 = []
    annotator2 = []
    with fh.LisFile(lis_1) as flis1, \
         fh.LisFile(lis_2) as flis2:
    
        if flis1.nb_frames() != flis2.nb_frames():
            logger.error('Files do not contain the same number of frames.')
        else:
            for frame_objs1, frame_objs2 in zip(flis1.objects_in_frame(ids=True), flis2.objects_in_frame(ids=True)):
                idfr, objs1 = frame_objs1
                idfr, objs2 = frame_objs2
                objs1, objs2 = align_lists(objs1, objs2)
                annotator1.extend(objs1)
                annotator2.extend(objs2)
    kappa = cohen_kappa_score(annotator1, annotator2)
    print(kappa)


def check_correct(objects_1, objects_2):
    objects_1 = sorted(objects_1)
    objects_2 = sorted(objects_2)
    for id, x, y, w, h in objects_1:
        


def agreement_iou(lis_1, lis_2):
    """ Agreement of bounding boxes considering threshold=0.5 """
    
    with fh.LisFile(lis_1) as flis1, \
         fh.LisFile(lis_2) as flis2:
    
        if flis1.nb_frames() != flis2.nb_frames():
            logger.error('Files do not contain the same number of frames.')
        else:
            for frame_objs1, frame_objs2 \
                in zip(flis1.objects_in_frame(ids=True, pos=True), \
                       flis2.objects_in_frame(ids=True, pos=True)):
                idfr, objs1 = frame_objs1
                idfr, objs2 = frame_objs2
                #cos = cosine(objs1[0], objs2[0])
                check_correct(objs1, objs2)
                #for i in objs2:
                #    print(objs1[0], i, euclidean(objs1[0], i))
                break 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('annotator_1', metavar='lis_annotator_1', help='LIS annotation file 1.')
    parser.add_argument('annotator_2', metavar='lis_annotator_2', help='LIS annotation file 2.')
    parser.add_argument('-c', '--cohen', help='Choose Cohen Kappa agreement', default=None)
    parser.add_argument('-s', '--stats', help='Check stats of the agreement', default=None)
    parser.add_argument('-i', '--iou', help='Agreement using IoU agreement', default=None)
    args = parser.parse_args()
    
    #cohens_kappa(args.annotator_1, args.annotator_2)
    #stats_of_agreement(args.annotator_1, args.annotator_2)
    agreement_iou(args.annotator_1, args.annotator_2)
