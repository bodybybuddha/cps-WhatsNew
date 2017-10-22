
import logging
import json

logger = logging.getLogger(__name__)
settings = None


def get_config(

):
    """Routine pull in the config file

     """
    global settings
    logger.info('Attempting to get config file.')

    try:
        with open('config.json', 'r') as f:
            settings = json.load(f)
            logger.info('Opened config file: config.json.')
    except:
        logger.exception('Error getting config file: config.json opened.')
