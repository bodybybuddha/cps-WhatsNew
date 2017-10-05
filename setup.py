from distutils.core import setup

setup(
    name='cps-WhatsNew',
    version='.9',
    packages=[''],
    url='',
    license='',
    author='John Taylor',
    author_email='jtaylor@recycledpapyr.us',
    description='Newsletter for calibre-web application',
    requires=[
        'feedparser',
        'marrow.mailer<4.1',
        'jinja2',
        'PILLOW'
    ]
)
