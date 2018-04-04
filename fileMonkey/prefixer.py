""" rename files in a directory to have a given prefix, or replace the prefix
    with a new one.  Assumes this format "prefix_unique.ext"
"""
import os

path = r"C:\code\bladeScripts\globals\Scripts\bodyNav"
prefix = "bodyNav"

tasks = []

for _, _, files in os.walk( path ):
    for file in files:
        if( file.startswith( "_" ) or
            file.endswith( ".bat" ) ):
            continue
        filename = file
        pre, und, name = file.partition( "_" )
        if( und == "_" ):
            # removing old prefix
            filename = name
        tasks.append( (file, "_".join( (prefix, filename) ) ) )

fh = open( os.path.join( path, "rename.bat" ), "w" )
for source, dest in tasks:
    fh.write( "REN {} {}\n".format( source, dest ) )
fh.close()
