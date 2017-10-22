# cps-WhatsNew #
## Background ##
I totally love [calibre-web](https://github.com/janeczku/calibre-web) as an interface to my [calibre](https://calibre-ebook.com) collection.  One feature I thought the system could use is a notification or newsletter that would inform site users know what books have been uploaded.  In addition, I wanted a project to sink my teeth into while learning Python.

The result is this project.  I don't know if it'll be supported in the future as its purpose was just to experience python programming, however, I thought it would be great to at least expose the code publicly to give back to the community.

## General Info ##

Basic python v2 script that will read the OPDS feed of a calibre-web site (or any other opds feed for that matter - never tested it, but it should work), scan for new books uploaded in a given time frame, then send an email out to a set of interested folks.  

### Configuration files ###
There are two configuration files in the project - one for logging and the other for the project itself.  Coming from a big corporate environment, logging is something I don't see a lot of and I wanted to make it a point of including it right from the beginning as opposed to something that is baked in afterwards.

The other configuration file is a standard JSON formatted configuration file.  The program is so small and its relatively obvious what its supposed to be doing that I don't think its really all that important to write up documentation on each setting.  However, if you have a question, just ask.

### Email Template ###
The email template is a little.... complicated.  I used [BeeFree.io](http://Beefree.io) to create it.  Great service - but, MAN!, the resulting HTML is pretty involved!  

In any event, I'm embedding a banner image for the email template.  You can find the location in the config file.  If your email does not have a banner - remove the appropriate line in the code. 

### Log File ###
Like I mentioned previously, I put logging into the script (and maybe a little too much.)  I've used the inherent python logging libraries and you can see the settings in the appropriate logging configuration file. Initially, I set it up for circular logging to save on disk space. More for my own sanity than anything else.

### Thumbnails ###
I was able add book thumbnails to the outgoing email.  Unfortunately, I needed the ability to write the thumbnail to disk before embedding it into the email.  I'm sure I don't HAVE to do this, but after awhile it was just easier.  Thus, as a requirement, whatever user you use to run this script, they must have write access to the directory.

### Distribution List management ###
I originally kept the distribution list in the configuration file, however, after thinking about it for a bit, I decided to go ahead and attempt to add a database table to this script.

A new configuration item in the config file tells the script to either pull the dl members from the configuration file or attempt the db method.

Now - the database is really an overkill feature for this script.  You can simply maintain the dl in the configuration file.  Then I started thinking, what if I attempt to extend the cps database to included the one field I wanted - basically a way of opting out of the newsletter. 

## Future Features ##

Working on db option.


