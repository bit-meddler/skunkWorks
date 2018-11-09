import logging
logger = logging.getLogger(__name__)

import time
import anotherLib

def do_something():
    print "About to"
    logger.info( "Do something" )
    time.sleep( 1 )
    print "Now Done"
    logger.info( "I did the Thang!" )
    logger.error( "Don't open that door McGee!" )
    anotherLib.do_another_thing()
