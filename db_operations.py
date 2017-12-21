
import logging
import config
import sqlite3

logger = logging.getLogger(__name__)

def get_dl_list(

):
    """
        This routine is to determine if the script is using the
        database or config file for a data source for the DL names

    :return: Array of email addresses
    """
    logger.info('Attempting to get dl list.')

    if config.settings['DLSource'] == 'config':
        logger.info('Config to use config file for DL list')
        logger.debug('Returning config file DistributionList')
        return config.settings['DistributionList']

    logger.info('Config NOT to use config file for DL list - assumption DB')

    conn = sqlite3.connect(config.settings['Database']['cps_db_loc'])

    c = conn.cursor()
    c.execute('ATTACH DATABASE "db_1.sqlite" AS db_1')
    c.execute('SELECT email FROM db_1.users')
    conn.commit()
    c.fetchall()
