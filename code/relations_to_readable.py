#!/usr/bin/env python
# coding: utf-8
"""
Convert a file that contains relations in the form:

Frame	Subject	Relation	Object	Path: data1/boiled-egg/

To a file containing relations in the form:

Initial_frame - Final_frame - Id_subject - Id_relation - Id_object

and creates a file containing a list of these relations without repetition.
"""
import sys
import os
import argparse
from os.path import join, dirname, splitext, basename
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import compress_relations as cr


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_file', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-r', '--relation_file', help='File containing ids and their relations', default='relations.cfg')
    args = parser.parse_args()
    
    cr.compress_relations(args.input, args.output, args.class_file, args.relation_file, True)
