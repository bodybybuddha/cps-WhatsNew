import feedparser
import os
import json
import logging.config

from feedparser import _parse_date as parse_date
from time import mktime
from datetime import datetime, timedelta
from marrow.mailer import Mailer, Message
import jinja2

gConfig = None
gLogger = None
gNewBookTable = None


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
                            filename=__file__ + '.log',
                            format='%(asctime)s : %(levelname)s : %(name)s  : %(message)s')


def getnewbooks(

):
    """Routine to query cps to get the latest books added.
    :rtype: gNewBookTable

    """
    gLogger.info('Getting new books from server')
    d = feedparser.parse('http://'
                         + gConfig['username'] + ':'
                         + gConfig['password'] + '@'
                         + gConfig['serveraddress'])

    gLogger.info('Name of the feed:' + d.feed.title)
    gLogger.info('Looking for books uploaded in the last: ' + str(gConfig['numofdaysfornotification']) + ' days.')

    recentbooks = []

    if d.status == 200:
        for book in d.entries:
            dt = datetime.fromtimestamp(mktime(parse_date(book.updated)))
            if datetime.now() - dt < timedelta(days=int(gConfig['numofdaysfornotification'])):
                if 'title' in book:
                    gLogger.info('Found book. Title: ' + book.title)
                else:
                    gLogger.info('Found book. Strange, no Title field!')

                # add newly added book to array for use later
                recentbooks.append(book)

        return recentbooks

    else:
        gLogger.error('Error getting opds feed! - Please check config. Status Code: ' + str(d.status))


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
    except:
        gLogger.exception('Error getting config file: config.json opened.')


def buildnewsletter(
            book_list

):
    """Routine to send an HTML newsletter


    """
    gLogger.info('Pulling together the newsletter.')

    mailer = Mailer(dict(
            transport=dict(
                use='smtp',
                host=gConfig['SMTPSettings']['host'],
                port=gConfig['SMTPSettings']['port'],
                username=gConfig['SMTPSettings']['user'],
                password=gConfig['SMTPSettings']['password'],
                tls=gConfig['SMTPSettings']['startttls']
            )
        )
    )

    try:
        cd = os.path.dirname(os.path.abspath(__file__))

        # Perform jinja

        jinjaenv = jinja2.Environment(
            loader=jinja2.FileSystemLoader(cd)
        )

        messagebody = jinjaenv.get_template(gConfig['TEMPLATE_FILE']).render(
            book_list=book_list
        )

        mailer.start()

        for winner in gConfig['DistributionList']:

            message = Message(author=gConfig['SMTPSettings']['user'], to=winner['addr'])
            message.subject = gConfig['SMTPSettings']['subject']
            message.plain = "This is only exciting if you use an HTML capable email client. Please disregard."
            message.rich = messagebody

            mailer.send(message)
    except:
        gLogger.exception('Error sending email.')

    mailer.stop()

    gLogger.info('Completed newsletter routine.')

    return


def main():
    global gLogger
    global gNewBookTable

    setup_logging()

    gLogger = logging.getLogger(__name__)

    gLogger.info('Starting script.')

    getconfig()

    if gConfig:
        gNewBookTable = getnewbooks()

        if gNewBookTable:
            gLogger.info("We found " + str(len(gNewBookTable)) + ' new books.')
            buildnewsletter(gNewBookTable)
        else:
            gLogger.info("We didn't find any books.")

    gLogger.info('Finishing script.')


if __name__ == "__main__":
    main()
