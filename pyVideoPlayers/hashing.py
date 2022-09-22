import numpy as np
from copy import deepcopy

class Hash2DObj( object ):
    """Object to set up a hashing scheme for a given resolution of input data and given number of bins.
        This Object does not maintain 'priors', just offers hash functionality for the specifics (res, bins).
    
        Full documentation here: https://www.youtube.com/watch?v=JKv-qF5t2uc
    
    Attributes:
        bins (int): Number of Bins in each dimention
        cell_height (int): cell (bin) height in pixels
        cell_width (int): cell (bin) width in pixels
        half_cell_dims ((w,h) int): useful hint for selecting a max pixel velocity (used in matchIt)
        hash_2d (1d ndarray): helper to create the hash
        hash_max (int): Maximum hash value. gets bitwise and'ed to clamp hashes in legal range
        resolution ((w,h) int): source native resolution (assumes image-like, don't know how it will work with -1...+1 ranges)
        scale (1d ndarray): Scaling in x,y to effectivly divide by cell_width, cell_height
        search_pattern (tuple): list of neighbours to check for matches. have several presets
        SEARCH_PATTERNS (dict): Preset search patterns, for matching
    """

    SEARCH_PATTERNS = {
        "DOWN_RIGHT"   : ( "X", "E", "S", "SE" ),
        "4-NEIGHBOURS" : ( "X", "N", "E", "S", "W" ),
        "BOTTOM_HALF"  : ( "X", "E", "S", "W", "SE", "SW" ),
        "8-NEIGHBOURS" : ( "X", "N", "N2", "E", "SE", "S", "SW", "W", "NW" ),
        "EXHAUSTIVE"   : ( "X", "N", "N2", "E", "SE", "S", "SW", "W", "NW",
                                "N2", "NNE", "NE2", "ENE", "E2", "ESE", "SE2", "SSE",
                                "S2", "SSW", "SW2", "WSW", "W2", "WNW", "NW2", "NNW") ,
    }

    def __init__( self, bins, resolution ):
        """ Prepare the hashing object with info about what we're hashing
            Source Resolution, num required bins.  Precompute some fequently used values
        
        Args:
            bins                   (int): Number of bins.  I think this is best if a power of two.
            resolution  ((w,h) listlike): Resolution of what we are hashing.
        """
        self.bins = bins
        self.hash_max = (bins * bins) - 1
        self.resolution  = resolution
        self.cell_width  = resolution[0] / self.bins
        self.cell_height = resolution[1] / self.bins
        self.half_cell_dims = (self.cell_width/2., self.cell_height/2.)

        # precompute
        # scale equivelent of x/cell_width, y/cell_width => binx, biny
        self.scale = np.asarray( (1./self.cell_width, 1./self.cell_height ), dtype=np.float32 )

        # np.dot( data, this ) is the math equivenet of binx + bins * biny
        self.hash_2d = np.asarray( (1, bins), dtype=np.float32 ) 

        # cache of offset data (for diagnostics)
        self._offset_data = []

        # index hints
        """
        NW2 NNW N2  NNE NE2
        WNW NW  N   NE  ENE
        W2  W   X   E   E2
        WSW SW  S   SE  ESE
        SW2 SSW S2  SSE SE2
        """
        bins2 = bins * 2
        self._compass = {
            "X"   :  0,         # 'x' marks the Spot, Jim Lad, Arrggh!
            #
            "N"   : -bins,
            "NE"  : -(bins-1),
            "E"   :  1,
            "SE"  :  bins+1,
            "S"   :  bins,
            "SW"  :  bins-1,
            "W"   : -1,
            "NW"  : -(bins+1),
            #
            "N2"  : -bins2,
            "NNE" : -(bins2-1),
            "NE2" : -(bins2-2),
            "ENE" : -(bins-2),
            "E2"  :  2,
            "ESE" :  bins+2,
            "SE2" :  bins2+2,
            "SSE" :  bins2+1,
            "S2"  :  bins2,
            "SSW" :  bins2-1,
            "SW2" :  bins2-2,
            "WSW" :  bins-2,
            "W2"  : -2,
            "WNW" : -(bins-2),
            "NW2" : -(bins2+2),
            "NNW" : -(bins2+1),
        }
        self.search_pattern = None
        self.setSearchPattern( "BOTTOM_HALF" )

    def setSearchPattern( self, pattern="8-NEIGHBOURS", custom=None ):
        """ Generate the search pattern for matching, this can be from a preset, or
            explicitly set using the 'custom' parameter.  Custom must be a list-like
        
        Args:
            pattern  (str, optional): preset pattern to use
            custom  (list, optional): a custom pattern
        
        Returns:
            (tuple): The search pattern tuned for the number of cells in the hash.
        """
        if( pattern not in self.SEARCH_PATTERNS ):
            pattern = "8-NEIGHBOURS"

        search = []
        directions = custom or self.SEARCH_PATTERNS[ pattern ]
        for point in directions:
            search.append( self._compass[ point ] )

        self.search_pattern = tuple( search )

    def hashIt( self, A ):
        """ Perform a 2D spatial hash of the incoming data. Consider the "resolution" is split into
            a grid of self.bins in the x and y dimensions (non square bins allowed).

        Args:
            A (2d ndarray): detections to hash (assumed legal 0 < det < resolution)
        
        Returns:
            (2d ndarray): The Bin (hash) that every detection sits in (in lockstep with the data)
        """
        floored = np.floor( A * self.scale ) # floor to integer values
        dotted = np.dot( floored, self.hash_2d )
        return dotted.astype( np.int32 ) & self.hash_max

    def binIt( self, hash_in ):
        """ Gather the hashes into their bins 
        
        Args:
            hash_in (1d ndarray): List of hash assigments, in lockstep with the data they describe
        
        Returns:
            dict{int:list}: dict of {bin_id:[indexs in the bin]}
        """
        h_order = np.argsort( hash_in ) # saves constantly testing 'if hash_ in bins'
        last_hash = -1
        bins = {}
        for hidx in h_order:
            new_hash = hash_in[ hidx ]
            if( last_hash != new_hash ):
                bins[ new_hash ] = []
            bins[ new_hash ].append( hidx )
            last_hash = new_hash
        return bins

    def matchIt( self, other_binning, new_data, px_dist=None ):
        """ Try to match the new_data's binning to the other_binning.
            The px_dist is a slack in the amount of pixels a detection can move between frames.
            this is subtracted from the new data as an offset, fast moving dets are "wound back"
            to a more appropriate bin, helps most if a detection crosses a bin boundary
        
        Args:
            other_binning       (dict): Previous data's binning
            new_data      (2d ndarray): New data doesn't need to be the same shape as old_data
            px_dist  ((w,h), optional): Pixel Velocity compensation
        
        Returns:
            (List of lists): proposed matching from matches[ new_idx ] -> list of candidate old_idx (unordered)
        
        """
        offset = px_dist or 0.
        matches = [ [] for _ in range( len( new_data ) ) ]
        # Temp hash of the new data.  This goes round the corner
        self._offset_data = new_data - offset
        offset_hash = self.hashIt( self._offset_data )
        for new_idx, hash_ in enumerate( offset_hash ):
            for bin_ in self.search_pattern:
                candidate_bin = (hash_ + bin_) & self.hash_max # fixup going round the corner at bins**2
                # the fixup causes low right candidates to be offered in the top row
                # the distance metric should help prune them quickly
                if( candidate_bin in other_binning ):
                    matches[ new_idx ].extend( other_binning[ candidate_bin ] )
                    
        return matches

    @staticmethod
    def _metric( A, B ):
        """ Square manhatten distance (cheaper than true distance, eg: np.linalg.norm(A-B) )"""
        return sum( (A - B)**2 )

    def measureIt( self, matches, old_data, new_data ):
        """ Based on the proposed matches, get a distance metric from new det to old candidates
        
        Args:
            matches  (List of lists): matching from matches[ new_idx ] -> list of candidate old_idx
            old_data    (2d ndarray): Priot detections
            new_data    (2d ndarray): New detections
        
        Returns:
            (List of lists): distances from new_data[ new_idx ] -> old_data[ candidates ] Lockstep with matches
        """
        
        distances = [ [] for _ in range( len( new_data ) ) ]
        for new_idx, candidates in enumerate( matches ):
            for old_idx in candidates:
                distances[ new_idx ].append( self._metric( new_data[ new_idx ], old_data[ old_idx ] ) )
                
        return distances


def toAjaMatrix( old_data, new_data, matches, distances ):
    """ We're only interested in the Old->New label propagation. There could be new detections,
        or some priors could be occluded.
        This could possibly be represented as a "sparse matrix" with
        lockstep Adjacency lists of weights and old indexs
    """
    dm = np.full( (new_data.shape[0], old_data.shape[0]), -1.0, dtype=np.float32 )
    for new_idx in range( new_data.shape[0] ):
        for old_idx, dist in zip( matches[new_idx], distances[new_idx] ):
            dm[new_idx,old_idx] = dist

    return np.asarray( dm, dtype=np.float32 )


def assignMinMatrix( dist_mat, threshold ):
    """
    Assignment
    We want to make the best assignment of an old idx's label to a new one.
    There could be "new" data, or some old points could disappear,
    so a 'perfect' solution is not realistic.  We want the least worst.

    """
    def argminPos( arr ):
        """ argmin, except it ignores negative numbers """
        lowest = 0xffffffff
        winner = None
        for i, val in enumerate( arr ):
            if( val >=0 ):
                if( val < lowest ):
                    lowest = val
                    winner = i
        return winner

    def idxsPos( arr ):
        """ We'd get this for free with a sparse representation """
        ret = []
        for idx, val in enumerate( arr ):
            if( val >= 0 ):
                ret.append( idx )

        return ret
    #
    num_new = len( dist_mat )

    #print( dist_mat )

    NONE = -1
    UNLABLED = -2
    threshold2 = threshold * 2

    new2old = [ NONE for _ in range( num_new ) ]
    old2new = [ NONE for _ in range( num_new ) ]  # reverse lut
    lowest_score = [ NONE for _ in range( num_new ) ]

    for new_idx, weigth_row in enumerate( dist_mat ):
        # initalize with just the cheapest edge, 99.8% of the time this is all that's needed
        low_idx = argminPos( weigth_row )
        if( low_idx is None ):
            # No min value found, not even a high one
            continue

        lowest_score[ new_idx ] = dist_mat[ new_idx, low_idx ]

        # if it's over the threashold distance, unlabel, maybe we can pick up a better candidate in the backtracking
        if (lowest_score[ new_idx ] > threshold):
            lowest_score[ new_idx ], new2old[ new_idx ] = threshold, NONE
            continue

        # see if this supersedes a previous labelling
        previous_mapping = old2new[ low_idx ]
        if (previous_mapping == NONE):
            # discovered this round
            old2new[ low_idx ], new2old[ new_idx ] = new_idx, low_idx

        elif (lowest_score[ previous_mapping ] > lowest_score[ new_idx ]):
            # if old2new had a previous mapping, but this is better, supercede, and mark the old mapping unassigned
            old2new[ low_idx ], new2old[ new_idx ] = new_idx, low_idx
            new2old[ previous_mapping ] = UNLABLED

        else:
            new2old[ new_idx ] = UNLABLED

    # So now all we have to do (ha ha) is resolve when labels have been stolen
    # this is an over simplification of Bellman Ford min-cost max-flow.  we only look for one
    # optimal reassignment.
    for c_idx in range( num_new ):
        if( new2old[ c_idx ] >= 0 ):
            # A presumably good assignment (though it might get changed in backtracking)
            continue

        prefered = argminPos( dist_mat[ c_idx ] )
        candidates = idxsPos( dist_mat[ c_idx ] )
        try:
            backlink = new2old.index( prefered ) # TODO: ??? What if not in list
        except ValueError:
            print( "{} not found".format( prefered ) )
            continue

        old_assign = new2old[ backlink ]

        print( "\n{} prefers {} from {}".format( c_idx, prefered, candidates ) )

        # penalize the backlink
        lowest_score[ backlink ] += threshold
        new2old[ backlink ] = -2

        # look for an alternate path from the "theif" that took our proffered assignment
        altpaths = idxsPos( dist_mat[ backlink ] )
        scores = dist_mat[ backlink ][ altpaths ]
        preference = np.argsort( scores )

        remap = False
        for order in preference:
            path = altpaths[ order ]
            if (path == prefered):
                # this is the de-linked path
                continue

            else:
                path_cost = dist_mat[ backlink ][ path ]

                print( "{} would cost {}, for a saving of {} over {:.2f}".format(
                    path, path_cost, dist_mat[ c_idx ][ prefered ], lowest_score[ backlink ] )
                )

                if( (path_cost > threshold2) or (lowest_score[ backlink ] < dist_mat[ c_idx ][ prefered ]) ):
                    # clamp out absurd distances
                    continue

                if( path_cost < lowest_score[ backlink ] ):
                    # An optimal sub-optimal path has been found
                    if( new2old[ path ] >= 0 ):
                        print( "reassignment would steal" )

                    new2old[ backlink ], lowest_score[ backlink ] = path, path_cost
                    remap = True

        if( remap ):
            # a remap has taken place, try to assign c_idx 1st preference
            if( new2old[ c_idx ] < 0 ):
                # prefered is still available, so take it
                new2old[ c_idx ], lowest_score[ c_idx ] = prefered, dist_mat[ c_idx ][ prefered ]

        else:
            # restore the old state if a suitable remap hasn't been found
            new2old[ backlink ], lowest_score[ backlink ] = old_assign, dist_mat[ backlink ][ old_assign ]

    return new2old


class HashPipe( object ):
    """ A dubiously named system where you configure a hashing engine, then push new detections
        through it, on each push it will hash, bin, match, measure, and then assign the old lables
        to the new data, cacheing some results for the next "push"
    """
    PRED_MODE_VELO = "VELO"
    PRED_MODE_PRIOR = "PRIOR"
    VELO_ORDER_FIRST = "FIRST"
    VELO_ORDER_SECOND = "SECOND"

    def __init__( self, bins=32, dims=(1920,1080), pattern="BOTTOM_HALF" ):
        self.hasher = Hash2DObj( bins, dims )
        self.hasher.setSearchPattern( pattern )

        self.px_dist = self.hasher.half_cell_dims
        self.threshold = ( self.hasher.half_cell_dims[0]**2 + self.hasher.half_cell_dims[1]**2 ) + 4
        #print( self.px_dist, self.threshold )

        self.current_data = None
        self.prev_data = None

        self.current_bin = None
        self.prev_bin = None

        self.current_velo = None
        self.prev_velo = None

        self.assignment = None
        self.labels = None
        self.prev_labels = None
        self.predictions = None

        self.matching_mode = self.PRED_MODE_VELO
        self.velo_order = self.VELO_ORDER_SECOND

        self.last_label = None

    def push( self, new_data ):
        """ Attempt to assign previous labels to the new data """
        self.prev_data = self.current_data
        self.prev_bin = self.current_bin
        self.prev_velo = self.current_velo
        self.prev_labels = self.labels

        self.current_data = deepcopy( new_data  )
        self.current_bin = self.hasher.binIt( self.hasher.hashIt( self.current_data ) )

        self.current_velo = np.zeros( (len( new_data), 2), dtype=np.float32 )

        # 1st run, there are no priors
        if( self.prev_bin is not None ):
            # create distance matrix

            if( self.current_velo is None or self.matching_mode == self.PRED_MODE_PRIOR ):
                # match mode: Offset Priors
                matches = self.hasher.matchIt( self.prev_bin, self.current_data, px_dist=self.px_dist )
                M = self.hasher.measureIt( matches, self.prev_data, self.current_data )
                dist_mat = toAjaMatrix( self.prev_data, self.current_data, matches, M )

            elif( self.matching_mode == self.PRED_MODE_VELO):
                # match mode: Velocity prediction
                velo_bin = self.hasher.binIt( self.hasher.hashIt( self.predictions ) )
                matches = self.hasher.matchIt( velo_bin, self.current_data, px_dist=0 )
                M = self.hasher.measureIt( matches, self.predictions, self.current_data )
                dist_mat = toAjaMatrix( self.predictions, self.current_data, matches, M )

            # run assignment
            self.assignment = assignMinMatrix( dist_mat, self.threshold )

            # update Labels
            new_labels = [ -1 for _ in range( len( self.assignment ) ) ]
            for i, assign in enumerate( self.assignment ):
                if( assign >= 0 ):
                    new_labels[ i ] = self.labels[ assign ]
                    if( self.prev_data is not None ):
                        # calculate Velocity
                        self.current_velo[assign] = self.current_data[i] - self.prev_data[ assign ]

                else:
                    # Give a tracking ID to new Labels
                    new_labels[ i ] = self.last_label
                    self.last_label += 1

            self.labels = new_labels

        else:
            # first run, give "priming" dets an arbitrary ID
            self.last_label = len( self.current_data ) + 1
            self.labels = [ i for i in range( 1, self.last_label ) ]

        print( "labels", self.labels )
        self.predict()
        return self.assignment


    def predict( self ):
        """ Once we have built up some priors we could use a Kalman filter to predict the tracked detections.
            No don't it's a sledge hammer to a nut.
        """
        if( self.prev_velo is not None and self.velo_order == self.VELO_ORDER_SECOND):
            # can estimate acceleration
            acceleration = self.current_velo - self.prev_velo
            self.predictions = self.current_data + self.current_velo + acceleration

        elif( self.current_velo is not None ):
            # have a velo
            self.predictions = self.current_data + self.current_velo

        else:
            # first run
            self.predictions = self.current_data

        return


if( __name__ == "__main__" ):
    np.set_printoptions( suppress=True, precision=3 )

    A = np.asarray( [ [1, 1], [1,31], [1,32], [1, 510], [1,510], [31,1], [32,1], [510,1], [510,510] ], dtype=np.float32 )
    B = A + 1
    B = np.append( B, [[10,45], [72,72]], axis=0 )
    #B = np.flipud( B )

    cheach = Hash2DObj( 32, (1920,1080) )
    chong  = Hash2DObj( 32, (1024,1024) )

    ha = chong.hashIt( A )
    ba = chong.binIt( ha )

    print( ba )

    print( "matching" )

    matches = chong.matchIt( ba, B, px_dist=chong.half_cell_dims )

    M = chong.measureIt( matches, A, B )

    dist_mat = toAjaMatrix( A, B, matches, M )
    #dist_mat = np.flipud( dist_mat )

    print( dist_mat )

    threshold = np.sqrt( chong.half_cell_dims[0]**2 + chong.half_cell_dims[1]**2 ) + 4

    new2old = assignMinMatrix( dist_mat, threshold )

    print( new2old )

