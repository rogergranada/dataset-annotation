import sys
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import os
from os.path import exists, join, splitext, basename
import lis
import progressbar

def load_classes(cfg_file, mode=None, inv=False, no_background=False):
    """ Load classes from configuration file """
    if not exists(cfg_file):
        logger.error('File {} does not exist!'.format(cfg_file))
        sys.exit(0)

    dclass = {}
    with open(cfg_file) as fin:
        for line in fin:
            arr = line.strip().split()
            if inv:
                if no_background:
                    if arr[1] == '__background__': continue
                    dclass[int(arr[0])-1] = arr[1]
                else:
                    dclass[int(arr[0])] = arr[1]
            else:
                if no_background:
                    if arr[1] == '__background__': continue
                    dclass[arr[1]] = int(arr[0])-1
                else:
                    dclass[arr[1]] = int(arr[0])
            
    if mode == 'set':
        return set(dclass.keys())
    return dclass


def check_labels(fileinput):
    dic = {}
    fann = lis.LIS(fileinput)
    pb = progressbar.ProgressBar(fann.count_lines())
    with fann as flis:
        for _ in flis:
            dic[flis.obj] = ''
            pb.update()
    logger.info('{}'.format(sorted(dic)))
    logger.info('Dictionary containing {} labels'.format(len(dic.keys())))


def create_pathfile_for_KSCGR(root_folder, output=None):
    """ Receive the ROOT folder of KSCGR dataset to create
        a `paths.txt` file containing all paths to images """
    if not output:
        output = join(root_folder, 'paths.txt')

    with open(output, 'w') as fout:
        nb_files = 0
        for folder, _, files in sorted(os.walk(root_folder)):
            if folder == root_folder: continue
            dnames = {}
            logger.info('Processing folder: %s' % folder)
            for f in sorted(files):
                idf = int(splitext(f)[0])
                dnames[idf] = f
            for idf in sorted(dnames):
                fout.write('%s\n' % join(folder, dnames[idf]))
                nb_files += 1
    logger.info('Create file containing %d paths' % nb_files)
    logger.info('File saved at: %s' % output)


def create_pathfile(inputfolder, output, path=None):
    """ Create a file containing all images from input folder """
    if not output:
        output = join(inputfolder, 'paths.txt')

    logger.info('Processing folder: %s' % inputfolder)
    with open(output, 'w') as fout:
        files = os.listdir(inputfolder)
        names = []
        for img in files:
            name, ext = splitext(basename(img))
            if ext == '.jpg':
                names.append(int(name))
        logger.info('Saving %d files in %s' % (len(names), output))
        for name in sorted(names):
            if path:
                fout.write('%s\n' % join(path, str(name)+'.jpg'))
            else:
                fout.write('%s\n' % join(inputfolder, str(name)+'.jpg'))
        logger.info('Process finished!')


def images_from_file(inputfile, extension=False):
    """ From a file containing bounding boxes (``), extract
        the name of the files and return as a list.
    """
    vnames = []
    fann = lis.LIS(inputfile)
    nb_items = fann.count_lines()
    pb = progressbar.ProgressBar(nb_items)
    with fann as flis:
        for _ in flis:
            if fann.obj != 'None':
                path = basename(fann.fname)
                if not extension:
                    path, _ = splitext(path)
                pb.update()
                vnames.append(path)
    logger.info('Loaded %d paths.' % nb_items)
    return vnames                
