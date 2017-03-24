import feedparser
import os
import json
from feedparser import _parse_date as parse_date
from time import mktime
from datetime import datetime, timedelta


with open('config.json', 'r') as f:
    config = json.load(f)

path = os.path.dirname(__file__)

# modify this to change the Template Directory
TEMPLATE_DIR = '/templates/'
COVER_DIR = '/covers/'


def getnewbooks():
    d = feedparser.parse('http://' + config['username'] + ':' + config['password'] + '@' + config['serveraddress'])

    print d.feed.title

    for book in d.entries:
        dt = datetime.fromtimestamp(mktime(parse_date(book.updated)))
        if datetime.now() - dt < timedelta(days=7):
            if 'title' in book:
                print 'Title: ' + book.title
            if 'authors' in book:
                print 'Author(s): ' + book.author
            if 'summary' in book:
                print book.summary
            else:
                print 'No Summary'

if __name__ == "__main__":
    getnewbooks()



