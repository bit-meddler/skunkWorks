"""
    collection of functions to read vicon data, staring simple with the XML stuff
        XCP
        VSK
        VSS
    Then on to the hard one, x2d
        X2D
"""

import numpy as np
from xml.dom import minidom
from quaternions import Quaternion

# In case we run out of precision
FLOAT_T = np.float32
INT_T   = np.int32


class ViconCamera( object ):

    def __init__( self, input_dict=None ):
        # camera data
        self.hw_id       = -1 # uniue id.  data is in id order in the x2d
        self.type        = ""
        self.vicon_name  = ""
        self.px_aspect   = -1 # 
        self.sensor_type = ""
        self.sensor_wh   = [0, 0] # px
        self.user_id     = -1
        
        # raw calibration data
        self._pp    = [0., 0.] # px
        self._radial= [0., 0.] # k1, k2
        self._pos   = [0., 0., 0.] # tx, ty, tz
        self._rotQ  = [0., 0., 0., 0.] # uartonions [x,y,z,w]
        self._err   = 0. # rms reprojection error
        self._skew  = 0. # ??
        self._focal = 0. # f in sensor px?
        
        # computed matrixs
        self.K  = np.eye( 3, dtype=FLOAT_T )
        self.R  = np.eye( 3, dtype=FLOAT_T )
        self.Q  = Quaternion()
        self.T  = np.zeros( (3,),  dtype=FLOAT_T )
        self.RT = np.zeros( (3,4), dtype=FLOAT_T )
        self.P  = np.zeros( (3,4), dtype=FLOAT_T )

        if( input_dict is not None ):
            self.setFromDict( input_dict )

            
    def setFromDict( self, dict ):
        self.hw_id       = dict["DEVICEID"]
        self.type        = dict["TYPE"]
        self.vicon_name  = dict["NAME"]
        self.px_aspect   = dict["PIXEL_ASPECT_RATIO"]
        self.sensor_type = dict["SENSOR"]
        self.sensor_wh   = dict["SENSOR_SIZE"]
        self.user_id     = dict["USERID"]
        self._pp         = dict["PRINCIPAL_POINT"]
        self._radial     = dict["VICON_RADIAL"]
        self._skew       = dict["SKEW"]
        self._focal      = dict["FOCAL_LENGTH"]
        self._pos        = dict["POSITION"]
        self._rotQ       = dict["ORIENTATION"]
        self._err        = dict["IMAGE_ERROR"]

        self.computeMatrix()


    def computeMatrix( self ):
        # compose RT
        self.T = self._pos

        x, y, z, w = self._rotQ
        self.Q.setQ( x, y, z, w )
        self.R = self.Q.toRotMat2()

        self.RT[ :3, :3 ] = self.R
        self.RT[ :, 3 ]   = self.T # do I need to transform the T?
        
        # compose K
        # fiddle with PP, focal length, aspect ratio and possibly skew
        
        # compute P = K.RT
        self.P = np.dot( self.K, self.RT )


    def projectPoints( self, points3D ):
        ret = np.zeros( ( points3D.shape[0], 3 ), dtype=FLOAT_T )
        # ret = self.P * points3D
        return ret


    
class CalReader( object ):

    CASTS = {
        # Intrinsics
        "PRINCIPAL_POINT"    : lambda x: map( float, x.split() ),
        "VICON_RADIAL"       : lambda x: map( float, x.split() ),
        "SKEW"               : float,
        "FOCAL_LENGTH"       : float,
        # extrinsics
        "ORIENTATION"        : lambda x: np.array( x.split(), dtype=FLOAT_T),
        "POSITION"           : lambda x: np.array( x.split(), dtype=FLOAT_T),
        # Meta Data
        "SENSOR_SIZE"        : lambda x: map( int, x.split() ),
        "PIXEL_ASPECT_RATIO" : float,
        "DEVICEID"           : int,
        "USERID"             : int,
        "NAME"               : lambda x: x, # passthru
        "SENSOR"             : lambda x: x, # passthru
        "TYPE"               : lambda x: x, # passthru
        "IMAGE_ERROR"        : float,
    }
    
    CAMERA_ID_KEY = "DEVICEID"
    CAMERA_ATTERS_HARDWARE = ( "DEVICEID", "NAME", "PIXEL_ASPECT_RATIO", "SENSOR", "SENSOR_SIZE", "SKEW", "TYPE", "USERID" )
    CAMERA_ATTERS_CALIBRATION = ( "FOCAL_LENGTH", "IMAGE_ERROR", "ORIENTATION", "POSITION", "PRINCIPAL_POINT", "VICON_RADIAL" )
    
    def __init__( self ):
        self.reset()


    def reset( self ) :
        self.data = {}
        self.cameras = {}
        self.camera_order = []
        self.source_file = ""
        

    def read( self, file_path=None ):
        if( file_path is None ):
            print( "Error: no file supplied" )
            return -1

        mode = "XCP"
        
        self.source_file = file_path
        
        if( file_path.lower().endswith( ".xcp" ) ):
            mode = "XCP"
        elif( file_path.lower().endswith( ".cp" ) ):
            print( "Error: .cp not yet supported" )
            return -1
        
        if( mode == "XCP" ):
            XD = minidom.parse( file_path )
            cameras = XD.getElementsByTagName( "Camera" )
            
            for camera in cameras:
                # create dict
                cid = camera.attributes[ CalReader.CAMERA_ID_KEY ].value.encode( "ascii" )
                self.data[ cid ] = {}
                # load camera data
                for entry in CalReader.CAMERA_ATTERS_HARDWARE:
                    self.data[ cid ][ entry ] = camera.attributes[ entry ].value.encode( "ascii" )

                # load calibration data
                kf_list = camera.getElementsByTagName( "KeyFrame" )
                if( len( kf_list ) > 0 ):
                    for entry in CalReader.CAMERA_ATTERS_CALIBRATION:
                        self.data[ cid ][ entry ] = kf_list[0].attributes[ entry ].value.encode( "ascii" )
                        
                # cast
                for atter, cast in self.CASTS.iteritems():
                    self.data[ cid ][ atter ] = cast( self.data[ cid ][ atter ] )
                
        for cam_id, cam_data in self.data.iteritems():
            camera = ViconCamera( cam_data )
            self.cameras[ int( cam_id ) ] = camera

        self.camera_order = sorted( self.cameras.keys() )
        

if( __name__ == "__main__" ):
    # testing reading an xml
    file_path = r"170202_WictorK_Body_ROM_01.xcp"

    cal_reader = CalReader()
    cal_reader.read( file_path )
    
    for cid in cal_reader.camera_order:
        cam = cal_reader.cameras[ cid ]
        print( "Camera '{}' is at T:{} R:{}".format(
            cid, cam.T, np.degrees( cam.Q.toAngles2() ) ) )
    print( "Eggs" )

    # examining this in blade, the rot should be [166.497, -84.23, -119.151]
    cam = cal_reader.cameras[ 2107343 ]

    print np.degrees( cam.Q.toAngles()  )
    print np.degrees( cam.Q.toAngles2() )
    print np.degrees( cam.Q.toAngles3() )
    
