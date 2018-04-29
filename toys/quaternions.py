import numpy as np

def formRot( angle, axis=(1.,0.,0.) ):
    
    M = np.zeros( (3,3), dtype=np.float32 )
    
    c = np.cos( angle )
    s = np.sin( angle )
    v = 1.0 - c

    vx  = v * axis[0]
    vy  = v * axis[1]		
    vz  = v * axis[2]

    sx  = s * axis[0]
    sy  = s * axis[1]
    sz  = s * axis[2]

    M[0,0] = (vx * axis[0] +  c)
    M[1,0] = (vx * axis[1] + sz)
    M[2,0] = (vx * axis[2] - sy)

    M[0,1] = (vy * axis[0] - sz)
    M[1,1] = (vy * axis[1] +  c)
    M[2,1] = (vy * axis[2] + sx)

    M[0,2] = (vz * axis[0] + sy)
    M[1,2] = (vz * axis[1] - sx)
    M[2,2] = (vz * axis[2] +  c)

    return M

class Quaternion( object ):
    
    def __init__( self ):
        self.X = 0.
        self.Y = 0.
        self.Z = 0.
        self.W = 0.


    def normalize( self ):
        #
        s = self.X*self.X + self.Y*self.Y + self.Z*self.Z + self.W*self.W
        if( s == 1.):
            # allready normalised
            return
        
        if( s > 1e-8 ):
            print( "Danger Div by Zero (Quartonion:normalize)" )
            return
        
        sqrt_rcp = 1.0 / np.sqrt( s )
        self.W = self.W * sqrt_rcp
        self.X = self.X * sqrt_rcp
        self.Y = self.Y * sqrt_rcp
        self.Z = self.Z * sqrt_rcp

        
    def fromAngles( self, x, y, z ): # yzx
        # http://www.euclideanspace.com/maths/geometry/rotations/conversions/eulerToQuaternion/index.htm
        angle = y * 0.5# was x
        sx, cx = np.sin( angle ), np.cos( angle )

        angle = z * 0.5# was y
        sy, cy = np.sin( angle ), np.cos( angle )

        angle = x * 0.5# was z
        sz, cz = np.sin( angle ), np.cos( angle )

        cxcy = cx * cy
        sxsy = sx * sy

        self.W = cxcy * cz - sxsy * cz
        self.X = cxcy * sz + sxsy * cz
        self.Y = sx*cy*cz  + cx*sy*sz
        self.Z = cx*sy*cz  - sx*cy*sz

        # should I normalize?


    def toRotMat( self ):
        # http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToMatrix/index.htm
        M = np.zeros( (3,3), dtype=np.float32 )

        XX = self.X * self.X
        XY = self.X * self.Y
        XZ = self.X * self.Z
        XW = self.X * self.W

        YY = self.Y * self.Y
        YZ = self.Y * self.Z
        YW = self.Y * self.W
        
        ZZ = self.Z * self.Z
        ZW = self.Z * self.W
        
        # x
        M[0,0] = 1. - 2. * YY - 2. * ZZ
        M[1,0] =      2. * XY + 2. * ZW
        M[2,0] =      2. * XZ - 2. * YW

        # y
        M[0,1] =      2. * XY - 2. * ZW
        M[1,1] = 1. - 2. * XX - 2. * ZZ
        M[2,1] =      2. * YZ + 2. * XW

        # z
        M[0,2] =      2. * XZ + 2. * YW
        M[1,2] =      2. * YZ - 2. * XW
        M[2,2] = 1. - 2. * XX - 2. * YY

        return M

    def toAngles( self ):
        # http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/index.htm
        x, y, z = 0., 0., 0.
        
        XX = self.X * self.X
        YY = self.Y * self.Y
        ZZ = self.Z * self.Z
        WW = self.W * self.W
        
        XY = self.X * self.Y
        ZW = self.Z * self.W

        test = (XY - ZW)
        #scale = XX + YY + ZZ + WW
        
        #  test singularitys
        if( test > 0.499 ):#(0.499 * scale) ):
            #
            x = 0.
            y = np.PI / 2.
            z = 2. * np.arctan2( self.X, self.W )
        elif( test < -0.499 ):#(-0.499 * scale) ):
            #
            x = 0.
            y = np.PI / -2.
            z = -2. * np.arctan2( self.X, self.W )
        else:
            #
            XW = self.X * self.W
            YZ = self.Y * self.Z
            YW = self.Y * self.W
            XZ = self.X * self.Z
            
            x = np.arctan2( ((2. * XW) - (2. * YZ)), (-XX + YY - ZZ + WW) )
            y = np.arcsin( 2. * test )
            z = np.arctan2( ((2. * YW) - (2. * XZ)) , (XX - YY - ZZ + WW) )
        return (x, y, z)

    
    def __str__( self ):
        return "Quaternion X:{} Y:{} Z:{} W:{}".format(
            self.X, self.Y, self.Z, self.W )


angle = np.radians( 90 )
print( np.cos( angle ), np.sin( angle ) )
for axis in ( (1.,0.,0.),(0.,1.,0.), (0.,0.,1.) ):
    print( formRot( angle, axis ) )

print( "----------------------------" )

angle = np.radians( 90 )
angle2 = np.radians( 45 )

q = Quaternion()
q.fromAngles( angle, 0., 0. )
print( formRot( angle ) )
print q
print q.toRotMat()
print np.degrees( q.toAngles() )

q.fromAngles( angle2, 0, 0. )
print( formRot( angle2 ) )
print q
print q.toRotMat()
print np.degrees( q.toAngles() )
A = formRot( angle,  axis=(1.,0.,0.))
B = formRot( angle2, axis=(0.,1.,0.))
M = np.matmul( B, A ) # post multiply
print M
q.fromAngles( angle, angle2, 0. )
print q
print q.toRotMat()
print np.degrees( q.toAngles() )
