#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script creates a file containing all paths of the dataset.
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import argparse

import utils

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('inputfolder', metavar='input_folder', help='Path to the folder containing images of the dataset.')
    argparser.add_argument('-o', '--output', help='Path to the file where paths are saved.', default=None)
    args = argparser.parse_args()
    utils.create_pathfile(args.inputfolder, args.output)

