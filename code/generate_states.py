#!/usr/bin/env python
# coding: utf-8
"""
This script reads a folder containing Decompressed files and generate a PDDL containing
the domain extracted from each file.

"""
import sys
import os
import argparse
from os.path import join, dirname, splitext, basename, isfile, isdir
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import numpy as np
import filehandler as fh



def XOR(state0, state1):
    """ last_state = state0, current_state = state1 """
    state0 = set(state0)
    state1 = set(state1)
    common = state0.intersection(state1)
    effdel = state0 - state1
    effadd = state1 - state0
    return effadd, effdel

#-----------------------------------------------------------------


class StateRepresentation(object):
    def __init__(self, folder_input):
        self.rel2idx = {} # [(triplet)] = i
        self.idx2rel = {} # [i] = (triplet)
        self.relations = self._extract_relations(folder_input)
        self._build_dictionary()

    def __iter__(self):
        for idx in sorted(self.idx2rel):
            # yield (id, ('sub','rel','obj'))
            yield idx, self.idx2rel[idx]

    def _extract_relations(self, folder_input):
        """ Extract relations (sub, rel, obj) from multiple files. """
        relations = []
        logger.info('Generating dictionary...')
        relfiles = fh.FolderHandler(folder_input)
        for file_input in relfiles:
            with fh.DecompressedFile(file_input) as cf:
                relations.extend(cf.list_relations())
        return relations

    def _build_dictionary(self):
        for i, arr in enumerate(sorted(self.relations)):
            self.rel2idx[arr] = i
            self.idx2rel[i] = arr

    def relations_to_vector(self, relations):
        vector = [0]*len(self.idx2rel)
        for idx, triplet in self:
            if triplet in relations:
                vector[idx] = 1
        return vector

    def __len__(self):
        return len(self.idx2rel)

    def save(self, fname):
        logger.info('Saving state representation at: {}'.format(fname))
        with open(fname, 'w') as fout:
            for idx in self.idx2rel:
                fout.write('{} {}\n'.format(idx, self.idx2rel[idx]))
# End of StateRepresentation

class State(object):
    def __init__(self, srep, relations, as_state=False):
        self.srep = srep
        if as_state:
            self.state = relations
        else:
            self.state = srep.relations_to_vector(relations)

    def __iter__(self):
        for val in self.state:
            yield val

    def __len__(self):
        return len(self.state)

    def __str__(self):
        return 'STATE: {}'.format(self.state)

    def __eq__(self, other):
        return self.state == other.state

    def __ne__(self, other):
        return self.state != other.state

    def __hash__ (self):
        return hash(str(self.state))

    def XORe(self, other):
        """ Perform Effect XOR (XORe), which is a different version
            of XOR, since it applies the following rules:
            
            | A | B | XORe |
            | - | - | ---- |
            | 0 | 0 |   0  |
            | 0 | 1 |   1  |
            | 1 | 0 |  -1  |
            | 1 | 1 |   0  |
            
            Parameters:
            -----------
            newstate: State
                Object representing another state

            Example:
            --------
            >>> curr = State.state = [0,0,1,1]
            >>> news = State.state = [0,1,0,1]
            >>> curr.XORe(news)
                [0,1,-1,0]
        """
        effect = [0]*len(self.state)
        assert len(effect) == len(other), 'Different dimensions'
        for i, arr in enumerate(zip(self, other)):
            cs, os = arr
            if cs == 1 and os == 0:
                effect[i] = -1
            else:
                effect[i] = (cs ^ os)
        return State(self.srep, effect, as_state=True)

    def XNORp(self, other):
        """ Perform Predicate XNOR (XNOR_p), which is a different version
            of XNOR, since it applies the following rules:
            
            | A | B | XORe |
            | - | - | ---- |
            | 0 | 0 |  -1  |
            | 0 | 1 |   0  |
            | 1 | 0 |   0  |
            | 1 | 1 |   1  |
            
            Parameters:
            -----------
            newstate: State
                Object representing another state

            Example:
            --------
            >>> curr = State.state = [0,0,1,1]
            >>> news = State.state = [0,1,0,1]
            >>> curr.XORe(news)
                [-1,0,0,1]
        """
        predicate = [0]*len(self.state)
        assert len(predicate) == len(other), 'Different dimensions'
        for i, arr in enumerate(zip(self, other)):
            cs, os = arr
            if cs == 0 and os == 0:
                predicate[i] = -1
            else:
                predicate[i] = 1-(cs ^ os)
        return State(self.srep, predicate, as_state=True)

    def convert_description(self):
        """ Convert from vector representation to PDDL description
            Use the following conversion configuration:

           -1 : negative description (not(p<id>))
            0 : do not include id in description
            1 : positive description (p<id>)
        """
        desc = ''
        for idx, val in enumerate(self):
            if val == -1:
                desc += '    (not (p{}))\n'.format(idx)
            elif val == 1:
                desc += '    (p{})\n'.format(idx)
        return desc[:-1]
            
# End State class

def XNORp(dprec, srep, convert_null=True):
    """ For each list of states, apply XNORp on it.
        In case of a single vector as precondition, we change the 
        null effect (i.e., 0) to negative effect (i.e., -1) since
        it would be represented as "(not (p<val>))" instead of being
        not included in the preconditions.

        | A | B | XORe |
        | - | - | ---- |
        | 0 | 0 |  -1  |
        | 0 | 1 |   0  |
        | 1 | 0 |   0  |
        | 1 | 1 |   1  |
    """      
    for eff in dprec:
        nb_vecs = len(dprec[eff])
        if nb_vecs == 1:
            prec = dprec[eff][0].state
            if convert_null:
                for i in range(len(prec)):
                    # convert null precondition to negative precondition
                    if prec[i] == 0: 
                        prec[i] = -1
        else:
            prec = list(np.sum(np.array([list(v.state) for v in dprec[eff]]), axis=0))
            for i in range(len(prec)):
                val = prec[i]
                if val == 0:
                    prec[i] = -1
                elif val < nb_vecs:
                    prec[i] = 0
                else:
                    prec[i] = 1 
        dprec[eff] = State(srep, prec[:], as_state=True)



REQUIREMENTS = [':strips', ':negative-preconditions']

def generate_actions(dprec):
    # dprec[effect] = precondition
    actions = {}    
    for idact, effect in enumerate(dprec):
        desc = '  :parameters ()\n'
        desc += '  :precondition (and\n'
        desc += '{}\n  )\n'.format(dprec[effect].convert_description())
        desc += '  :effect (and\n'
        desc += '{}\n  )\n'.format(effect.convert_description())
        actions[idact] = desc
    return actions
        
            
def generate_pddl(srep, dprec, foutput):
    fpddl = fh.AutoPDDLFile('autokitchen')
    [fpddl.add_requirements(req) for req in REQUIREMENTS]
    [fpddl.add_predicates(idpred) for idpred, _ in srep]
    actions = generate_actions(dprec)
    [fpddl.add_action(idact, actions[idact]) for idact in actions]
    fpddl.save_file(foutput)
        

ST0 = [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
ST1 = [0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1]
ST2 = [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1]
ST3 = [0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]

def preconditions_effects(file_input, srep, dprec):
    last_state = []
    current_state = []
    logger.info('Processing file: {}'.format(file_input))
    nb, allf = 0, 0

    with fh.DecompressedFile(file_input) as cf:
        for idfr, relations in cf.iterate_frames():
            #print idfr,  State(srep, relations).state
            if idfr == 0:
                last_state = State(srep, relations)
            else:
                current_state = State(srep, relations)
                if current_state != last_state:
                    effect = last_state.XORe(current_state)
                    if effect in dprec:
                        dprec[effect].append(last_state)
                    else:
                        dprec[effect] = [last_state]
                    nb += 1
                last_state = current_state
    return dprec

def domains_folder(folder_input, output):
    if not output:
        output = folder_input
        output = join(folder_input, 'auto_pddls.tmp')
        output = fh.mkdir_from_file(output)
        fdic = join(output, 'dictionary.dat')
        fpddl = join(output, 'auto_domain.pddl')

    dprec = {}
    srep = StateRepresentation(folder_input)
    logger.info('Dictionary contaning {} relations.'.format(len(srep)))
    relfiles = fh.FolderHandler(folder_input)
    for file_input in relfiles:
        fname, _ = fh.filename(file_input)
        file_output = join(output, fname+'.pddl')
        # get all preconditions and effects before applying XNORp
        preconditions_effects(file_input, srep, dprec)
    XNORp(dprec, srep)
    v= [(v.state, dprec[v].state) for v in dprec]
    generate_pddl(srep, dprec, fpddl)
    srep.save(fdic)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    args = parser.parse_args()

    if isfile(args.input):
        domains_folder(args.input, args.output)
    elif isdir(args.input):
        domains_folder(args.input, args.output)
    
