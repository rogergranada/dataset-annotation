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
#from sklearn.metrics import cohen_kappa_score
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


def intersection_over_union(bbox1, bbox2):
    """ Compute the intersection over union of two bounding boxes """
    xA = max(bbox1[0], bbox2[0])
    yA = max(bbox1[1], bbox2[1])
    xB = min(bbox1[2], bbox2[2])
    yB = min(bbox1[3], bbox2[3])
 
    intersection_area = (xB - xA + 1) * (yB - yA + 1)
    bbox1_area = (bbox1[2] - bbox1[0] + 1) * (bbox1[3] - bbox1[1] + 1)
    bbox2_area = (bbox2[2] - bbox2[0] + 1) * (bbox2[3] - bbox2[1] + 1)
    iou = intersection_area / float(bbox1_area + bbox2_area - intersection_area)
    return iou


def add_to_dic(list_objs):
    """ Convert a list to a dict with the first element as a key """
    dic = {}
    for id, x, y, w, h in list_objs:
        if dic.has_key(id):
            dic[id].append((x, y, w, h))
        else:
            dic[id] = [(x, y, w, h)]
    return dic


def single_pair(objref, list_objs, first_ref=True):
    """ Align a pair with another in a list.
        E.g. 
        Input:
            A = [(0,0,0)]
            B = [(1,2,3), (0,0,0)]
        Output:
            ((0,0,0), (0,0,0))
    """
    min_eu = float('inf')
    for obj in list_objs:
        eu = euclidean(obj, objref)
        if eu < min_eu:
            min_eu = eu
            similar = obj
    if first_ref:
        return (objref, similar)
    return (similar, objref)


def multiple_pairs(objs1, objs2, first_ref=True):
    """ Align multiple pairs in both `objs1` and `objs2`
        E.g. 
        Input:
            A = [(0,0,0), (1,2,3)]
            B = [(1,2,3), (0,0,0)]
        Output:
            (((0,0,0), (0,0,0)), ((1,2,3),(1,2,3)))
    """
    pairs = []
    for obj1 in objs1:
        pair = single_pair(obj1, objs2, first_ref=first_ref)
        pairs.append(pair)
    return pairs

"""
def align_objects(objs1, objs2):
    size1 = len(objs1)
    size2 = len(objs2)
    if size1 > 1:
        if size2 > 1:
            if size2 >= size1:
                print 'multiple 1:', objs1, objs2, '::',
                pairs = multiple_pairs(objs1, objs2, first_ref=True)
                print pairs
            else:
                print 'multiple 2:', objs2, objs1, '::',
                pairs = multiple_pairs(objs2, objs1, first_ref=False)
                print pairs
        else:
            print 'single 1:', objs2, objs1, '::',
            pairs = [single_pair(objs2[0], objs1, first_ref=False)]
            print pairs
    else:
        if size2 > 1:
            print 'single 2:', objs1, objs2, '::',
            pairs = [single_pair(objs1[0], objs2, first_ref=True)]
            print pairs
        else:
            print '1 to 1:', objs1, objs2, '::',
            pairs = [(objs1[0], objs2[0])]
            print pairs
    print 
    return pairs
"""

def align_objects(objects_1, objects_2):
    """ From a list containing bounding boxes, join the boxes that 
        belong to the same object. In case of multiples instances of 
        the same object, align the objects that are close to each other.

        Output:
            dic: {'label_1': [((x1, y1, w1, h1), (x2, y2, w2, h2))],
                  'label_2': [((x1, y1, w1, h1), (x2, y2, w2, h2))],
                  ...
            }
    """
    objects_1 = add_to_dic(objects_1)
    objects_2 = add_to_dic(objects_2)
    dobjs = {}
    _, _, both = intersection(objects_1.keys(), objects_2.keys())
    for i in both:
        #aligned = pair_objects(objects_1[i], objects_2[i])
        #dobjs[i] = aligned
        objs1 = objects_1[i]
        objs2 = objects_2[i]
        size1 = len(objs1)
        size2 = len(objs2)
        if size1 > 1:
            if size2 > 1:
                if size2 >= size1:
                    pairs = multiple_pairs(objs1, objs2, first_ref=True)
                else:
                    pairs = multiple_pairs(objs2, objs1, first_ref=False)
            else:
                pairs = [single_pair(objs2[0], objs1, first_ref=False)]
        else:
            if size2 > 1:
                pairs = [single_pair(objs1[0], objs2, first_ref=True)]
            else:
                pairs = [(objs1[0], objs2[0])]
        dobjs[i] = pairs
    return dobjs

    


def agreement_iou(lis_1, lis_2):
    """ Agreement of bounding boxes considering threshold=0.5 """
    accumulated_iou = 0.0
    nb_objects = 0
    list_iou = []
    
    with fh.LisFile(lis_1) as flis1, \
         fh.LisFile(lis_2) as flis2:
        if flis1.nb_frames() != flis2.nb_frames():
            logger.error('Files do not contain the same number of frames.')
        else:
            pb = pbar.ProgressBar(flis1.nb_frames())
            for frame_objs1, frame_objs2 \
                in zip(flis1.objects_in_frame(ids=True, pos=True), \
                       flis2.objects_in_frame(ids=True, pos=True)):
                idfr, objs1 = frame_objs1
                idfr, objs2 = frame_objs2
                dpairs = align_objects(objs1, objs2)
                for idobj in dpairs:
                    for bbox1, bbox2 in dpairs[idobj]:
                        bbox1 = (bbox1[0], bbox1[1], bbox1[0]+bbox1[2], bbox1[1]+bbox1[3])
                        bbox2 = (bbox2[0], bbox2[1], bbox2[0]+bbox2[2], bbox2[1]+bbox2[3])
                        iou = intersection_over_union(bbox1, bbox2)
                        accumulated_iou += iou
                        nb_objects += 1
                        list_iou.append(round(iou, 2))
                        #print idobj, iou, bbox1, bbox2
                #break 
                pb.update()
    print accumulated_iou
    print nb_objects
    print accumulated_iou / float(nb_objects)
    with open(join(dirname(lis_1), 'iou.txt'), 'w') as fout:
        for value in list_iou:
            fout.write('{}\n'.format(value))
    

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
