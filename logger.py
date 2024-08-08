import logging
import os

def setup(name, fileName=None, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 로그 포맷 설정
    logName = fileName
    #log_format = '[%(asctime)s][%(levelname)s] %(message)s'
    log_format = '%(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, datefmt=date_format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # file_handler = TimedRotatingFileHandler('/var/log/{}'.format(logName),
    #                                         when='midnight',
    #                                         interval=1,
    #                                         backupCount=7)
    # file_handler.suffix = "%Y%m%d"
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    return logger

logger = setup(
    name='tickets',
    level=logging.DEBUG if not 'LOG_LEVEL' in os.environ else os.environ['LOG_LEVEL'])
