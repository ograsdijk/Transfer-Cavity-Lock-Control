"""
The file that's initializing the application. It sets up the logger and creates a GUI object.
"""


from .Sweep_GUI import GUI
import logging


logger=logging.getLogger('SWP')
logger.setLevel(logging.DEBUG)

fh=logging.FileHandler('Error_log.log')
fh.setLevel(logging.DEBUG)

formatter=logging.Formatter('\n%(asctime)s - [%(levelname)s] Error caught: %(message)s.')

fh.setFormatter(formatter)

logger.addHandler(fh)


app=GUI()

