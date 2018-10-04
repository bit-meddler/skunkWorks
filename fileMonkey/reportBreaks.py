import re
import sys

# get args
if( len( sys.argv ) != 2 ):
    print( "USAGE: python reportBreaks.py FILENAME" )
    exit(0)
    
filename = sys.argv[1]

# prep Regex
REGEX_TIMEBASE = r"(?:\[Parsed_showinfo).*?(?:in time_base).*?([\d/]+).*?(?:frame_rate).*?([\d/]+).*"
REGEX_INFOLINE = r"(?:\[Parsed_showinfo).*(?:pts:)\s*([\d]+)\s*(?:pts_time:)([\d.]+)\s*.*"

MATCH_TIMEBASE = re.compile( REGEX_TIMEBASE, re.I )
MATCH_INFOLINE= re.compile( REGEX_INFOLINE, re.I )

# load file
fh = open( filename, "rb" )
# get timebase
sanity = 30
match = None
while( not match ):
    line = fh.readline()
    match = MATCH_TIMEBASE.match( line )

rate, divisor = map( float, match.group(2).split("/") )
timebase = rate / divisor
print( "Timebase: {}".format( timebase ) ) 

event_list = []

# get events
line = fh.readline()
while( line ):
    match = MATCH_INFOLINE.match( line )
    if match:
        time_s = match.group(2)
        event_list.append( float( time_s ) )
    line = fh.readline()
    
fh.close()

# report
f_durr = 1./ timebase
for i, t in enumerate( event_list ):
    secs, frame_ms = divmod( t, 1. )
    mins, secs = divmod( secs, 60. )
    hours, mins = divmod( mins, 60. )
    frames = round( frame_ms / f_durr )
    TC = map( int, [ hours, mins, secs, frames ] )
    print "Event: {: >3} => {:0>2}:{:0>2}:{:0>2}:{:0>2}".format( i, *TC )