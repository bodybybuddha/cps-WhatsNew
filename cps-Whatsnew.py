import feedparser
import os
import json
import logging.config
import urllib2
import base64
import cStringIO
from PIL import Image

from feedparser import _parse_date as parse_date
from time import mktime
from datetime import datetime, timedelta
from marrow.mailer import Mailer, Message
import jinja2

gConfig = None
gLogger = None


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


def get_thumbnail(
        book_cover_url
):
    """Routine to create a thumbnail from a URL that serves up a jpeg
        Not build a ton of catches in here, just assuming the above!
    """

    gLogger.debug("Building cover for: %s ", book_cover_url)

    size = 300, 300

    try:

        request = urllib2.Request(book_cover_url)
        base64string = base64.encodestring('%s:%s' % (gConfig['username'], gConfig['password'])).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        cover_file = cStringIO.StringIO(urllib2.urlopen(request).read())

        img = Image.open(cover_file)

        img.thumbnail(size, Image.ANTIALIAS)
        return img

    except:
        gLogger.debug("Couldn't get a cover thumbnail created.")
        return "no data"



def getnewbooks(

):

    """Routine to query cps to get the latest books added. return array of new books

    """
    gLogger.info('Getting new books from server')
    d = feedparser.parse('http://'
                         + gConfig['username'] + ':'
                         + gConfig['password'] + '@'
                         + gConfig['serveraddress'])

    gLogger.info('Name of the feed:' + d.feed.title)
    gLogger.info('Looking for books uploaded in the last: ' + str(gConfig['numofdaysfornotification']) + ' days.')

    _thumbnail_uri = u'http://opds-spec.org/image/thumbnail'
    recent_books = []

    if d.status == 200:
        for book in d.entries:
            dt = datetime.fromtimestamp(mktime(parse_date(book.updated)))
            if datetime.now() - dt < timedelta(days=int(gConfig['numofdaysfornotification'])):
                if 'title' in book:
                    gLogger.info('Found book. Title: ' + book.title)
                else:
                    gLogger.info('Found book. Strange, no Title field!')

                # Need to get a uniqueID for naming the CIDs in the html newsletter - pulling the GUID from the link url
                # While we are here, might as well find out if the book has a cover
                #  if the book has a cover set:
                #        the book_cover_id to the GUID
                #        pull the url to make it easier to get to
                #        go get the cover and resize it
                #  if the book doesn't have a cover, set book_cover_id to 'Unknown.png'
                for _entry in book.links:
                    if _entry.rel == _thumbnail_uri:

                        try:
                            book['book_cover_location'] = _entry.href
                            book_cover_id = book.link.rsplit('/', 1)[1]
                            book["book_cover_id"] = book_cover_id
                            book["cover_thumbnail"] = get_thumbnail(book['book_cover_location'])
                            gLogger.debug('    Book has cover.')
                        except:
                            gLogger.debug('    Error in getting book cover.')
                            book["book_cover_id"] = "Unknown.png"

                    if book.get('book_cover_id', 'nope') == 'nope':
                        gLogger.debug('    Book nas no cover.')
                        book["book_cover_id"] = "Unknown.png"

                # add newly added book to array
                recent_books.append(book)

        return recent_books

    else:
        gLogger.error('Error getting opds feed! - Please check config. Status Code: ' + str(d.status))


def buildnewsletter(
            book_list
):
    """Routine to send an HTML newsletter


    """
    gLogger.info('Pulling together the newsletter.')

    __tmp__file__loc = "tmpicon.jpg"

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

        message_template_file = os.path.join(gConfig['TEMPLATE_DIR'], gConfig['TEMPLATE_FILE'])
        message_banner_img = os.path.join(gConfig['TEMPLATE_DIR'], gConfig['TEMPLATE_BANNER_IMG'])
        message_unknown_img = os.path.join(gConfig['TEMPLATE_DIR'], gConfig['TEMPLATE_NOCOVER_IMG'])

        messagebody = jinjaenv.get_template(message_template_file).render(
            book_list=book_list
        )

        mailer.start()

        message = Message(author=gConfig['SMTPSettings']['user'])
        message.subject = gConfig['SMTPSettings']['subject']
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

        for winner in gConfig['DistributionList']:
            message.to = winner['addr']
            mailer.send(message)

    except:
        gLogger.exception('Error sending email.')

    mailer.stop()

    gLogger.info('Completed newsletter routine.')

    return


def main():
    global gLogger

    setup_logging()

    gLogger = logging.getLogger(__name__)

    gLogger.info('Starting script.')

    getconfig()

    if gConfig:
        new_book_table = getnewbooks()

        if new_book_table:
            gLogger.info("We found " + str(len(new_book_table)) + ' new books.')
            buildnewsletter(new_book_table)
        else:
            gLogger.info("We didn't find any books.")

    gLogger.info('Finishing script.')

if __name__ == "__main__":
    main()
