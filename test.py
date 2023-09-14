
import sys
from astrology import Stars
import logging

logging.basicConfig(
    filename='test.log',  # Specify the log file name
    level=logging.DEBUG,      # Set the log level (DEBUG for all messages)
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info(sys.PATH)
logging.info(flatlib.PATH_LIB)
logging.info(flatlib.PATH_RES)

bd='2015/03/13'
bt='17:00'
bz='01776'
stars = Stars(bd, bt, bz)

print(stars.p.get('sun'))
logging.info(stars.p.get('sun'))
