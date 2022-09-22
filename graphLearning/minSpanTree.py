# Minimize edge cost to capture sub-tree, for V Verts, V-1 Edges
# Prim - Greedy
# Kruskal - Greedy, uses DSU for cycle detection

from queue import PriorityQueue


class DSU( object ):

    ROOT = -1

    def __init__( self, num_nodes ):
        self.num_nodes = num_nodes
        self.parents   = [ self.ROOT for i in range(self.num_nodes) ]
        self.ranks     = [ 1 for i in range(self.num_nodes) ]

    def make_union( self, u, v ):
        p_u = self.find_leader( u )
        p_v = self.find_leader( v )

        if( (p_v != p_u) or (p_u == self.ROOT) ):
            r_u = self.ranks[ p_u ]
            r_v = self.ranks[ p_v ]

            if( r_u < r_v ):
                self.parents[ p_u ] = p_v
                self.ranks[ p_v ] += r_u

            else:
                self.parents[ p_v ] = p_u
                self.ranks[ p_u ] += r_v

            return True

        return False

    def find_leader( self, node ):
        parent = self.parents[ node ]

        if( parent == self.ROOT ):
            return node

        grandparent = self.find_leader( parent )
        self.parents[ node ] = grandparent
        return grandparent

    def optimizePaths( self ):
        for i in range( self.num_nodes ):
            _ = self.find_leader(i)

        print( self.parents )


class GraphPrim( object ):

    def __init__( self, num_nodes ):
        self.num_nodes = num_nodes
        self.adj_list  = [ [] for i in range( self.num_nodes ) ]

    def addEdge( self, source, target, weight, is_directed=False ):
        self.adj_list[source].append( [target, weight] )
        if( not is_directed ):
            self.adj_list[target].append( [source, weight] )

    def printGraph( self ):
        for i, edges in enumerate( self.adj_list ):
            print( "{} -> {}".format( i, ", ".join([ f"{t} @ {w}" for t,w in edges ]) ) )

    def prim( self, source ):
        # Calculate MST using Prim's method

        active_edges = PriorityQueue() # [(w,t)]
        visited = [ False for _ in range( self.num_nodes ) ]
        min_span = []
        total = 0

        active_edges.put( (0, source) ) # min weight forces source node to be inspected first

        while( not active_edges.empty() ):
            weight, target = active_edges.get()

            if( visited[ target ]):
                continue

            total += weight
            visited[ target ] = True
            min_span.append( target )

            # queue the target's Edges
            for n_target, n_weight in self.adj_list[ target ]:
                active_edges.put( (n_weight, n_target) )

        print( min_span )
        return total


class GraphKruskal( object ):

    def __init__( self, num_nodes ):
        self.num_nodes = num_nodes
        self.edge_list  = []

    def addEdge( self, source, target, weight ):
        # Undirected
        self.edge_list.append( [weight, source, target] )

    def printGraph( self ):
        for weight, source, target in self.edge_list:
            print( "{} -> {} @ {}".format( source, target, weight ) )

    def kruskal( self ):
        edges = sorted( self.edge_list )

        dsu_sets = DSU( self.num_nodes )

        total = 0
        nodes = []
        for edge in edges:
            weight, source, target = edge
            if( dsu_sets.make_union( source, target ) ):
                total += weight
                nodes.append( (source, target) )

        print( nodes )

        return total


if( __name__ == '__main__' ):
    g = GraphPrim(4)

    g.addEdge( 0, 1, 1 )
    g.addEdge( 0, 3, 2 )
    g.addEdge( 0, 2, 2 )
    g.addEdge( 1, 2, 2 )
    g.addEdge( 1, 3, 2 )
    g.addEdge( 3, 2, 3 )

    g.printGraph()

    print( g.prim(0) )


    g = GraphKruskal(10)

    g.addEdge( 1, 2, 10 )
    g.addEdge( 1, 3, 12 )
    g.addEdge( 2, 3,  9 )
    g.addEdge( 2, 4,  8 )
    g.addEdge( 3, 5,  3 )
    g.addEdge( 3, 6,  1 )
    g.addEdge( 4, 5,  7 )
    g.addEdge( 4, 7,  8 )
    g.addEdge( 4, 8,  5 )
    g.addEdge( 5, 6,  3 )
    g.addEdge( 6, 4, 10 )
    g.addEdge( 6, 8,  6 )
    g.addEdge( 7, 8,  9 )
    g.addEdge( 7, 9,  2 )
    g.addEdge( 8, 9, 11 )
    g.printGraph()

    print( g.kruskal() )