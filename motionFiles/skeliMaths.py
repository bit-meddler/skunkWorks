""" Math Library for Skeleton operations
"""
import numpy as np


# -- Auto Generated Rotation matrixes for call combinations of DoFs and orders -- #
def _rotMatXYZ( rx, ry, rz ):
    # compose and simplify rotation matrix in order of XYZ
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )

    cz_sy = cz * sy
    sz_sy = sz * sy
    
    M = [ [(cz*cy), (-sz*cx)+(cz_sy*sx), (-sz*-sx)+(cz_sy*cx)],
          [(sz*cy), (cz*cx)+(sz_sy*sx),  (cz*-sx)+(sz_sy*cx) ],
          [-sy,     (cy*sx),             (cy*cx)             ] ]
    return M


def _rotMatXZY( rx, ry, rz ):
    # compose and simplify rotation matrix in order of XZY
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )

    msy_msz = -sy * -sz
    cy_msz  =  cy * -sz
    
    M = [ [(cy*cz),  (cy_msz*cx)+(sy*sx),  (cy_msz*-sx)+(sy*cx)  ],
          [sz,       (cz*cx),              (cz*-sx)              ],
          [(-sy*cz), (msy_msz*cx)+(cy*sx), (msy_msz*-sx)+(cy*cx) ] ]
    return M


def _rotMatYXZ( rx, ry, rz ):
    # compose and simplify rotation matrix in order of YXZ
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )

    msz_msx = -sz * -sx
    cz_msx  = cz  * -sx
    
    M = [ [(cz*cy)+(msz_msx*-sy), (-sz*cx), (cz*sy)+(msz_msx*cy) ],
          [(sz*cy)+(cz_msx*-sy),  (cz*cx),  (sz*sy)+(cz_msx*cy)  ],
          [(cx*-sy),              sx,       (cx*cy)              ] ]
    return M


def _rotMatYZX( rx, ry, rz ):
    # compose and simplify rotation matrix in order of YZX
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )

    cx_sz = cx * sz
    sx_sz = sx * sz
    
    M = [ [(cz*cy),              -sz,     (cz*sy)            ],
          [(cx_sz*cy)+(-sx*-sy), (cx*cz), (cx_sz*sy)+(-sx*cy)],
          [(sx_sz*cy)+(cx*-sy),  (sx*cz), (sx_sz*sy)+(cx*cy) ] ]
    return M


def _rotMatZXY( rx, ry, rz ):
    # compose and simplify rotation matrix in order of ZXY
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )

    sy_sx = sy * sx
    cy_sx = cy * sx
    
    M = [ [(cy*cz)+(sy_sx*sz),  (cy*-sz)+(sy_sx*cz), (sy*cx)],
          [(cx*sz),             (cx*cz),                 -sx],
          [(-sy*cz)+(cy_sx*sz), (-sy*-sz)+(cy_sx*cz), (cy*cx)] ]
    return M


def _rotMatZYX( rx, ry, rz ):
    # compose and simplify rotation matrix in order of ZYX
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )

    msx_msy =-sx * -sy
    cx_msy  = cx * -sy
    
    M = [ [(cy*cz),              (cy*-sz),                    sy],
          [(msx_msy*cz)+(cx*sz), (msx_msy*-sz)+(cx*cz), (-sx*cy)],
          [(cx_msy*cz)+(sx*sz),  (cx_msy*-sz)+(sx*cz),  (cx*cy) ] ]
    return M


def _rotMatXY( rx, ry, rz ):
    # compose and simplify rotation matrix in order of XY
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )

    M = [ [cy,  (sy*sx), (sy*cx) ],
          [0,   cx,      -sx     ],
          [-sy, (cy*sx), (cy*cx) ] ]
    return M


def _rotMatXZ( rx, ry, rz ):
    # compose and simplify rotation matrix in order of XZ
    cx, sx = np.cos( rx ), np.sin( rx )
    cz, sz = np.cos( rz ), np.sin( rz )

    M = [ [cz, (-sz*cx), (-sz*-sx)],
          [sz, (cz*cx),  (cz*-sx) ],
          [0,  sx,        cx      ] ]
    return M


def _rotMatYX( rx, ry, rz ):
    # compose and simplify rotation matrix in order of YX
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )

    M = [ [cy,         0, sy      ],
          [(-sx*-sy), cx, (-sx*cy)],
          [(cx*-sy),  sx, (cx*cy) ] ]
    return M


def _rotMatYZ( rx, ry, rz ):
    # compose and simplify rotation matrix in order of YZ
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )

    M = [ [(cz*cy), -sz, (cz*sy)],
          [(sz*cy),  cz, (sz*sy)],
          [-sy,       0,  cy    ] ]
    return M


def _rotMatZX( rx, ry, rz ):
    # compose and simplify rotation matrix in order of ZX
    cx, sx = np.cos( rx ), np.sin( rx )
    cz, sz = np.cos( rz ), np.sin( rz )

    M = [ [cz,      -sz,     0  ],
          [(cx*sz), (cx*cz), -sx],
          [(sx*sz), (sx*cz),  cx] ]
    return M


def _rotMatZY( rx, ry, rz ):
    # compose and simplify rotation matrix in order of ZY
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )

    M = [ [(cy*cz),  (cy*-sz),  sy],
          [sz,       cz,        0 ],
          [(-sy*cz), (-sy*-sz), cy] ]
    return M


def _rotMatX( rx, ry, rz ):
    # compose and simplify rotation matrix in order of X
    cx, sx = np.cos( rx ), np.sin( rx )

    M = [ [1, 0,   0 ],
          [0, cx, -sx],
          [0, sx,  cx] ]
    return M


def _rotMatY( rx, ry, rz ):
    # compose and simplify rotation matrix in order of Y
    cy, sy = np.cos( ry ), np.sin( ry )


    M = [ [cy,  0, sy],
          [0,   1,  0],
          [-sy, 0, cy] ]
    return M


def _rotMatZ( rx, ry, rz ):
    # compose and simplify rotation matrix in order of Z
    cz, sz = np.cos( rz ), np.sin( rz )


    M = [ [cz, -sz, 0],
          [sz,  cz, 0],
          [0,   0,  1] ]
    return M
    
AXISDICT = {
    "XYZ" : _rotMatXYZ,
    "XZY" : _rotMatXZY,
    "YXZ" : _rotMatYXZ,
    "YZX" : _rotMatYZX,
    "ZXY" : _rotMatZXY,
    "ZYX" : _rotMatZYX,
    "XY"  : _rotMatXY,
    "XZ"  : _rotMatXZ,
    "YX"  : _rotMatYX,
    "YZ"  : _rotMatYZ,
    "ZX"  : _rotMatZX,
    "ZY"  : _rotMatZY,
    "X"   : _rotMatX,
    "Y"   : _rotMatY,
    "Z"   : _rotMatZ
}
# -- End of autogenerated code ----------------------------------------------- #

ARRAYS = map( type, [ [], (), np.zeros((3)) ] )


def formMatDirect( rx, ry, rz, axis ):
    # Assumes valid input, angles in floats, units radians
    return AXISDICT[ axis ]( rx, ry, rz )

    
def formMatSafe( rx=None, ry=None, rz=None, axis="XYZ", units="D" ):
    """
        Safe method to form matrix.  may take a list-like of 3 angles, can specifiy
        units for conversion
    """
    if( rx is None ):
        return np.eye(3)
        
    _rx, _ry, _rz = 0., 0., 0.
    
    if( type( rx ) in ARRAYS ):
        if( len( rx ) == 3 ):
            if( units == "D" ):
                _rx, _ry, _rz = np.radians( rx )
            else:
                _rx, _ry, _rz = rx
    else:
        if( ry == None ):
            ry = 0.
        if( rz == None ):
            rx = 0.
        if( units == "D" ):
            _rx, _ry, _rz = np.radians( [rx,ry,rz] )
        else:    
            _rx, _ry, _rz = rx, ry, rz
    if( axis not in AXISDICT ):
        axis = "XYZ"
        
    return formMatDirect( _rx, _ry, _rz, axis )

    
if( __name__ == "__main__" ):
    # test
    R = np.radians( [10,20,30] )
    print formMatSafe( R, axis="XYZ", units="R" )
    print formMatSafe( [10,20,30] )
    R = np.radians( [0,90,30] )
    print formMatSafe( R, axis="XYZ", units="R" )
    print formMatSafe( R, axis="YZX", units="R" )
