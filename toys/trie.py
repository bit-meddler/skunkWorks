# Trie experiments

class TrieNode( object ):
    
    def __init__( self, letter, parent ):
        self.children = {}
        self.parent = None
        self.letter = letter
        self.is_word = False

    def iterChildren( self ):
        for letter in sorted( self.children ):
            yield self.children[ letter ]

    def __contains__( self, letter ):
        return bool(letter in self.children)


class Trie( object ):
    
    def __init__( self ):
        self.root = TrieNode( None, None )
        self.num_words = 0

    def add( self, word ):
        current_node = self.root
        for letter in word.lower():
            if( letter in current_node ):
                current_node = current_node.children[ letter ]

            else:
                current_node.children[ letter ] = TrieNode( letter, current_node )
                current_node = current_node.children[ letter ]
            
        current_node.is_word = True
        self.num_words += 1
            
    def list( self ):
        word_list = []

        self._dfsList( self.root, "", word_list )

        return word_list

    def _dfsList( self, node, prefix, word_list ):
        for child in node.iterChildren():
            if( child.is_word ):
                word_list.append( prefix + child.letter )

            prefix += child.letter
            self._dfsList( child, prefix, word_list )
            prefix = prefix[:-1]
            
    def iter( self ):
        yield from self._dfsIt( self.root, "" )
        
    def _dfsIt( self, node, prefix ):
        for child in node.iterChildren():
            if( child.is_word ):
                yield prefix + child.letter

            prefix += child.letter
            yield from self._dfsIt( child, prefix )
            prefix = prefix[:-1]

    def hasPrefix( self, prefix ):
        current_node = self.root
        for letter in prefix.lower():
            if( letter in current_node ):
                current_node = current_node.children[ letter ]

            else:
                return False

        return True
    
    def isWord( self, word ):
        current_node = self.root
        for letter in word.lower():
            if( letter in current_node ):
                current_node = current_node.children[ letter ]

            else:
                return False
            
        if( current_node.is_word ):
            return True
        
        return False
    
    def prefixIter( self, prefix ):
        # navigate to begining for prefix tree
        current_node = self.root
        for letter in prefix.lower():
            if( letter in current_node ):
                current_node = current_node.children[ letter ]

            else:
                return # no prefix available
             
        yield from self._dfsIt( current_node, prefix )


w_list = ("and", "ant", "cat", "cab", "a", "andy", "android", "anthony")
X = Trie()

for word in w_list:
    X.add( word )

for word in ("an", "c", "ca", "no", "can"):
    print( word, X.hasPrefix( word ) )

for possible in X.prefixIter( "ca" ):
    print( possible )

for possible in ( "a", "an", "and" ):
    print( possible, list( X.prefixIter( possible ) ), X.isWord( possible ) )

for possible in X.prefixIter( "no" ):
    print( possible )
