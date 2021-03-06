#!/usr/bin/env python
# coding: utf-8
"""
This script first checks whether the sequence of frames is correct for
bouding boxes and relations. Then, for a each relation it checks whether 
exists bounding boxes in the image or not. 
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import sys
import os
import argparse
from os.path import join, dirname, splitext, basename
from collections import defaultdict

import filehandler as fh


def check_error(objects, obj, path):
    """ Check whether there is the object in the image """
    if obj not in objects:
        logger.error('Could not find element in frame: {} [IMAGE: {}]'.format(obj, path))
        return False
    return True


def verify_sequence_frames(inputfile):
    """ Verify whether the sequence of frames is increased by one """
    logger.info('Checking sequence for file: {}'.format(inputfile))
    with open(inputfile) as fin:
        last_fr = 0
        last_id = -1
        for line in fin:
            if not line[0].isdigit(): continue
            fr = int(line.strip().split('\t')[0])
            if fr != last_id and fr != 0:
                if fr != (last_fr + 1):
                    logger.error('Could not find a correct sequence. Uncorrect at frame: {}'.format(last_fr))
                    sys.exit()
                last_fr = fr
            last_id = fr


def load_possible_relations(config_file):
    dic = {}
    with open(config_file) as fin:
        for line in fin:
            sub, rel, obj = line.strip().split()
            dic[(sub, rel, obj)] = ''
    return dic


def sanitize_for_bounding_boxes(file_objects, file_relations, output=None):
    """ Check whether a file of relations is according with the bouding boxes
        described in the `file_objects` file.
    """
    if not output:
        fname, ext = splitext(basename(file_relations))
        output = join(dirname(file_relations), fname+'_sanity'+ext)

    verify_sequence_frames(file_objects)
    verify_sequence_frames(file_relations)

    drels = defaultdict(list)
    # Load groups of relations for frame 
    frls = fh.DecompressedFile(file_relations)
    with frls as frels:
        for arr in frels:
            fr, o1, r, o2 = arr[0], arr[1], arr[2], arr[3]
            pathimg = str(fr)+'.jpg'
            drels[pathimg].append((fr, o1, r, o2))
    logger.info('Loaded relations for {} frames.'.format(len(drels)))

    errors = 0
    filelis = fh.LisFile(file_objects)
    with open(output, 'w') as fout, filelis as flis:
        fout.write('Frame\tSubject\tRelation\tObject\tPath: {}\n'.format(frls.path))
        for pathimg, arr in flis.iterate_frames():
            objects = [bbox[0] for bbox in arr]
            relations = drels[pathimg]
            for fr, o1, r, o2 in relations:
                if check_error(objects, o1, pathimg) and check_error(objects, o2, pathimg):
                    fout.write('{}\t{}\t{}\t{}\n'.format(fr, o1, r, o2))
                else:
                    errors += 1
    if errors:
        logger.info('Finished WITH {} errors!'.format(errors))
    else:
        os.remove(output)
        logger.info('Finished without errors!')


def sanitize_relations(file_relations, config_file):
    """ Check whether a file containing relations is according with the possible relations
        described in the `config_file` file.
    """
    logger.info('Checking file: {}'.format(file_relations))
    verify_sequence_frames(file_relations)
    drels = load_possible_relations(config_file)

    # Load groups of relations for frame
    errors = 0 
    recorded = {}
    frls = fh.DecompressedFile(file_relations)
    with frls as frels:
        for arr in frels:
            fr, o1, r, o2 = arr[0], arr[1], arr[2], arr[3]
            pathimg = str(fr)+'.jpg'
            if not drels.has_key((o1, r, o2)) and not recorded.has_key((o1, r, o2)):
                logger.error('There is not possible relation: [{}, {}, {}]'.format(o1, r, o2))
                recorded[(o1, r, o2)] = ''
                errors += 1

    if errors:
        logger.info('Finished WITH {} errors!'.format(errors))
    else:
        logger.info('Finished without errors!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='file_or_folder', help='File or folder containing decompressed relations annotation')
    parser.add_argument('-b', '--bounding_boxes', help='File containing LIS annotation for objects', default='Bounding_Boxes_Annotation.txt')
    parser.add_argument('-r', '--relations', help='File containing possible relations', default='possible_relations.cfg')
    parser.add_argument('-o', '--output', help='Path to the file to save the new relations.')
    parser.add_argument('-f', '--folder', help='Perform sanitizing of files inside a folder.', action='store_true')
    args = parser.parse_args()

    if args.folder:
        hdobj = fh.FolderHandler(args.input)
        for objpath in hdobj:
            fname = basename(objpath)
            relpath = join(args.input, fname)
            #sanitize(objpath, relpath, args.output)
            sanitize_relations(relpath, args.relations)
    #else:
    #    sanitize(args.objectfile, args.relationfile, args.output)
