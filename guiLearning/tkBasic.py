import Tkinter as tk
import ttk


win = tk.Tk()

win.title( "CaptureDay Survey" )

tabman = ttk.Notebook( win )

tab_v = ttk.Frame( tabman )
tabman.add( tab_v, text='Vicon' )

tab_g = ttk.Frame( tabman )
tabman.add( tab_g, text='Giant' )

tabman.pack( expand=1, fill="both" )

tv = ttk.Treeview( tab_v, show="tree" )
tv.grid(column=0, row=0)
tv.pack( side="left" )
tv.insert( "", "end", "Takes", text="Takes" )
tv.insert( "", "end", "Cals", text="Calibrations" )
tv.insert( "", "end", "Roms", text="Roms" )
tv.insert( "", "end", "Subjects", text="Subjects" )

rom_img = tk.PhotoImage( file="rom.gif" )
tv.insert( "Roms", "end", "performer1", text="First Performer", image=rom_img )
tv.insert( "Roms", "end", "performer2", text="Second Performer", image=rom_img )
tv.insert( "Roms", "end", "performer3", text="Third Performer", image=rom_img )

for i in range( 12 ):
    txt = "Take_{:0>3}".format( i )
    tv.insert( "Takes", "end", txt, text=txt )

for i in range( 5 ):
    txt = "Subject_{}".format( i )
    tv.insert( "Subjects", "end", txt, text=txt )
    
tv.insert( "Cals", "end", "cal1", text="AM Calibration" )
tv.insert( "Cals", "end", "cal2", text="PM Calibration" )

tree_scroller = ttk.Scrollbar( tab_v, orient="vertical", command=tv.yview )
tree_scroller.pack( side='right', fill='y' )

tv.configure( yscrollcommand=tree_scroller.set )

info = ttk.LabelFrame( tab_v, text="MoCap component Info Panel" )
info.grid( column=1, row=0 )
for i in range( 5 ):
    ttk.Label( info, text="Blar").grid( column=0, row=i, sticky=tk.W )
    
info.pack()

win.mainloop()
