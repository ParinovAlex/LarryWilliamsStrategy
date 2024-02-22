import os
import sys
import logging
from logging import StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler

#setup logger
if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler1 = StreamHandler(stream=sys.stdout)
handler1.setFormatter(Formatter(fmt="[%(asctime)s: %(levelname)s] %(message)s"))
logger.addHandler(handler1)

handler2 = TimedRotatingFileHandler("logs/logfile.log", when="midnight", backupCount=10)
handler2.setFormatter(Formatter(fmt="[%(asctime)s: %(levelname)s] %(message)s"))
logger.addHandler(handler2)