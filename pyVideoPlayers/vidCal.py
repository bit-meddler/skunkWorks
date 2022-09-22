import logging
log = logging.getLogger( __name__ )

import functools
import os
import sys

from PySide2 import QtWidgets, QtGui, QtCore

import cv2
import numpy as np

from vision import ImgProc
from vidGUI import *


class Viewer( QtWidgets.QGraphicsView ):

    DEFAULT_ZOOM = 1.05 #(5%)

    def __init__( self, parent, scene=None ):
        # manage my own Scene
        self.scene = scene or QtWidgets.QGraphicsScene( parent )

        super( Viewer, self ).__init__( self.scene )
        self._parent = parent

        self.scene.setBackgroundBrush( QtCore.Qt.black )

        # Vars
        self._zoom = 1.0
        self._pan_mode = False
        self._panning = False
        self._pan_start = None

        self.cur_img = None

        self.setTransformationAnchor( self.AnchorUnderMouse )
        self.setFrameStyle( 0 )

        #self.loadImage()

    # overloads
    def wheelEvent( self, event ):
        super( Viewer, self ).wheelEvent( event )

        orig_centre = self.mapToScene(self.viewport().rect().center() )

        wheel_delta = event.angleDelta().y()
        wheel_delta /= 100.

        if( wheel_delta > 0.0 ):
            # Zoomed in
            self._zoom *= self.DEFAULT_ZOOM
        elif( wheel_delta < 0.0 ):
            # zoom out
            self._zoom /= self.DEFAULT_ZOOM

        self._applyScale()

        new_centre = self.mapToScene(self.viewport().rect().center() )
        new_point = self.mapToScene( event.pos() )

        offset = new_centre - orig_centre

        tgt_centre = new_point - offset

        self.centerOn( tgt_centre  )

    def mousePressEvent( self, event ):
        super( Viewer, self).mousePressEvent( event )

        pressed_left = event.button() == LMB
        pressed_right = event.button() == RMB
        pressed_mid = event.button() == MMB

        if pressed_left :
            if( self._pan_mode ):
                self.setCursor( QtCore.Qt.ClosedHandCursor )
                self._panning = True
                self._pan_start = event.pos()

        elif pressed_right :
            if( self._pan_mode ):
                self.setCursor( QtCore.Qt.ClosedHandCursor )
                self._panning = True
                self._pan_start = event.pos()

        elif pressed_mid:
            # this does nothing!
            if (self._pan_mode):
                return

    def mouseReleaseEvent( self, event ):
        super( Viewer, self ).mouseReleaseEvent( event )
        pressed_right = event.button() == RMB
        pressed_left = event.button() == LMB

        if( self._panning and (pressed_left or pressed_right) ):
            self._panning = False
            self.setCursor( QtCore.Qt.OpenHandCursor )

    def mouseMoveEvent( self, event ):
        super( Viewer, self ).mouseMoveEvent( event )
        if( self._panning ):
            self.setCursor( QtCore.Qt.ClosedHandCursor )
            hz = self.horizontalScrollBar().value()
            hz -= event.x() - self._pan_start.x()
            vt = self.verticalScrollBar().value()
            vt -= event.y() - self._pan_start.y()
            self.horizontalScrollBar().setValue( hz )
            self.verticalScrollBar().setValue( vt )
            self._pan_start = event.pos()

    def keyPressEvent( self, event ):
        super( Viewer, self ).keyPressEvent( event )
        key = event.key()
        if( key == QtCore.Qt.Key_Alt ):
            self._pan_mode = True
            self.setCursor( QtCore.Qt.OpenHandCursor )

        elif( key == QtCore.Qt.Key_F ):
            self._fit2Scene()

    def keyReleaseEvent( self, event ):
        super( Viewer, self ).keyReleaseEvent( event )
        key = event.key()
        if( key == QtCore.Qt.Key_Alt ):
            self.setCursor( QtCore.Qt.ArrowCursor )
            self._pan_mode = False

    # internals
    def img2nda( self ):
        if( self.cur_img is None ):
            return

        pixmap = self.cur_img.pixmap()
        size = pixmap.size()
        h = size.width()
        w = size.height()

        qimg = pixmap.toImage()
        byte_str = qimg.bits().tobytes()

        img = np.frombuffer( byte_str, dtype=np.uint8 ).reshape( (w,h,-1) )

        return img

    def loadImage( self, path=r"cardK.png" ):
        if( self.cur_img is not None ):
            self.scene.removeItem( self.cur_img )
        self.scene.clear()

        pix_map = QtGui.QPixmap( path )
        self.cur_img = QtWidgets.QGraphicsPixmapItem( pix_map )

        self.scene.addItem( self.cur_img )
        self._sizeScene()
        self._fit2Scene()

    def _sizeScene( self ):
        # reset scene rect
        pm = self.cur_img.pixmap()
        biggest = max( pm.width(), pm.height() )
        #biggest *= 1.5
        self.scene.setSceneRect( 0, 0, int(biggest), int(biggest) )

    def attachBuffer( self, nd_buffer ):
        """ Take the ndarray as an RGB Buffer, make it a pixmap, and place in scece.
            Theoretically would be nice not to have to clear and remake the item
        """

        if( nd_buffer is None ):
            return

        if( self.cur_img is not None ):
            self.scene.removeItem( self.cur_img )
        
        h, w, ch = nd_buffer.shape

        qimg = QtGui.QImage( nd_buffer.data, w, h, ch*w, QtGui.QImage.Format_RGB888 ) 
        pix_map = QtGui.QPixmap( qimg )

        self.cur_img = QtWidgets.QGraphicsPixmapItem( pix_map )
        self.scene.addItem( self.cur_img )

    def _fit2Scene( self ):
        self._resetZoom()
        self.resetTransform()
        self.centerOn( self.sceneRect().center() )
        space_avail = self.frameRect()
        space_request = self.sceneRect()
        PAD = 8

        # try fit to width
        scale = float( space_avail.width() ) / (space_request.width() + PAD)
        scaled_height = space_request.height() * scale
        if( scaled_height > space_avail.height() ):
            # scale by height instead
            scale = float( space_avail.height() ) / (space_request.height() + PAD)

        self._zoom = scale

        self._applyScale()

    def _resetZoom( self ):
        self._zoom = 1.0
        self._applyScale()

    def _applyScale( self ):
        new_mat = QtGui.QTransform().scale( self._zoom, self._zoom )
        self.setTransform( new_mat )


class Player( QtWidgets.QMainWindow ):
    
    TITLE_FMT = "Rich's OpenCV Video Player {save_flag}[{title}]"
    DEFAULT_PATH = r"C:\code\exampleData"
    FACE_DRAW_STYLES = [ "Landmarks", "Face Mesh" ]


    def __init__(self, parent=None):
        super( Player, self ).__init__( parent )

        # Internals
        self.video_title = ""
        self.needs_save = False        
        self._current_file = None

        self._video_meta   = {}

        # OpenCV Video
        self._device = None
        self._current_frame_data = None

        # position in video
        self._frame_last = None
        self._frame_current = None
        self._frame_next = None

        # CV
        self.chess_dims = ( 15, 10 ) # dXYZ 15*10
        self.chess_criteria = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001 )
        self._mask_exclude = ImgProc.Excluder()

        # Build UI
        self._buildUI()
        
    def _setTitle( self ):
        flag = "*" if self.needs_save else ""
        self.setWindowTitle( self.TITLE_FMT.format( save_flag=flag, title=self.video_title ) )

    def _buildUI( self ):
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        # Video Canvas
        self._canvas = Viewer( self )

        palette = self._canvas.palette()
        palette.setColor( QtGui.QPalette.Window, QtGui.QColor(0, 0, 0) )
        self._canvas.setPalette( palette )
        self._canvas.setAutoFillBackground( True )
        

        # Timeline
        self.timeline = QTimeline( self )


        # Computer vision stuffs
        cv_buts = QtWidgets.QHBoxLayout()

        # Detect Chess
        self.but_chess = QtWidgets.QPushButton( "Detect" )
        cv_buts.addWidget( self.but_chess )
        
        self.but_track = QtWidgets.QPushButton( "Track Forward" )
        cv_buts.addWidget( self.but_track )

        # Video Layout
        player_paine = QtWidgets.QVBoxLayout()
        player_paine.addWidget( self._canvas )
        player_paine.addWidget( self.timeline )
        player_paine.addLayout( cv_buts )


        # Tools
        tools = QtWidgets.QVBoxLayout()

        # Masking
        mask_buts = QtWidgets.QHBoxLayout()
        self.but_mask_add = QtWidgets.QPushButton( "Add Mask" )
        mask_buts.addWidget( self.but_mask_add )
        self.but_mask_rem = QtWidgets.QPushButton( "Remove Mask" )
        mask_buts.addWidget( self.but_mask_rem )
        tools.addLayout( mask_buts )

        # Mask list
        self.masks = QtWidgets.QTableWidget( self )
        self.masks.setRowCount( 0 )
        self.masks.setColumnCount( 1 )
        self.masks.setHorizontalHeaderLabels( ["Masks"] )
        tools.addWidget( self.masks )


        # Annotations
        self.ano_tree = QtWidgets.QTreeWidget( self )
        self.r_grid = QtWidgets.QTreeWidgetItem( self.ano_tree )
        self.r_grid.setText( 0, "Detected Grids" )
        tools.addWidget( self.ano_tree )


        # Main Layout
        layout = QtWidgets.QHBoxLayout( self.widget )
        layout.addLayout( player_paine )
        layout.addLayout( tools )


        # Menu
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Add actions to file menu
        openv_action = QtWidgets.QAction( "Load Video", self )
        opens_action = QtWidgets.QAction( "Load Image", self )
        close_action = QtWidgets.QAction( "Exit App", self )

        file_menu.addAction( openv_action )
        file_menu.addAction( opens_action )
        file_menu.addSeparator()
        file_menu.addAction( close_action )

        openv_action.triggered.connect( self.vidOpen )
        opens_action.triggered.connect( self.imgOpen )
        close_action.triggered.connect( sys.exit )

        self._setTitle()

        # buttons
        self.but_chess.clicked.connect( self.doChessAnchor )#scanForChess
        self.but_track.clicked.connect( self.scanForChess )

        # Attach timeline to video player
        self.timeline.requestFrame.connect( self.getNextFrame )

    def imgOpen( self ):

        if( self._device is not None ):
            self._device.release()
            self._device = None

        filename, _ = QtWidgets.QFileDialog.getOpenFileName( self, "Open an Image...", self.DEFAULT_PATH )

        if( not filename ):
            return

        self._current_file = filename
        name, ext = os.path.basename( filename ).rsplit( ".", 1 )
        self._file_title = name
        self._file_ext = ext

        self.video_title = name
        self._setTitle()

        self._canvas.loadImage( self._current_file )
        self._current_frame_data = cv2.cvtColor( self._canvas.img2nda(),  cv2.COLOR_RGBA2BGR )

        w, h, ch = self._current_frame_data.shape
        print( '"{}": ({},{})'.format( self.video_title, w, h ) )

    def vidOpen( self ):

        if( self._device is not None ):
            self._device.release()
            self._device = None

        filename, _ = QtWidgets.QFileDialog.getOpenFileName( self, "Open a Video...", self.DEFAULT_PATH )

        if( not filename ):
            return

        self._current_file = filename
        name, ext = os.path.basename( filename ).rsplit( ".", 1 )
        self._file_title = name
        self._file_ext = ext

        self.fileDiagnose()

    def fileDiagnose( self ):
        self._device = cv2.VideoCapture( self._current_file )
        
        self._video_meta = {}
        self._video_meta["WIDTH"]       = self._device.get( cv2.CAP_PROP_FRAME_WIDTH )
        self._video_meta["HEIGHT"]      = self._device.get( cv2.CAP_PROP_FRAME_HEIGHT )
        self._video_meta["FPS"]         = self._device.get( cv2.CAP_PROP_FPS )
        self._video_meta["4CC"]         = self._device.get( cv2.CAP_PROP_FOURCC )
        self._video_meta["NUM_FRAMES"]  = self._device.get( cv2.CAP_PROP_FRAME_COUNT )
        self._video_meta["MAT_FORMAT"]  = self._device.get( cv2.CAP_PROP_FORMAT )
        self._video_meta["MODE"]        = self._device.get( cv2.CAP_PROP_MODE )
        self._video_meta["CONVERT_RGB"] = self._device.get( cv2.CAP_PROP_CONVERT_RGB )

        # returned as floats, some can only be ints
        for cast in ("WIDTH", "HEIGHT", "NUM_FRAMES"):
            self._video_meta[ cast ] = int( self._video_meta[ cast ] )

        # Use this info to setup the timeline
        self.timeline.setDuration( self._video_meta["NUM_FRAMES"] )

        print( "{}: ({}x{}) at {}fps duration: {} frames. mat:{} mode:{} rgb:{}".format(
            self._file_title, self._video_meta["WIDTH"], self._video_meta["HEIGHT"], self._video_meta["FPS"], self._video_meta["NUM_FRAMES"],
            self._video_meta["MAT_FORMAT"], self._video_meta["MODE"], self._video_meta["CONVERT_RGB"] )
        )

        self._frame_last = -1
        self._frame_current = -1
        self._frame_next = int( self._device.get( cv2.CAP_PROP_POS_FRAMES ) )

        self._setTitle()
        self.showNext()
        self._canvas._sizeScene()

    def showNext( self ):
        # get the first frame
        ret, img = self._device.read()

        if( ret ):
            self._current_frame_data = img
            self._frame_current = self._frame_next
            self._frame_next = int( self._device.get( cv2.CAP_PROP_POS_FRAMES ) )

        else:
            print( "Error reading video" )

        # Add to canvas
        self._canvas.attachBuffer( self._current_frame_data )
        
    def getNextFrame( self, next_frame ):
        """ if playing back sequentialy repeated calls will yeild the frames.
            If seeking, we will land on an I-Frame and have to "fast forward" to the target frame
        """
        if( self._device is None ):
            return

        

        if( self._frame_next != next_frame ):
            print( "{} {}".format( self._frame_next, next_frame ) )
            last_state = self.timeline._is_playing

            if( last_state ):
                self.timeline.doStop()

            res = self.seekFrame( next_frame )

            if( last_state ):
                # stop if this is the end anyway?
                if( res ):
                    self.timeline.doPlay()

            return

        # get the next frame, update last next current
        self.showNext()

    def seekFrame( self, new_frame ):
        print( "seeking requested: {}".format( new_frame ) )
        if( (new_frame > self._video_meta["NUM_FRAMES"]) or (new_frame < 0) ):
            return False

        target_frame = new_frame
        res = self._device.set( cv2.CAP_PROP_POS_FRAMES, target_frame )

        self._frame_next = int( self._device.get( cv2.CAP_PROP_POS_FRAMES ) )
        self._frame_last = self._frame_next - 2

        self.showNext()

        return True

    def scanForChess( self ):
        skip_frames = 3 * self.video_rate
        found = 0
        iterations = 0
        start = self.timeline.startSB.value()
        end = self.timeline.finishSB.value() - skip_frames - 5
        print( start, end )
        self._current_frame = start
        res = self.seekFrame( self._current_frame )

        while( found < 10 and iterations < 5 ):
            print( "Scanning {}".format( self._current_frame ) )
            # check for xhess on this frame
            ided, dets = self.doChessAnchor()
            if( dets is not None ):
                #register frame
                found += 1
                item = QtWidgets.QTreeWidgetItem( self.r_grid )
                item.setCheckable( False )
                item.setText( 0, "Frame {: 5>} - {}".format( self._current_frame, "Labelled" if res else "Unlabelled" ) )
                item.setData( 0, (ided, dets) )
                self.ano_tree.update()

            # Skip to next frame to check
            count = 0
            while( count < skip_frames ):
                # maybe faster than seeking?  Certainly riskyer :(
                try:
                    packet = next( self._current_generator )

                except StopIteration:
                    # Generator gave up
                    print( "Blurgh!" )
                    self._container.seek( 0, stream=self._stream )
                    self._current_generator = self._container.demux( video=self.video_stream_index )
                    res = self.seekFrame( self._current_frame - 1)
                    packet = next( self._current_generator )

                for frame in packet.decode():
                    if( type( frame ) == av.VideoFrame ):
                        count += 1
                        self._current_frame += 1
                        self._last_frame += 1

                if( self._current_frame >= end ):
                    break

            # show the skipped to frame
            self._current_frame_data = frame.to_ndarray( format="rgb24" )
            self._current_frame_data.flags.writeable = False
            self._canvas.attachBuffer( self._current_frame_data )

            if( self._current_frame >= end ):
                # If we ran out of frames, loop around again with a little offset
                iterations += 1
                print( iterations )
                self._current_frame = start + iterations + self.video_rate
                res = self.seekFrame( self._current_frame )

    def doChess( self ):
        if( self._current_frame_data is None ):
            return False, None

        # with the current data frame
        # prep the frame
        gray = self.chessPrecondition( self._current_frame_data, [self.PC_GREY] )

        res, inital = cv2.findChessboardCornersSB( gray, self.chess_dims, 0 )

        if( inital is not None ):
            print( "Chessboard found on frame {: 5>} - {}".format( self._current_frame, "Labelled" if res else "Unlabelled" ) )
            corners = cv2.cornerSubPix( gray, inital, (11,11), (-1,-1), self.chess_criteria )
            self._current_frame_data.flags.writeable = True
            cv2.drawChessboardCorners( self._current_frame_data, self.chess_dims, corners, res )
            self._current_frame_data.flags.writeable = False
            self._canvas.attachBuffer( self._current_frame_data )
            self.update()
            return res, corners

        return False, None

    def doChessAnchor( self ):
        if( self._current_frame_data is None ):
            return False, None

        # prep the frame
        gray = ImgProc.chessPrecondition( self._current_frame_data, [ImgProc.PC_GREY, ImgProc.PC_BILIN] )

        res, inital = cv2.findChessboardCornersSB( gray, self.chess_dims, 0 )

        if( inital is not None ):
            print( "Anchor Chessboard found on frame {: 5>} - {}".format( self._current_frame, "Labelled" if res else "Unlabelled" ) )
            return res, corners

        else:
            print( "No Chess found" )

        return False, None

  
def main():
    app = QtWidgets.QApplication( sys.argv )
    app.setStyle( "Fusion" )
    player = Player()
    player.show()
    player.resize (800, 600 )
    sys.exit( app.exec_() )

if __name__ == "__main__":
    main()
