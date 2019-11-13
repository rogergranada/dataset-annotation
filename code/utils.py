import sys
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from os.path import exists, join
import lis
import progressbar

def load_classes(cfg_file, mode='set'):
    """ Load classes from configuration file """
    if not exists(cfg_file):
        logger.error('File {} does not exist!'.format(cfg_file))
        sys.exit(0)

    dclass = {}
    with open(cfg_file) as fin:
        for line in fin:
            arr = line.strip().split()
            dclass[arr[1]] = arr[0]
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


def create_pathfile(root_folder, output=None):
    """ Receive the ROOT folder of KSCGR dataset to create
        a `paths.txt` file containing all paths to images """
    if not output:
        output = join(root_folder, 'paths.txt')

    with open(output, 'w') as fout:
        nb_files = 0
        for folder, _, files in os.walk(root_folder):
            for f in files:
                fout.write('%s\n' % join(folder, f))
                nb_files += 1
    logger.info('Create file containing %d paths' % nb_files)
    logger.info('File saved at: %s' % output)
