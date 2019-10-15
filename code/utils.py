import sys
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from os.path import exists
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
    logger.info('Dictionary containing {} labels'.format(len(dic.keys()))
