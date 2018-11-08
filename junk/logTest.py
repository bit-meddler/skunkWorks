import logging
logger = logging.getLogger( "Melvin" )
formatter = logging.Formatter( "%(asctime)s.%(msecs)03d [%(levelname)-8s] (%(name)s): %(message)s {%(filename)s@%(lineno)s}", "%y%m%d %H:%M:%S" )

import exLib

def main():
    logger.setLevel( logging.DEBUG )

    ch = logging.StreamHandler()
    fh = logging.FileHandler( "fails.log.secret" )

    ch.setFormatter( formatter )
    fh.setFormatter( formatter )
    ch.setLevel( logging.ERROR )
    fh.setLevel( logging.DEBUG )

    logger.addHandler( fh )
    logger.addHandler( ch )
    
    # run application...
    logger.debug( "The square of the hypotenuse is equal to the sum of the squares of the other two sides" )
    logger.info( "I like apple sauce..." )
    exLib.do_something()
    logger.info( 'Eggs and spam and spam and eggs' )
    exLib.do_something()

if __name__ == '__main__':
    main()
