class Node(object):

    def __init__( self, name ):
        self.name = name
        self.neighbors = []

class GraphALN(object):

    def __init__( self, cities ):
        self.nodes = {}

        for city in cities:
            self.nodes[ city ] = Node( city )

    def addEdge(self, source, dest, is_directed=False ):
        self.nodes[ source ].neighbors.append( dest )

        if( not is_directed ):
            self.nodes[ dest ].neighbors.append( source )

    def printGraph( self ):
        for name, node in self.nodes.items():
            print( "{} -> {}".format( name, ", ".join(node.neighbors) ) ) 


if( __name__ == '__main__' ):
    cities = ["Delhi", "London", "Paris", "New York", ]
    g = GraphALN( cities )

    g.addEdge( "Delhi", "London", True )
    g.addEdge( "New York", "London", True )
    g.addEdge( "Delhi", "Paris", True )
    g.addEdge( "Paris", "New York", True )

    g.printGraph()