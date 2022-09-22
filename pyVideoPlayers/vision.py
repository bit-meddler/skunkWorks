import logging
log = logging.getLogger( __name__ )

import cv2
import numpy as np

class ImgProc( object ):
    # Preconditioning filters
    PC_GREY  = "PC_GREY"
    PC_BILIN = "PC_BILIN"

    @staticmethod
    def chessPrecondition( arr, mode=None ):
        """ apply one or more preconditioning steps to the image"""
        mode = mode or [ ImgProc.PC_GREY ]

        img = np.copy( arr )

        for operation in mode:

            if( operation == ImgProc.PC_GREY ):
                img = cv2.cvtColor( img, cv2.COLOR_RGB2GRAY )

            if( operation == ImgProc.PC_BILIN ):
                img = cv2.bilateralFilter( img, 5, 75, 75 )

        return img


    class Excluder( object ):
        """ Mask out a given area of the image that might confuse corner detection """

        def __init__( self, colour=(0,0,0) ):
            self.zones = {} # name:(x,y,m,n)
            self.colour = colour

        def exclude( self, img ):
            """ exclude contents of the zones """
            for reg in self.zones.items():
                cv2.rectangle( img, (reg[0],reg[1]), (reg[2],reg[3]), color=self.colour, thickness=-1 )

        def reexclude( self, img ):
            """ exclude the edge of the zones (useful to remove false detections) """
            for reg in self.zones.items():
                cv2.rectangle( img, (reg[0],reg[1]), (reg[2],reg[3]), color=self.colour, thickness=5 )

        def addMask( self, name, top_left, bottom_right ):
            self.zones[ name ] = ( top_left[0], top_left[1], bottom_right[0], bottom_right[1] )

        def remMask( self, name ):
            del( self.zones[ name ] )


class VideoHelper( object ):

    def fileDiagnose( self ):
        self._container = av.open( self._current_file )
        
        self._current_md = {}
        for stream in self._container.streams.get():
            s_type = stream.type

            if( s_type == "video" ):
                # Collect Video Metadata
                d = {}
                d["index"] = stream.index
                d["frames"] = stream.frames
                d["time_base"] = stream.time_base
                d["duration"] = stream.duration
                d["base_rate"] = stream.base_rate
                d["guessed_rate"] = stream.guessed_rate
                d["metadata"] = stream.metadata

                # Codec Data
                d["width"] = stream.codec_context.width
                d["height"] = stream.codec_context.height
                d["framerate"] = stream.codec_context.framerate
                d["codec_name"] = stream.codec_context.name
                d["pix_fmt"] = stream.codec_context.pix_fmt
                d["codec_time_base"] = stream.codec_context.time_base
                d["ticks_per_frame"] = stream.codec_context.ticks_per_frame

                # add to meta store
                self._current_md["video"] = d

            elif( s_type == "audio" ):
                # Collect audio Metadata
                d = {}
                d["index"] = stream.index
                d["frames"] = stream.frames
                d["time_base"] = stream.time_base
                d["duration"] = stream.duration
                d["base_rate"] = stream.base_rate
                d["guessed_rate"] = stream.guessed_rate
                d["metadata"] = stream.metadata

                # Codec Data
                d["channels"] = stream.codec_context.channels
                d["frame_size"] = stream.codec_context.frame_size
                d["rate"] = stream.codec_context.rate
                d["codec_name"] = stream.codec_context.name
                d["sample_rate"] = stream.codec_context.sample_rate
                d["frame_size"] = stream.codec_context.frame_size
                d["codec_time_base"] = stream.codec_context.time_base
                d["ticks_per_frame"] = stream.codec_context.ticks_per_frame

                # add to meta store
                self._current_md["audio"] = d

            elif( s_type == "data" ):
                # Timecode info
                d = {}
                d["index"] = stream.index
                d["frames"] = stream.frames
                d["time_base"] = stream.time_base
                d["duration"] = stream.duration
                d["base_rate"] = stream.base_rate
                d["guessed_rate"] = stream.guessed_rate
                d["metadata"] = stream.metadata

                # add to meta store
                self._current_md["data"] = d

        #pprint( self._current_md )

        # get relevent info from the video
        self.video_wh = ( self._current_md["video"]["width"], self._current_md["video"]["height"] )
        self.video_rate = self._current_md["video"]["framerate"].numerator
        self.video_timebase = self._current_md["video"]["time_base"].denominator
        self.video_title = self._container.metadata.get( "title", self._file_title )
        self.video_num_frames = self._current_md["video"]["frames"]
        self.video_stream_index = self._current_md["video"]["index"]

        # some may be missing or odd
        self.video_fftc = None
        if( "data" in self._current_md ):
            # Try to get timecode
            tc_md = self._current_md["data"]["metadata"]
            if( type( tc_md ) == dict ):
                # OK
                self.video_fftc = tc_md.get( "timecode", None )

        # Do some calculations with the metadata
        self.video_pts_per_frame = int( self.video_timebase / self.video_rate )

        # Use this to setup video replay
        self.timeline.setDuration( self.video_num_frames )
        self._stream = self._container.streams.get( self._current_md["video"]["index"] )[0]

        print( "{}: {} at {}fps with {} timebase. Duration: {}f, timecode:{},  {}pts per frame.".format(
            self.video_title, self.video_wh, self.video_rate, self.video_timebase, self.video_num_frames,
            self.video_fftc, self.video_pts_per_frame )
        )