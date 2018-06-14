from Tkinter import *
import ttk

from random import randint
import math


class HindingScroller( ttk.Scrollbar ):
    def set( self, min, max ):
        f_min = float( min )
        f_max = float( max )
        if( (f_min <= 0.) and (f_max >= 1.) ):
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set( self, min, max )


class ZoomingCanvas( ttk.Frame ):

    def __init__( self, owner ):
        ttk.Frame.__init__( self, master=owner )

        # the Canvas
        self.canvas = Canvas( self.master )
        self.canvas.grid( row=0, column=0, sticky='nswe' )
        self.canvas.update()
        
        # Vertical and horizontal scrollbars for canvas
        self.vbar = HindingScroller( self.master, orient='vertical' )
        self.hbar = HindingScroller( self.master, orient='horizontal' )
        self.vbar.grid( row=0, column=1, sticky='ns' )
        self.hbar.grid( row=1, column=0, sticky='ew' )
       
        self.vbar.configure( command=self._scrollY )
        self.hbar.configure( command=self._scrollX )

        self.master.rowconfigure( 0, weight=1 )
        self.master.columnconfigure( 0, weight=1 )

        # attach scrollbars
        self.canvas.configure(  xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set )

        # Navigation events 
        self.canvas.bind( '<Button-2>',        self._moveStart  )
        self.canvas.bind( '<B2-Motion>',       self._moveIng )
        self.canvas.bind( '<MouseWheel>',      self._wheelJog )
        self.canvas.bind( 'i', self._zoomIn )
        self.canvas.bind( 'o', self._zoomOut )
        self.canvas.bind( "<Double-Button-2>", self._resetZoom )
        
        # Zoom control
        self._z_delta = 1.2
        self._curr_scale = 1.0
        self.zoom_depth = 0
        self.canvas.configure( scrollregion=self.canvas.bbox('all') )
        self._lastClick = (None, None)


    def _scrollY( self, *args, **kwargs ):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview( *args, **kwargs )  # scroll vertically
        

    def _scrollX( self, *args, **kwargs ):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview( *args, **kwargs )  # scroll horizontally
        
        
    def _moveStart( self, event ):
        ''' Remember previous coordinates for scrolling with the mouse '''
        x, y = event.x, event.y       
        self.canvas.scan_mark( x, y )
        self._last_click = (x, y)


    def _resetZoom( self, event ):
        print self._curr_scale
        self._curr_scale = 1.0 / self._curr_scale
        self.zoom_depth = 0
        print "DBL"
        self.canvas.scale( 'all', 0, 0, self._curr_scale, self._curr_scale )

        
    def _moveIng( self, event ):
        ''' Drag (move) canvas to the new position '''
        x, y = event.x, event.y
        self.canvas.scan_dragto( x, y, gain=1 )


    def _wheelJog( self, event ):
        ''' Zoom with mouse wheel '''
        print event
        x, y = event.x, event.y
        L_x = self.canvas.canvasx( x )
        L_y = self.canvas.canvasy( y )
        
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if( event.num == 5 or event.delta == -120 ):
            self._zoomIn()
            
        if( event.num == 4 or event.delta == 120 ):
            self._zoomOut()

            
    def _zoomIn( self, event=None ):
        print "in"
        self.zoom_depth += 1
        scale = 1. * self._z_delta #* self.zoom_depth

        self.canvas.scale( 'all', 0, 0, scale, scale )
        self.canvas.configure( scrollregion=self.canvas.bbox( 'all' ) )


    def _zoomOut( self, event=None ):
        self.zoom_depth -= 1
        scale = 1. / self._z_delta #* self.zoom_depth

        self.canvas.scale( 'all', 0, 0, scale, scale )
        self.canvas.configure( scrollregion=self.canvas.bbox( 'all' ) )

        
win = Tk()

SZ=1000

last = None

frame = ZoomingCanvas( win )
canv = frame.canvas
canv.configure( bg="black" )

def _canvCB( e ):
    global last
    X = canv.find_withtag( CURRENT )
    if( last ):
        canv.itemconfig( last, width=0 )
    if( X ):
        canv.itemconfig( X, fill='red', width=2 )
        canv.update_idletasks()
        canv.after( 200 )
        canv.itemconfig( X, fill='blue' )
    last = X

canv.create_rectangle( 0,0,1024,1024, outline="white", fill="", width=1 )
canv.grid( column=0, row=0, sticky="NSEW" )

for i in range( 35 ):
    x, y = randint( 0, SZ-1 ), randint( 0, SZ-1 )
    tag = "i_{}".format( i )
    item = canv.create_oval( x-5, y-5, x+5, y+5, fill="blue", width=0, outline="white", tags=tag )
    

canv.bind( "<Button-1>", _canvCB )

win.mainloop()
