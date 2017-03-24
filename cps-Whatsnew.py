import feedparser
import os
import json
import logging.config
from feedparser import _parse_date as parse_date
from time import mktime
from datetime import datetime, timedelta

gConfig = None
gLogger = None

# modify this to change the Template Directory
TEMPLATE_DIR = '/templates/'
COVER_DIR = '/covers/'


def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level,
                            filename=__file__+'.log',
                            format='%(asctime)s : %(levelname)s : %(name)s  : %(message)s')


def getnewbooks(

):
    """Routine to query cps to get the latest books added.

    """
    gLogger.info('Getting new books from server')
    d = feedparser.parse('http://'
                         + gConfig['username'] + ':'
                         + gConfig['password'] + '@'
                         + gConfig['serveraddress'])

    gLogger.info('Name of the feed:' + d.feed.title)

    for book in d.entries:
        dt = datetime.fromtimestamp(mktime(parse_date(book.updated)))
        if datetime.now() - dt < timedelta(days=int(gConfig['numofdaysfornotification'])):
            if 'title' in book:
                print 'Title: ' + book.title
            if 'authors' in book:
                print 'Author(s): ' + book.author
            if 'summary' in book:
                print book.summary
            else:
                print 'No Summary'


def getconfig(

):
    """Routine pull in the config file

     """
    global gConfig
    gLogger.info('Attempting to get config file.')

    try:
        with open('config.json', 'r') as f:
            gConfig = json.load(f)
            gLogger.info('Opened config file: config.json.')
    except :
        gLogger.exception('Error getting config file: config.json opened.')


def main():
    global gLogger
    setup_logging()

    gLogger = logging.getLogger(__name__)

    gLogger.info('Starting script.')

    getconfig()

    if gConfig:
        getnewbooks()

    gLogger.info('Finishing script.')

if __name__ == "__main__":
    main()



