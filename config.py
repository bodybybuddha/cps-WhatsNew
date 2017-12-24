
import logging
import json
import os
import db_operations


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

        # Since we got the configuration - let's check for the database config setting
        # and do some db operations if needed
        # Allowed values are:  db, config

        if settings['DLSource'] == 'db':

            logger.info('Configured for database')

            if os.path.exists(settings['Database']['cps_db_loc']):
                logger.debug("Found database file at {0}".format(settings['Database']['cps_db_loc']))
                settings['DLSourceExist'] = True
                return True

            else:
                logger.error("Did NOT Find database file at {0}".format(settings['Database']['cps_db_loc']))

                settings['DLSourceExist'] = False
                return False

    except:
        logger.exception('Error getting config file: config.json opened.')
        return False