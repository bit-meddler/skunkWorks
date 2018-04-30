# RichH - autorename BB assessment bulk download to Student No.
import re
import os

tasks = []

SIDget = re.compile( "(\d{8})(?:_\w+(?:-\d\d)+)(?:.*)(\.\w{2,3})" )
nameGet= re.compile( "(?:\w+):\s*(.+)\s+\((\d{8})\)" )

file_path = r"C:\Temp\A2"

count = set()
lut = {}
for root, dirs, files in os.walk( file_path ):
    for name in files:
        lname = name.lower()
        res = SIDget.search( lname )
        if res:
            tasks.append( (name, res.group(1) + res.group(2)) )
            count.add( res.group(1) )
        if( name.endswith( ".txt" ) ):
            fh = open( os.path.join( file_path, name ), "r" )
            txt = fh.readline()
            res = nameGet.search( txt )
            if res:
                lut[ res.group(2) ] = res.group(1).replace( " ", "_" )
            fh.close()
            
fh = open( os.path.join( file_path, "rename.bat" ), "w" )
tgts = set()
for s, d in tasks:
    toks = d.split( "." )
    name = lut[ toks[0] ]
    out = name + "." + toks[1]
    while( out in tgts ):
        name += "-"
        out = name + "." + toks[1]
    tgts.add( out )

    fh.write( 'ren "{}" "{}"\n'.format( s, out ) )
fh.close()
    
print( len(count) )
print( "\n".join( list(count) ) )
