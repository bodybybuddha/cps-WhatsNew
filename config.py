
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

            if os.path.exists(settings['Database']['extras_db_fn']):
                logger.debug("Found database file at {0}".format(settings['Database']['extras_db_fn']))
                settings['DLSourceExist'] = True

                #Database is there, need to make all of the users are updated
                if db_operations.update_users_customdb():
                    logger.info("Returning from updating database.")
                    return True
                else:
                    return False

            else:
                logger.error("Did NOT Find database file at {0}".format(settings['Database']['extras_db_fn']))

                settings['DLSourceExist'] = False

                #Database isn't there, so we need to create it and then load it up
                if db_operations.create_customdb():
                    logger.info("Custom database created.")
                    return True
                else:
                    return False

    except:
        logger.exception('Error getting config file: config.json opened.')
        return False