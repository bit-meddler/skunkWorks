import logging
logger = logging.getLogger("Melvin.moleman")

import time


def do_something():
    print "About to"
    logger.info( "Do something" )
    time.sleep( 1 )
    print "Now Done"
    logger.error( "Don't open that door McGee!" )
