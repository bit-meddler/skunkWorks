import numpy as np


class Kalman1D( object ):

    def __init__( self, x, v, a ):
        self.x = np.array( [x,v] ) # Mean
        self.a = a # acceleration variance
        
        self.P = np.eye(2) # Covariance

        self.last_x = np.zeros( self.x.shape )

    def predict( self, dt=1 ):
        self.last_x = self.x
        
        F = np.array( [[1, dt], [0,1]] )
        new_x = F.dot( self.x )

        G = np.array( [[0.5 * dt**2], [dt]] )
        new_P = F.dot( self.P ).dot( F.T ) + G.dot( G.T ) * self.a

        self.P = new_P
        self.x = new_x

    def update( self, m_x, m_v ):
        # y = z - H x
        # S = H P Ht + R
        # K = P Ht S^-1
        # x = x + K y
        # P = (I - K H) * P

        H = np.zeros((1, 2))
        H[0, 0] = 1

        z = np.array( [m_x] )
        R = np.array( [m_v] )

        y = z - H.dot( self.x )
        S = H.dot( self.P ).dot( H.T ) + R
        S_ = np.linalg.inv( S )
        
        print( "S", S )
        print( "S-1", S_ )
        
        K = self.P.dot( H.T ).dot( S_ )

        print( K )

        new_x = self.x + K.dot( y )
        new_P = (np.eye(2) - K.dot(H)).dot( self.P )

        self.P = new_P
        self.x = new_x


class Kalman2D( object ):
    
    def __init__( self, dt, u_x, u_y, std_acc, x_std_meas, y_std_meas ):
        """
        :param dt: sampling time (time for 1 cycle)
        :param u_x: acceleration in x-direction
        :param u_y: acceleration in y-direction
        :param std_acc: process noise magnitude
        :param x_std_meas: standard deviation of the measurement in x-direction
        :param y_std_meas: standard deviation of the measurement in y-direction
        """
        # Define sampling time
        self.dt = dt

        # Define the  control input variables
        self.u = np.matrix([ [u_x] [u_y] ])

        # Intial State
        self.x = np.matrix( [[0], [0], [0], [0]] )

        # Define the State Transition Matrix A
        self.A = np.matrix([[1, 0, self.dt,       0],
                            [0, 1,       0, self.dt],
                            [0, 0,       1,       0],
                            [0, 0,       0,       1],])
        
        # Define the Control Input Matrix B
        self.B = np.matrix([[(self.dt**2)/2,              0],
                            [             0, (self.dt**2)/2],
                            [       self.dt,              0],
                            [             0,        self.dt],])
        
        # Define Measurement Mapping Matrix
        self.H = np.matrix([[1, 0, 0, 0],
                            [0, 1, 0, 0],])
        
        #Initial Process Noise Covariance
        self.Q = np.matrix([[(self.dt**4)/4,              0, (self.dt**3)/2,              0],
                            [             0, (self.dt**4)/4,              0, (self.dt**3)/2],
                            [(self.dt**3)/2,              0,     self.dt**2,              0],
                            [             0, (self.dt**3)/2,              0,     self.dt**2],]) * std_acc**2
        
        #Initial Measurement Noise Covariance
        self.R = np.matrix([[ x_std_meas**2,             0],
                            [             0, y_std_meas**2],])

        #Initial Covariance Matrix
        self.P = np.eye(self.A.shape[1])


    def predict(self):
        # Update time state
        self.x = np.dot( self.A, self.x ) + np.dot( self.B, self.u )

        # Calculate error covariance
        self.P = np.dot( np.dot( self.A, self.P), self.A.T ) + self.Q
        return self.x[0:2]

    def update( self, z ):
        # Calculate the Kalman Gain
        S = np.dot( self.H, np.dot( self.P, self.H.T ) ) + self.R
        K = np.dot( np.dot( self.P, self.H.T ), np.linalg.inv( S ) )

        # update state
        self.x = np.round( self.x + np.dot( K, (z - np.dot( self.H, self.x )) ) )

        # Update error covariance matrix
        self.P = ( np.eye( self.H.shape[1] ) - (K * self.H) ) * self.P
        return self.x[0:2]
    

class KalmanSimple( object ):

    def __init__( self, init_val, init_val_e, init_est_e ):
        self.val = init_val
        self.val_e = init_val_e
        self.est = init_val
        self.est_e = init_est_e
        self.est_prev = init_val
        self.est_prev_e = init_est_e
        self.kg = 0

    def predict( self ):
        self.kg = self.est_e / ( self.est_e + self.val_e)
        self.est = self.est_prev + self.kg * ( self.val - self.est_prev )
        self.est_prev = self.est
        return self.est

    def update( self, val ):
        self.val = val
        self.est_e = (1.0 - self.kg) * self.est_prev_e
        self.est_prev_e = self.est_e


def test1D():
    kf = Kalman1D( 0.2, 2.3, 1.2 )
    kf.predict( 0.1 )

    print( kf.x, kf.P )

    kf.update( 2.1, 2.0 )
    
    kf.predict( 0.1 )

    print( kf.x, kf.P )

def testSimple():
    Ms = [ 68, 75, 71, 70, 74, 72 ]
    k = KalmanSimple( 68, 4, 2 )
    for m in Ms:
        k.update( m )
        est = k.predict()
        print( m, est, k.val, k.est_e, k.kg )


if( __name__=="__main__" ):

    testSimple()
