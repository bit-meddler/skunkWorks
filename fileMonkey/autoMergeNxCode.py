# Batch convert xf100 MXFs using ffmpeg
# when files split (crossing cards or for FAT reasons), combine them
import os
from glob import glob

# settings

FFMPEG_PATH = r"C:\port\ffmpeg\bin\ffmpeg.exe"
RUSHES_PATH = r"D:\rushes"
TARGET_PATH = os.path.join( RUSHES_PATH, "xcodes" )

PRESETS = {
    "xf100" : {
        "AUDIO_MIX"   : '-filter_complex "[0:a:0][0:a:1]amerge"',
        "VIDEO_CODEC" : '-c:v libx264 -preset faster -crf 27',
        "AUDIO_CODEC" : '-c:a aac -b:a 128',
        "OUTPUT_WRAP" : "mp4",
    },

    "default" : {
        "AUDIO_MIX"   : '-filter_complex "[0:a:0][0:a:1]amerge"',
        "VIDEO_CODEC" : '-c:v libx264 -preset faster -crf 26',
        "AUDIO_CODEC" : '-c:a mp3',
        "OUTPUT_WRAP" : "mp4",
    }
}


def buildXcode( path_fq, out_name, mode="default", type="single" ):
    conf = PRESETS[ mode ]
    load_mode = ""
    if( type == "single" ):
        load_mode = '-i "{}"'.format( path_fq )
    elif( type == "concat" ):
        load_mode = '-f concat -safe 0 -i "{}filelist.txt"'.format( path_fq )
    return '"{}" {} {} {} {} "{}.{}"\n'.format(
        FFMPEG_PATH, load_mode,
        conf[ "AUDIO_MIX" ], conf[ "VIDEO_CODEC" ], conf[ "AUDIO_CODEC" ],
        os.path.join( TARGET_PATH, out_name ), conf[ "OUTPUT_WRAP" ]
    )

# build task list
tasks = []
dirs = glob( os.path.join( RUSHES_PATH, "*", "" ) )
for clip in dirs:
    frags = glob( clip + "*.mxf" )
    clip_name = os.path.basename( os.path.dirname( clip ) )
    num_clips = len( frags )
    print clip_name, num_clips
    if( num_clips > 1 ): # concat operation
        # build file list
        fh = open( os.path.join( clip, "filelist.txt" ), "w" )
        for file in frags:
            fh.write( "file '{}'\n".format( file ) )
        fh.close()
        # register task (xcode, cleanup)
        tasks.append( buildXcode( clip, clip_name, mode="xf100", type="concat" ) )
        tasks.append( 'DEL "{}filelist.txt"\n'.format( clip ) )
    else:
        # register task (xcode)
        tasks.append( buildXcode( frags[0], clip_name, mode="xf100" ) )
        
# finally output as batch file
fh = open( os.path.join( RUSHES_PATH, "transcode.bat" ), "w" )
fh.write( "ECHO OFF\n" )
fh.write( "MKDIR {}\n".format( TARGET_PATH ) )
for task in tasks:
    fh.write( task )
fh.write( "DEL transcode.bat\n" )
fh.close()
