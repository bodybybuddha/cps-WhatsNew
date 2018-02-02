
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

    try:
        logger.info('Config to use database for DL list')
        conn = sqlite3.connect(config.settings['Database']['cps_db_loc'])

        c = conn.cursor()
        c.execute('SELECT email FROM user order by id')
        all_emails = c.fetchall()
        conn.close()

        exclusion_list = config.settings['DistributionExclusionsList']

        final_email_list = [x[0] for x in all_emails if x[0] not in exclusion_list]

        logger.info('Returning list of emails from db.')

        return final_email_list

    except:
        logger.exception('Issue with getting information from database')
        return False


