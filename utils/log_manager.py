import logging
import time
import os

def init_logs(path):
    logsLocation = path
    if not os.path.exists(logsLocation):
        os.mkdir(logsLocation)
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=path + time.strftime("%Y-%m-%d-%H%M%S") + '.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger

def exception(e, logger):
    logger.error(str(repr(e)))
    logger.exception(e)

def log(str, logger):
    logger.info(str)