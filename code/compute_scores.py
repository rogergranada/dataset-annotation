#!/usr/bin/env python
# coding: utf-8
"""
This script compute the acuracy score for each goal.
"""
import sys
import os
import argparse
from os.path import join, dirname, splitext, basename, isfile, isdir
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import numpy as np
import pandas as pd
import filehandler as fh
from matplotlib import pyplot as plt


# RECIPES[<filename>] = <column name in scores file> 
MAP = {'boiledegg': 'hard-boiled_egg',
       'kinshiegg': 'kinshi_egg',
       'hamegg': 'ham_egg',
       'scrambledegg': 'scrambled_egg',
       'omelette': 'omelette'
}


def plot_result(csv_file, name=''):
    """ Return the accuracy of scores according to the true class `name`. 

    Parameters:
    -----------
    csv_file: string
        csv file containing scores from the goal recognizer
    """
    fname = fh.filename(csv_file, extension=False)
    fplot = join(dirname(csv_file), fname+'.png')
    df_full = pd.read_csv(csv_file)
    # remove idfr column
    names = list(df_full.columns)[1:] 
    df = df_full[names]

    dnames = dict([(i, n) for i, n in enumerate(names)])
    dic = dict([(i, []) for i, n in enumerate(names)])
    for i, scores in enumerate(zip(df[names[0]], df[names[1]], df[names[2]], df[names[3]], df[names[4]])):
        winner = np.argwhere(scores == np.amax(scores)).flatten().tolist()
        for idname in dnames:
            if idname in winner:
                dic[idname].append(idname)
            else:
                dic[idname].append(-1)

    plt.figure(figsize=(15,10))
    size = len(dic[0])
    for key in dic:
        plt.scatter(range(size), dic[key])
    plt.ylim(-0.5, 4.5)
    plt.yticks(range(len(names)), names)
    plt.legend(names)
    plt.savefig(fplot)
    #plt.show()


def compute_accuracy(csv_file, name=''):
    """ Return the accuracy of scores according to the true class `name`. 

    Parameters:
    -----------
    csv_file: string
        csv file containing scores from the goal recognizer
    name: string
        name of the file according to the key of the MAP dictionary
    """
    dfull = pd.read_csv(csv_file)
    names = list(dfull.columns)[1:]
    df = dfull[names]

    correct, candidates = 0, 0
    for i, scores in enumerate(zip(df[names[0]], df[names[1]], 
                                   df[names[2]], df[names[3]], df[names[4]])):
        winner = np.argwhere(scores == np.amax(scores)).flatten().tolist()
        candidates += len(winner)
        for w in winner:
            if names[w] == MAP[name]:
                correct += 1
        nb_obs = df[names[0]].size
        acc = float(correct)/nb_obs
        spread = float(candidates)/nb_obs
    return acc, correct, spread, nb_obs


def compute_from_folder(folder_input, output, plot=False):
    """ Receives a folder containing files with scores for each
        goal.

    Parameters:
    -----------
    folder_input: string
        path to the folder containing files with relations
    output: string
        path to the file where the goals are saved.
    """
    if not output:
        output = join(folder_input, 'results.txt')
 
    drecipes = {}
    filescores = fh.FolderHandler(folder_input, ext='csv')
    with open(output, 'w') as fout:
        for file_score in filescores:
            logger.info('Reading file: {}'.format(file_score))
            fname = fh.filename(file_score, extension=False).split('-')[1]
            # fname = boiledegg
            acc, correct, spread, nb_obs = compute_accuracy(file_score, name=fname)
            fout.write('{}: \n\tAccuracy: {}\n\tCorrect: {}\n\tSpread: {}\n\tObservations: {}\n\n'.format(
                fname, acc, correct, spread, nb_obs)
            )
            if plot:
                plot_result(file_score, name=fname)
            
    logger.info('Accuracy scores saved in file: {}'.format(output))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input_folder', help='Plain text file')
    parser.add_argument('-o', '--output', help='Plain text file', default=None)
    parser.add_argument('-p', '--plot', help='Save a plot file', action='store_true')
    args = parser.parse_args()

    if isfile(args.input):
        compute_from_folder(args.input, args.output, args.plot)
    elif isdir(args.input):
        compute_from_folder(args.input, args.output, args.plot)
    
