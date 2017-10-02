# cps-What'sNew #
## Background ##
I totally love [calibre-web](https://github.com/janeczku/calibre-web) as an interface to my [calibre](https://calibre-ebook.com) collection.  One feature I thought the system could use is a notification or newsletter feature that would allow users of a site know what books have been uploaded.  In addition, I wanted a project to sink my teeth into while learning python.

The result is this project.  I don't know if it'll be supported in the future as its purpose was just to experience python programming, however, I thought it would be great to at least expose the code publicly to give back to the community.

## General Info ##

Basic python v2 script that will read the opds feed of a calibre-web site (or any other opds feed for that matter - never tested it, but it should work), scan for new books uploaded in a given time frame, then send an email out to a set of interested folks.  

### Configuration files ###
There are two configuration files in the project - one for logging and the other for the project itself.  Coming from a big corporate environment, logging is something I don't see a lot of and I wanted to make it a point of including it right from the beginning as opposed to something that is baked in afterwards.

The other configuration file is a standard JSON formatted configuration file.  The program is so small and its relatively obvious what its supposed to be doing that I don't think its really all that important to write up documentation on each setting.  However, if you have a question, just ask.

## Future Features ##
There is my first crack at the application.  I have some of the basics down - feed parsing, email templating, etc.  Here are some of the area left to tackle:

1. Book thumbnails
2. Better HTML template (I stole some CSS as oppose to writing my own - will have to redo this bit.)
3. Distrubution List mgt - currently system relies on a config file for a list of email addresses for it's distribution list.  It would be nice to tap directly into the calibre-web database.
 No newline at end of file
