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
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from sklearn.metrics import cohen_kappa_score
from scipy.spatial.distance import cosine, euclidean
from collections import defaultdict
from matplotlib import pyplot as plt
from os.path import join, dirname, basename
import numpy as np

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
    """ Show some stats about the Cohen Kappa agreement 
        It considers the intersection of objects between 
        annotators."""
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
    """ Generate the IoU score for each pair of bounding box.

        Output: list containing (id_frame, id_object, iou)
    """
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
                # get correspondence between bounding boxes
                dpairs = align_objects(objs1, objs2)
                for idobj in dpairs:
                    for bbox1, bbox2 in dpairs[idobj]:
                        bbox1 = (bbox1[0], bbox1[1], bbox1[0]+bbox1[2], bbox1[1]+bbox1[3])
                        bbox2 = (bbox2[0], bbox2[1], bbox2[0]+bbox2[2], bbox2[1]+bbox2[3])
                        iou = intersection_over_union(bbox1, bbox2)
                        # (id_frame, id_object, iou)
                        list_iou.append((idfr, idobj, round(iou, 2)))
                pb.update()
    return list_iou


def stats_iou(lis_1, lis_2, output=None, classes='classes.cfg'):
    """ Check statistics for IoU objects. """
    if not output:
        output = dirname(lis_1)

    dclasses = fh.ConfigFile(classes).load_classes()

    accumulated_iou = 0.0
    nb_objects = 0
    dic_obj = defaultdict(list)
    all_iou = []

    # create dictionary with iou for each object
    list_iou = agreement_iou(lis_1, lis_2)
    for _, idobj, iou in list_iou:
        dic_obj[idobj].append(iou)
        accumulated_iou += iou
        all_iou.append(iou)
        nb_objects += 1

    # convert to numpy arrays
    for idobj in dic_obj:
        dic_obj[idobj] = np.array(dic_obj[idobj])
    all_iou = np.array(all_iou)
    
    # plot distribution for all iou
    plt.hist(all_iou, bins=100)
    plt.axis(xmin=0, xmax=1.0)
    plt.title('Distribution of IoU for all objects')
    plt.xlabel('IoU scores')
    plt.ylabel('Number of instances')
    plt.savefig(join(output, 'iou_all.svg'))
    plt.clf()

    # plot distribution for each object
    for idobj in dic_obj:
        iou_obj = dic_obj[idobj]
        plt.hist(iou_obj, bins=100)
        plt.axis(xmin=0, xmax=1.0)
        plt.title('Distribution of IoU for {}'.format(dclasses[idobj]))
        plt.xlabel('IoU scores')
        plt.ylabel('Number of instances')
        plt.savefig(join(output, 'iou_'+dclasses[idobj]+'.svg'))
        plt.clf()

    # save stats of IoU in a file
    with open(join(output,'stats_iou.txt'), 'w') as fout:
        fout.write('Statistics for intersection over union - IoU\n')
        fout.write('============================================\n')
        fout.write('Input file 1: {}\n'.format(basename(lis_1)))
        fout.write('Input file 2: {}\n\n'.format(basename(lis_2)))

        fout.write('Statistics for Objects\n')
        fout.write('----------------------\n')
        fout.write('Total number of object: {}\n'.format(len(all_iou)))
        for idobj in dic_obj:
            fout.write('Object {}: {}\n'.format(dclasses[idobj], len(dic_obj[idobj])))
        fout.write('\n')
        
        fout.write('General Intersection over Union (IoU)\n')
        fout.write('-------------------------------------\n')
        fout.write('Mean Iou: {}\n'.format(np.mean(all_iou)))
        fout.write('Std Iou: {}\n'.format(np.std(all_iou)))
        fout.write('\n')
        
        agree_05 = all_iou[all_iou>=0.5]
        agree_07 = all_iou[all_iou>=0.7]
        fout.write('Correct bboxes IoU>=0.5: {}\n'.format(len(agree_05)))
        fout.write('Ratio correct bboxes IoU>=0.5: {}\n'.format(len(agree_05)/float(len(all_iou))))
        fout.write('Correct bboxes IoU>=0.7: {}\n'.format(len(agree_07)))
        fout.write('Ratio correct bboxes IoU>=0.7: {}\n\n'.format(len(agree_07)/float(len(all_iou))))

        fout.write('Intersection over Union (IoU) for objects\n')
        fout.write('-----------------------------------------\n')
        for idobj in dic_obj:
            obj_iou = dic_obj[idobj]
            agree_05 = obj_iou[obj_iou>=0.5]
            agree_07 = obj_iou[obj_iou>=0.7]
            fout.write('Object {}:\n'.format(dclasses[idobj]))
            fout.write('- Correct bboxes IoU>=0.5: {}\n'.format(len(agree_05)))
            fout.write('- Ratio correct bboxes IoU>=0.5: {}\n'.format(len(agree_05)/float(len(obj_iou))))
            fout.write('- Correct bboxes IoU>=0.7: {}\n'.format(len(agree_07)))
            fout.write('- Ratio correct bboxes IoU>=0.7: {}\n'.format(len(agree_07)/float(len(obj_iou))))


def convert_list(dic, vec):
    for i in range(len(vec)):
        triplet = vec[i]
        if triplet in dic:
            vec[i] = dic[triplet]
        else:
            dic[triplet] = str(len(dic))
            vec[i] = dic[triplet]

def cohen_kappa_relations(fanno_1, fanno_2):
    dic = {}
    annotator1 = []
    annotator2 = []
    fd1 = fh.DecompressedFile(fanno_1)
    fd2 = fh.DecompressedFile(fanno_2)
    for arr1, arr2 in zip(fd1.iterate_frames(), fd2.iterate_frames()):
        idf1, vec1 = arr1
        idf2, vec2 = arr2
        convert_list(dic, vec1)
        convert_list(dic, vec2)
        if idf1 != idf2: 
            logger.error('Files do not contain the same sequence of frames: {}/{}'.format(idf1, idf2))
            sys.exit()
        v1, v2 = align_lists(vec1, vec2)
        annotator1.extend(v1)
        annotator2.extend(v2)
    kappa = cohen_kappa_score(annotator1, annotator2)
    print(kappa)
    print('Finished')


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
    #stats_iou(args.annotator_1, args.annotator_2)
    cohen_kappa_relations(args.annotator_1, args.annotator_2)
