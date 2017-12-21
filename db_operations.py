
import logging
import config
import sqlite3

logger = logging.getLogger(__name__)


def create_customdb(

):
    """
    This routine will create the custom database

    :return:
    """
    logger.info("Need to create the custom database.")

    #Do some interesting stuff to create the database!

    #Once the database is created, we need to update all users in it.

    if update_users_customdb():
        logger.info("Finished creating & updating custom database.")
        return True
    else:
        logger.error("Issue with updating the custom database.")
        return False


def update_users_customdb(

):
    """
    This routine will sync up the users in the custom database with the cps database

    :return:
    """
    logger.info("Updating the users in the custom database.")
    return True


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

    conn = sqlite3.connect(config.settings['Database']['extras_db_fn'])

    # c = conn.cursor()
    # c.execute('ATTACH DATABASE "db_1.sqlite" AS db_1')
    # c.execute('SELECT * FROM db_1.my_table')
    # conn.commit()
    # c.fetchall()