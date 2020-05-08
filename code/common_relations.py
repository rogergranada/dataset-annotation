#!/usr/bin/env python
# coding: utf-8
"""
This script reads a folder containing files with relations as:

```
Frame \t Subject \t Relation \t Object
```

and generates the list of relations that appear in all files:

```
# Common Relations

Subject_1 Relation_1 Object_1
Subject_2 Relation_2 Object_2
...

# Not common Relations

#id-files file Subject_3 Relation_3 Object_3
"""
import sys
import os
import argparse
from os.path import join, dirname, splitext, basename
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import filehandler as fh


def check_common_relations(folder_input, output=None, file_types='types.pddl', class_file='classes.cfg', rels_file='relations.cfg', keep_names=False):
    if not output:
        output = join(dirname(folder_input), 'common_relations.txt')

    fdh = fh.FolderHandler(folder_input)
    dic = {}
    for file_input in fdh:
        with fh.CompressedFile(file_input) as cf:
            relations = []
            fname, _ = splitext(basename(file_input))
            for start, end, sub, rel, obj in cf:
                relations.append((sub, rel, obj))
            relations = set(relations)
            for rels in relations:
                if dic.has_key(rels):
                    dic[rels].append(fname)
                else:
                    dic[rels] = [fname]

    dtimes = {}
    for rel in dic:
        size = len(dic[rel])
        if dtimes.has_key(size):
            dtimes[size].append(rel)
        else:
            dtimes[size] = [rel] 

    with open(output, 'w') as fout:
        for size in sorted(dtimes, reverse=True):
            fout.write('# {} recipes\n'.format(size))
            for sub, rel, obj in dtimes[size]:
                fout.write('{} {} {}\n'.format(sub, rel, obj))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-t', '--types_file', help='File containing PDDL types', default='types.pddl')
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-r', '--relation_file', help='File containing ids and their relations', default='relations.cfg')
    parser.add_argument('-n', '--store_names', help='Save names for objects and relations instead of their ids.', action='store_true')
    args = parser.parse_args()
    
    check_common_relations(args.input, args.output, args.types_file, args.class_file, args.relation_file, args.store_names)
