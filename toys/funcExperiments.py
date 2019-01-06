class TestIt( object ):
	def __init__( self ):
		self.myFunc = lambda x: x+1
		self.mutant = self.clsFun
		self.y = 9

	def clsFun( self, x ):
		print x

x = TestIt()
y = TestIt()
y.y = 69

print x.myFunc( 2 )
print "spam"
x.clsFun( 10 )
print "egg"

def newAnon( cls, num ):
	print cls.y
	print num

print "test"

x.clsFun = newAnon
def newAnon( cls, num ):
	print( cls.y )
	print( num + 5 )

print "hfhfh"

y.clsFun = newAnon
x.mutant = newAnon

x.clsFun( x, 20 )
y.clsFun( y, 20 )
x.mutant( x, 30 )
