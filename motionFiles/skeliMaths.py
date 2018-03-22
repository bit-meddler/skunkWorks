""" Math Library for Skeleton operations
"""
def _rotMatXYZ( rx, ry, rz ):
    # compose and simplify rotation matrix in order of XYZ
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )


    M = [['cvz*cvy', '-svz*cvx +(cvz*svy*svx)', '-svz*-svx +(cvz*svy*cvx)'],
         ['svz*cvy',  'cvz*cvx +(svz*svy*svx)',  'cvz*-svx +(svz*svy*cvx)'],
         ['-svy', 'cvy*svx', 'cvy*cvx']]
    return M