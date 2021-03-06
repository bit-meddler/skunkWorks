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
        # see also: http://run.usc.edu/cs420-s15/lec05-viewing/05-viewing-6up.pdf
        # compose RT
        self.T = self._pos

        x, y, z, w = self._rotQ
        self.Q.setQ( x, y, z, w )
        # These transposed RotMats are driving me mad!
        self.R = self.Q.toRotMat2().T
        self.R = self.Q.toRotMat()
        
        # from Vicon's "Cara Reference" pdf (/Fileformats/XCP)
        # Assuming (!) XCPs are the same between products
        # P = [ R | -RT ]
        self.RT[ :3, :3 ] = self.R
        self.RT[ :, 3 ]   = -np.matmul( self.R, self.T )
        
        # compose K
        # fiddle with PP, focal length, aspect ratio and skew (which in all encountered files is zero0
        a           = self.px_aspect
        x_pp, y_pp  = self._pp
        f           = self._focal
        k           = self._skew
        
        self.K = np.array(
            [ [  f,     k, x_pp ],
              [ 0., (f/a), y_pp ],
              [ 0.,    0.,   1. ] ] , dtype=FLOAT_T )
        
        # compute P = K.RT
        self.P = np.matmul( self.K, self.RT )


    def undistort( self, point ):
        # As Vicon doesn't use NDCs the undistort is computed per det - dumb!
        a          = self.px_aspect
        w1, w2     = self._radial
        x_pp, y_pp = self._pp
        # Again from the CaraPost Refference pdf
        x_r, y_r = point
        dp = [ x_r - x_pp, a * ( y_r - y_pp ) ]
        print dp
        r = np.linalg.norm( dp )
        print r
        s = 1 + w1 * r**1 + w2 * r**2
        print s
        ud = [ s * dp[0] + x_pp, (s * dp[1] + y_pp)/a ]
        print ud

        
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

    # examining this in blade, the rot should be [166.497, -84.23, -119.151]
    cam = cal_reader.cameras[ 2107343 ]
    
    print np.degrees( cam.Q.toAngles()  )
    print np.degrees( cam.Q.toAngles2() )
    print np.degrees( cam.Q.toAngles3() )
    
    # 178, 408, 142 is about the center of 2107343
    x, y, z = np.matmul( cam.P, np.array( [-178.20, -408.21, 142.86, 1.] ) )
    print x/z, y/z
    # not bad :)
    
