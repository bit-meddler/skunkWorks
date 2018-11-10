from collections import Counter
import os
from string import translate, maketrans 
import json
from difflib import SequenceMatcher


DELIMITERS = "._ -"
ENCIRCLERS = "(){}[]-.,_"

RESOLUTION = [ "720P", "720p", "1080P", "1080p", "HD", "480p", "480P", ]
DVD_TAGS   = [ "dvdrip", "DvDrip", "DVDrip", "DvDRip", "DVDRip", "DVD", ]
BR_TAGS    = [ "BluRay", "bluray", "BRRip", "BrRip", ]
AUDIO_TAGS = [ "AC3", "AAC", "MP3", ]
CODECS     = [ "Xvid", "XviD", "xvid", "h264", "x264", "H264", ]
CREW_TAGS  = [ "YIFY", "VPPV", "ETRG", "anoXmous", "aXXo", "VLiS", ]

META_CLUES = RESOLUTION + \
             DVD_TAGS + BR_TAGS + \
             AUDIO_TAGS + \
             CODECS + \
             CREW_TAGS

FIRST_LO = 1001
FIRST_HI = -1


TRANS_TABLE = maketrans( ENCIRCLERS, (' ' * len( ENCIRCLERS ) ) )

def smartSplit( str ):
    counts = Counter( str )
    win_c, delim = -1, "X"
    for d in DELIMITERS:
        count = counts[d]
        if count > win_c:
            win_c, delim = count, d
    if win_c<1:
        print "Ambigious delimiter"
        print str
        str = translate( str, TRANS_TABLE )
        delim = " "
        
    toks = str.split( delim )
    if len(toks)<2:
        print "Bad Split"
        return
    # split further on any braces
    ret = []
    for itm in toks:
        res = translate( itm, TRANS_TABLE ).split()
        ret.extend( res )
    return ret
    
def dir2task( filenames ):
    tasks = {}
    last_task = None
    last_task_name = None

    for name in filenames:
        fname, ex = os.path.splitext(name)
        if ex==".srt":
            score = SequenceMatcher( None, last_task, fname ).ratio()
            if score>0.75:
                tasks[last_task_name]["subs"] = name
                continue
        elif( ex==".db" or ex==".bat" or ex==".txt" ):
                continue
            
        tasks[name] = {}
        toks = smartSplit( fname )

        if toks ==None:
            tasks[name]={ "OK":False, "toks":None, "hasyear":False }
            continue
            
        num = len(toks)
        mid = num/2
        
        c_hi, c_lo = FIRST_HI, FIRST_LO
        for clue in META_CLUES:
            if clue not in toks:
                continue
            idx = toks.index( clue )
            if idx> c_hi:
                c_hi = idx
            if idx<c_lo:
                c_lo = idx

        if c_lo == FIRST_LO or c_hi == FIRST_HI:
            # test for iplayer
            tag = toks[-1]
            if tag in ("original", "editorial", "default", "iplayer" ):
                del toks[-2:]
        else:
            if c_hi<mid:
                # could be in middle or early?
                del toks[c_lo:c_hi+1]
            else:
                del toks[c_lo:]
           
        tasks[name]={ "OK":True, "toks":toks, "hasyear":False } 
        sub_idx = -1
        for i in range(len(toks)):
            text = toks[i]
            if text.isdigit():
                val = int( text )
                if val>1888 and val<2020:
                    #probably a year
                    toks[i] = "({})".format(val)
                    sub_idx = i
                    tasks[name]["hasyear"] = True
                    
        if sub_idx>0:            
            tasks[name]["new"] = " ".join( toks[:sub_idx+1] )
        elif tasks[name]["OK"]:
            tasks[name]["new"] = " ".join( toks )
        last_task = fname
        last_task_name = name
            
    for name, dat in tasks.iteritems():
        if not dat["OK"]:
            print "'{}' couldn't be parsed".format(name)
        elif not dat["hasyear"]:
            print "'{}' has no year".format(dat["new"])
    return tasks


def dic2JSON( dict, out_file_path ):
    res = json.dumps( dict, sort_keys=True, indent=2, separators=(":",",") )

    fh = open( out_file_path, "w" )
    fh.write(res)
    fh.close()

def getFiles( root_path ):
    # file
    import unicodedata
    res = []
    for root, dirs, files in os.walk( root_path ):
        for file in files:
            try:
                if type( file ) == str:
                    norm = file
                else:
                    norm = unicodedata.normalize( "NFKD", file )
                res.append( norm.encode( 'ascii', 'replace' ) )
            except:
                print file, type( file )
        return res

# begin
base_path = "G:\\"
file_list = getFiles( base_path )
tasks = dir2task( file_list )
out_file_path = os.path.join( base_path, "mover.bat" )
fh = open( out_file_path, "w" )
for t in tasks.keys():
    task = tasks[t]
    if task['OK']:
        year = ""
        new = task['new']
        if not task['hasyear']:
            fh.write( "REM *** https://www.google.co.uk/search?q=imdb+{} ***\n".format( new.replace(" ", "+") ) )
            new += " ()"
        fh.write( 'MKDIR "{}"\n'.format( new ) )
        fh.write( 'MOVE "{}" "{}"\n'.format( t, new ) )
        if "subs" in task:
            fh.write( 'MOVE "{}" "{}"\n'.format( task['subs'], new ) )
    else:
        print "No instructions for '{}'".format( t )
fh.close()           
#dic2JSON( tasks, os.path.join( base_path, "films.json" ) )
