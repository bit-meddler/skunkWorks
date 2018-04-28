"""
    collection of functions to read vicon data, staring simple with the XML stuff
        XCP
        VSK
        VSS
    Then on to the hard one, x2d
        X2D
"""

import numpy as np

# In case we run out of precision
FLOAT_T = np.float32
INT_T   = np.int32


class ViconCamera( object ):

    def __init__( self, input_dict=None ):
        self.hw_id = -1
        self.type = ""
        self.vicon_name = ""
        self.px_aspect = -1
        self.sensor_type = ""
        self.sensor_wh = [0,0]
        self.user_id = -1
        self.calibration = []
        self.K  = np.zeros( (3,3), dtype=FLOAT_T )
        self.R  = np.zeros( (3,3), dtype=FLOAT_T )
        self.T  = np.zeros( (3,),  dtype=FLOAT_T )
        self.RT = np.zeros( (3,4), dtype=FLOAT_T )
        self.P  = np.zeros( (3,4), dtype=FLOAT_T )

        if( input_dict is not None ):
            self.setFromDict( input_dict )

            
    def setFromDict( self, dict ):
        pass


    def computerMatrix( self ):
        # compose RT

        # compose K

        # compute P = K.RT
        self.P = np.dot( self.K, self.RT )
        pass


    def projectPoints( self, points3D ):
        ret = np.zeros( ( points3D.shape[0], 3 ), dtype=FLOAT_T )
        # ret = points3D * self.P
        return ret


    
class CalReader( object ):

    CASTS = {
        # Intrinsics
        "PRINCIPAL_POINT"    : lambda x: np.array( x.split(), dtype=FLOAT_T),
        "VICON_RADIAL"       : lambda x: np.array( x.split(), dtype=FLOAT_T),
        "SKEW"               : float,
        "FOCAL_LENGTH"       : float,
        # extrinsics
        "ORIENTATION"        : lambda x: np.array( x.split(), dtype=FLOAT_T),
        "POSITION"           : lambda x: np.array( x.split(), dtype=FLOAT_T),
        # Meta Data
        "SENSOR_SIZE"        : lambda x: np.array( x.split(), dtype=INT_T),
        "PIXEL_ASPECT_RATIO" : float,
        "DEVICEID"           : int,
        "NAME"               : lambda x: x, # passtrue
        "IMAGE_ERROR"        : float,
    }
    
    CAMERA_ID_KEY = "DEVICEID"
    CAMERA_ATTERS_HARDWARE = ( "NAME", "PIXEL_ASPECT_RATIO", "SENSOR", "SENSOR_SIZE", "SKEW", "TYPE", "USERID" )
    CAMERA_ATTERS_CALIBRATION = ( "FOCAL_LENGTH", "IMAGE_ERROR", "ORIENTATION", "POSITION", "PRINCIPAL_POINT", "VICON_RADIAL" )
    
    def __init__( self ):
        self.reset()


    def reset( self ) :
        self.data = {}
        self.cameras = []
        self.source_file = ""
        

    def read( self, file_path=None ):
        if( file_path is None ):
            print( "Error: no file supplied" )
            return -1

        mode = "XCP"

        if( file_path.lower().endswith( ".xcp" ) ):
            mode = "XCP"
        elif( file_path.lower().endswith( ".cp" ) ):
            print( "Error: .cp not yet supported" )
            return -1

        if( mode == "XCP" ):
            pass

if( __name__ == "__main__" ):
    # testing reading an xml
    file_path = r"170202_WictorK_Body_ROM_01.xcp"

    from xml.dom import minidom
    XD = minidom.parse( file_path )
    cameras = XD.getElementsByTagName( "Camera" )
    print( "{} Cameras found.".format( len( cameras ) ) )
    cam_dict = {}
    for camera in cameras:
        id = camera.attributes[ CalReader.CAMERA_ID_KEY ].value.encode( "ascii" )
        cam_dict[ id ] = {}
        
        for entry in CalReader.CAMERA_ATTERS_HARDWARE:
            cam_dict[ id ][ entry ] = camera.attributes[ entry ].value.encode( "ascii" )
            
        kf_list = camera.getElementsByTagName( "KeyFrame" )
        
        if( len( kf_list ) > 0 ):
            for entry in CalReader.CAMERA_ATTERS_CALIBRATION:
                cam_dict[ id ][ entry ] = kf_list[0].attributes[ entry ].value.encode( "ascii" )
                
    print( "Done!" )
