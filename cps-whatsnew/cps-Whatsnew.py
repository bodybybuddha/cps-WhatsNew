
import logging
import logging.config
import feedparser
import json
import os
import urllib2
import base64
import cStringIO
from PIL import Image

from feedparser import _parse_date as parse_date
from time import mktime
from datetime import datetime, timedelta
from marrow.mailer import Mailer, Message
import jinja2

import config
import db_operations

logger = None


def setup_logging(
        default_path='../custom/logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration

        attempt to find the logging config file: logging.json
        if one can't be found, basic configuration is used

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            logging_config = json.load(f)
        logging.config.dictConfig(logging_config)
    else:
        logging.basicConfig(level=default_level,
                            filename=__file__ + '.log',
                            format='%(asctime)s : %(levelname)s : %(name)s  : %(message)s')


def get_thumbnail(
        book_cover_url
):
    """Routine to create a thumbnail from a URL that serves up a jpeg
        Not build a ton of catches in here, just assuming the above!
    """

    logger.debug("Building cover for: %s ", book_cover_url)

    size = 300, 300

    try:

        request = urllib2.Request(book_cover_url)
        base64string = base64.encodestring('%s:%s' % (config.settings['username'], config.settings['password'])).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        cover_file = cStringIO.StringIO(urllib2.urlopen(request).read())

        img = Image.open(cover_file)

        img.thumbnail(size, Image.ANTIALIAS)
        return img

    except:
        logger.debug("Couldn't get a cover thumbnail created.")
        return "no data"


def getnewbooks(

):

    """Routine to query cps to get the latest books added. return array of new books

    """
    logger.info('Getting new books from server')
    d = feedparser.parse('http://'
                         + config.settings['username'] + ':'
                         + config.settings['password'] + '@'
                         + config.settings['serveraddress'])

    if d.bozo == 1:
        logger.error('Username, password, or Server Address url is incorrect.')
        return False
    else:
        logger.info('Name of the feed:' + d.feed.title)
        logger.info('Looking for books uploaded in the last: ' + str(config.settings['numofdaysfornotification']) + ' days.')

    _thumbnail_uri = u'http://opds-spec.org/image/thumbnail'
    recent_books = []

    if d.status == 200:
        for book in d.entries:
            dt = datetime.fromtimestamp(mktime(parse_date(book.updated)))
            if datetime.now() - dt < timedelta(days=int(config.settings['numofdaysfornotification'])):
                if 'title' in book:
                    logger.info('Found book. Title: ' + book.title)
                else:
                    logger.info('Found book. Strange, no Title field!')

                # Need to get a uniqueID for naming the CIDs in the html newsletter - pulling the GUID from the link url
                # While we are here, might as well find out if the book has a cover
                #  if the book has a cover set:
                #        the book_cover_id to the GUID
                #        pull the url to make it easier to get to
                #        go get the cover and resize it
                #  if the book doesn't have a cover, set book_cover_id to 'Unknown.png'
                # Also setup the book_location - we'll use that in the newsletter to point to the book
                for _entry in book.links:
                    if _entry.rel == _thumbnail_uri:

                        try:
                            book['book_location'] = config.settings['serverbookurl'] + (_entry.href.rsplit('/', 1)[1])
                            book_cover_id = book.link.rsplit('/', 1)[1]
                            book["book_cover_id"] = book_cover_id
                            book["cover_thumbnail"] = get_thumbnail(_entry.href)
                            logger.debug('    Book has cover.')
                        except:
                            logger.debug('    Error in getting book cover.')
                            book["book_cover_id"] = "Unknown.png"
                            book['book_location'] = "#"

                    if book.get('book_cover_id', 'nope') == 'nope':
                        logger.debug('    Book nas no cover.')
                        book["book_cover_id"] = "Unknown.png"

                # The book summary that are posted with OPDS feeds can be long
                # Need to check for the size and if it's beyond a set size, reduce it
                try:
                    if len(book['summary']) >= config.settings['SUMMARY_LENGTH']:
                        book['short_summary'] = book['summary'][:config.settings['SUMMARY_LENGTH']] + "...see site..."
                        logger.debug('    Book summary too long. Being shorten.')
                    elif len(book['summary']) == 0:
                        book['short_summary'] = 'No summary information.'
                        logger.debug('    Book summary does not exist.')
                    else:
                        book['short_summary'] = book["summary"]
                        logger.debug('    Book summary too long. Being shorten.')

                except:
                    book['short_summary'] = 'No summary information.'

                # add newly added book to array
                recent_books.append(book)

        return recent_books

    else:
        logger.error('Error getting opds feed! - Please check config. Status Code: ' + str(d.status))
        return False


def buildnewsletter(
            book_list
):
    """Routine to send an HTML newsletter


    """
    logger.info('Pulling together the newsletter.')

    __tmp__file__loc = "tmpicon.jpg"

    mailer = Mailer(dict(
            transport=dict(
                use='smtp',
                host=config.settings['SMTPSettings']['host'],
                port=config.settings['SMTPSettings']['port'],
                username=config.settings['SMTPSettings']['user'],
                password=config.settings['SMTPSettings']['password'],
                tls=config.settings['SMTPSettings']['startttls']
            )
        )
    )

    try:

        # Perform jinja

        message_template_file = config.settings['TEMPLATE_FILE']
        message_banner_img = os.path.join(config.settings['TEMPLATE_DIR'], config.settings['TEMPLATE_BANNER_IMG'])
        message_unknown_img = os.path.join(config.settings['TEMPLATE_DIR'], config.settings['TEMPLATE_NOCOVER_IMG'])
        message_intropara_file = os.path.join(config.settings['TEMPLATE_DIR'], config.settings['TEMPLATE_INTROPARA'])

        cd = config.settings['TEMPLATE_DIR']
        logger.info(cd)

        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(cd)
        )

        try:
            with open(message_intropara_file, 'r') as introparafile:
                message_intropara = introparafile.read().replace('\n', '')
                logger.info('Loaded newsletter intro paragraph.')
        except:
            message_intropara = "<p>New books added.</p>"
            logger.exception("Couldn't load intro paragraph.")
            logger.warn('Loading default newsletter intro paragraph.')

        messagebody = jinja_env.get_template(message_template_file).render(
            book_list=book_list,
            intropara_blk=message_intropara
        )

        mailer.start()

        message = Message(author=config.settings['SMTPSettings']['user'])
        message.subject = config.settings['SMTPSettings']['subject']
        message.plain = "This is only exciting if you use an HTML capable email client. Please disregard."
        message.rich = messagebody
        message.embed(message_banner_img)

        flg_unknown_embedded = False

        for book in book_list:
            if book["book_cover_id"] != "Unknown.png":
                book['cover_thumbnail'].save(__tmp__file__loc, "JPEG")
                message.embed((book["book_cover_id"]), open(__tmp__file__loc))
            elif book["book_cover_id"] == "Unknown.png" and not flg_unknown_embedded:
                message.embed(message_unknown_img)
                flg_unknown_embedded = True

        for winner in db_operations.get_dl_list():

            message.to = winner

            if config.settings['DevMode']:
                mailer.send(message)
                logger.info('DevMode - Sending email to %s', winner)
            else:
                mailer.send(message)
                logger.info('sending email to %s', winner)

    except:
        logger.exception('Error sending email.')

    mailer.stop()

    logger.info('Completed newsletter routine.')

    return


def main(

):
    global logger

    setup_logging()

    logger = logging.getLogger(__name__)

    logger.info('Starting script.')

    # config.settings

    if config.get_config():

        new_book_table = getnewbooks()

        if new_book_table:
            logger.info("We found " + str(len(new_book_table)) + ' new books.')
            buildnewsletter(new_book_table)
        else:
            logger.info("We didn't find any books.")
    else:
        logger.error("No configuration loaded.")

    logger.info('Finishing script.')


if __name__ == "__main__":
    main()
