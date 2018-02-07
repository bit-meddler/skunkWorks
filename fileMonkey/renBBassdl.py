# RichH - autorename BB assessment bulk download to Student No.
import re
import os

tasks = []

SIDget = re.compile( "(\d{8})(?:_\w+(?:-\d\d)+)(?:.*)(\.\w{2,3})" )

file_path = r"C:\temp\comp\A2"

count = set()

for root, dirs, files in os.walk( file_path ):
    for name in files:
        lname = name.lower()
        res = SIDget.search( lname )
        if res:
            tasks.append( (name, res.group(1) + res.group(2)) )
            count.add( res.group(1) )

fh = open( os.path.join( file_path, "rename.bat" ), "w" )
for s,d in tasks:
    fh.write( 'ren "{}" "{}"\n'.format( s, d ) )
fh.close()
    
print( len(count) )
print( "\n".join( list(count) ) )
