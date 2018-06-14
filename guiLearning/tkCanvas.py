from Tkinter import *
from random import randint

win = Tk()

SZ=300

canv = Canvas( win, width=SZ, height=SZ )
canv.pack()

def _canvCB( e ):
    print type( CURRENT ), CURRENT
    if( canv.find_withtag( CURRENT ) ):
        print type( CURRENT ), CURRENT
        canv.itemconfig( CURRENT, fill='blue' )
        canv.update_idletasks()
        canv.after( 300 )
        canv.itemconfig( CURRENT, fill='red' )

for i in range( 35 ):
    x, y = randint( 0, SZ-1 ), randint( 0, SZ-1 )
    canv.create_oval( x-5, y-5, x+5, y+5, fill="red" )

canv.bind( "<Button-1>", _canvCB )

win.mainloop()
