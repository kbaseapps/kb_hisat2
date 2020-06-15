import os
import logging


def init_logger(scratch, level='DEBUG'):
    log_path = os.path.join(scratch, 'kb_hisat2.log')
    logger = logging.getLogger('kb_hisat2')
    logger.setLevel(level)
    fh = logging.FileHandler(log_path)
    fh.setLevel(level)
    logger.addHandler(fh)
    return logger
