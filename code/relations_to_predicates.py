#!/usr/bin/env python
# coding: utf-8
"""
This script reads a uncompressed file containing relations as:

```
Frame \t Subject \t Relation \t Object
```

and the description of `types` of each object to create a file with `predicates` 
for PDDL based on the sequence of relation as:

```
(in ?f - food ?d - dish)
```

Thus, an example file containing:

```
0\tperson\tholding\tshell-egg
1\tperson\tholding\tshell-egg
1\tperson\tmoving\tshell-egg
2\tperson\tholding\tshell-egg
2\tperson\tmoving\tshell-egg
3\tperson\tholding\tshell-egg
4\tperson\tholding\tshell-egg
4\tshell-egg\ton\tbowl
```

and types as:

```
person - subject
shell-egg - egg
bowl - dish
```

generates the following lines:

```
(:predicates
  (holding subject egg)
  (moving subject egg)
  (on egg dish)
)
```
"""
import sys
import os
import argparse
from os.path import join, dirname, splitext, basename
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import filehandler as fh


def compress_relations(file_input, output=None, file_types='types.pddl', class_file='classes.cfg', rels_file='relations.cfg', keep_names=False):
    if not output:
        fname, _ = splitext(basename(file_input))
        output = join(dirname(file_input), fname+'_predicates.txt')

    # Load classes for objects from dict {0: 'rel0', 1: 'rel1'}
    do = fh.ConfigFile(class_file).load_classes(cnames=True)
    logger.info('Loaded dictionary with {} objects.'.format(len(do)))
    dr = fh.ConfigFile(rels_file).load_classes(cnames=True)
    logger.info('Loaded dictionary with {} relations.'.format(len(dr)))
    dp = fh.PddlTypes(file_types)

    df = fh.DecompressedFile(file_input)
    rels = df.list_relations()

    relations = []
    for s, r, o in rels:
        s = s.replace('_', '-')
        o = o.replace('_', '-')
        relations.append((r, dp[s], dp[o]))
        relations.append((r, (s, dp[s][1]), (o, dp[o][1])))

    with open(output, 'w') as fout:
        fout.write('(:predicates\n')
        for r, s, o in sorted(set(relations)):
            # (on ?f - food ?o - object)
            fout.write('    (%s ?%s - %s ?%s - %s)\n' % (r, s[1], s[0], o[1], o[0]))
        fout.write(')')
    logger.info('File saved at: %s' % output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_file', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-t', '--types_file', help='File containing PDDL types', default='types.pddl')
    parser.add_argument('-c', '--class_file', help='File containing ids and their classes', default='classes.cfg')
    parser.add_argument('-r', '--relation_file', help='File containing ids and their relations', default='relations.cfg')
    parser.add_argument('-n', '--store_names', help='Save names for objects and relations instead of their ids.', action='store_true')
    args = parser.parse_args()
    
    compress_relations(args.input, args.output, args.types_file, args.class_file, args.relation_file, args.store_names)
