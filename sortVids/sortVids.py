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

def smartSplit( text ):
    counts = Counter( text )
    win_c, delim = -1, "X"
    for d in DELIMITERS:
        count = counts[d]
        if count > win_c:
            win_c, delim = count, d
    if win_c<1:
        print "Ambigious delimiter"
        print text
        text = translate( text, TRANS_TABLE )
        delim = " "
        
    toks = text.split( delim )
    if len(toks)<2:
        print "Bad Split"
        return
    # split further on any braces
    ret = []
    for itm in toks:
        res = translate( itm, TRANS_TABLE ).split()
        ret.extend( res )
    return ret
    
def dir2task( filenames, do_split=True ):
    tasks = {}
    last_task = None
    last_task_name = None
    print len( filenames )

    for name in filenames:
        if do_split:
            fname, ex = os.path.splitext(name)
            print fname, ex
            if ex==".srt":
                if last_task==None:
                    continue
                score = SequenceMatcher( None, last_task, fname ).ratio()
                if score>0.75:
                    tasks[last_task_name]["subs"] = name
                    continue
            elif( ex==".db" or ex==".bat" or ex==".txt" or ex=="sh" ):
                    continue
        else:
            fname = name

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
                if type( file ) == text:
                    norm = file
                else:
                    norm = unicodedata.normalize( "NFKD", file )
                res.append( norm.encode( "ascii", "replace" ) )
            except:
                print file, type( file )
        return res

def getDirs( root_path ):
    # dirs
    import unicodedata
    res = []
    for root, dirs, files in os.walk( root_path ):
        for d in dirs:
            res.append( d )
    return res

def archCmd( arch, cmd, remark=None, source=None, target=None ):
    ret = ""
    if cmd=="coment":
        if arch=="win":
            ret = "REM *** {} ***\n".format( remark )
        elif arch=="nix":
            ret = "# *** {} ***\n".format( remark )
    elif  cmd=="mkdir":
        if arch=="win":
            ret = 'MKDIR "{}"\n'.format( target )
        elif arch=="nix":
            ret = 'mkdir -p "{}"\n'.format( target )
    elif  cmd=="move":
        if arch=="win":
            ret = 'MOVE "{}" "{}"\n'.format( source, target )
        elif arch=="nix":
            ret = 'mv "{}" "{}"\n'.format( source, target )
    return ret

def tasks2script( tasks, path, arch="win", d_mode=False ):
    # 
    ex = "bat" if arch=="win" else "sh"
    out_file_path = os.path.join( path, "mover."+ex )
    fh = open( out_file_path, "w" )

    for old, task in tasks.iteritems():
        if task['OK']:
            year = ""
            new = task['new']
            if not task['hasyear']:
                fh.write( archCmd( arch, "coment",
                    remark="https://www.google.co.uk/search?q=imdb+{}".format(
                        new.replace(" ", "+") )
                    )
                )
                new += " ()"
            if not d_mode:
                fh.write( archCmd( arch, "mkdir", target=new ) )
            if old==new:
                continue
            fh.write( archCmd( arch, "move", source=old, target=new ) )
            if "subs" in task:
                fh.write( archCmd( arch, "move", source=task['subs'], target=new ) )
        else:
            print "No instructions for '{}'".format( old )
    fh.close()  

# begin
base_path = "G:\\"
base_path = "/mnt/z_vids/film"
arch = "nix"

#file_list = getFiles( base_path )
#tasks = dir2task( file_list )
d_list = getDirs( base_path )
tasks = dir2task( d_list, False )

tasks2script( tasks, base_path, arch, True )
#dic2JSON( tasks, os.path.join( base_path, "films.json" ) )