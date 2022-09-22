import logging
log = logging.getLogger( __name__ )

from copy import deepcopy
import functools
import os
import sys

from PySide2 import QtWidgets, QtGui, QtCore

import cv2
import numpy as np
np.set_printoptions( suppress=True, precision=3 )

from vision import ImgProc
from vidGUI import *
from hashing import *

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

        self.setTransformationAnchor( self.AnchorUnderMouse )
        self.setFrameStyle( 0 )

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
                # Panning
                self.setCursor( QtCore.Qt.ClosedHandCursor )
                self._panning = True
                self._pan_start = event.pos()

            elif( self._parent.but_point_add.isChecked() ):
                self._parent.addPoint( self.mapToScene( event.pos() ) )

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
    def _resetZoom( self ):
        self._zoom = 1.0
        self._applyScale()

    def _applyScale( self ):
        new_mat = QtGui.QTransform().scale( self._zoom, self._zoom )
        self.setTransform( new_mat )


class Player( QtWidgets.QMainWindow ):
    POINT_Z = 10
    PRIOR_Z = 5

    def __init__(self, parent=None):
        super( Player, self ).__init__( parent )
        self.setWindowTitle( "Tracking test Harness" )

        # Points
        self._points = []
        self._priors = []
        self._deltas = []
        self._ofsets = [] # hasher offsets the new points, visualize thsi

        self._point_gfx = {}
        self._proir_gfx = {}
        self._offs_gfx  = {}
        self._point_itm = {}

        # Tracks
        self._track_len = 12
        self._tracks = {}
        self._track_gfx = {}

        # The playing field
        self.dims = [600, 480]

        # The device
        self._hashpipe = HashPipe( 16, dims=self.dims, pattern="8-NEIGHBOURS" )


        # Build UI
        self._buildUI()

        # timer for auto movement
        self._playTimer = QtCore.QTimer( self )
        self._playTimer.setTimerType( QtCore.Qt.PreciseTimer )
        self._playTimer.timeout.connect( self.doAuto )
        self._period = 250
        self._playing = False

    def addPoint( self, p_pos ):
        p_id = len( self._points )
        self._points.append( [p_pos.x(), p_pos.y()] )
        point_idx = len( self._points ) - 1

        # update table
        self.tab_pts.setRowCount( len( self._points ) )
        pi_pos = QtWidgets.QTableWidgetItem( "<{:.2f}, {:.2f}>".format( p_pos.x(), p_pos.y() ) )
        pi_id  = QtWidgets.QTableWidgetItem( "{}".format( p_id ) )
        pi_lab = QtWidgets.QTableWidgetItem( "" )
        pi_pos.setData( QtCore.Qt.UserRole, p_id )
        self.tab_pts.setItem( point_idx, 0, pi_pos )
        self.tab_pts.setItem( point_idx, 1, pi_id )
        self.tab_pts.setItem( point_idx, 2, pi_lab )

        # add to grpahics
        gfx = QtWidgets.QGraphicsEllipseItem( -2, -2, 4, 4 )
        gfx.setPen( QtGui.QPen( QtCore.Qt.white, 2, QtCore.Qt.SolidLine ) )
        gfx.setToolTip( "{}".format( p_id ) )
        self._point_gfx[ p_id ] = gfx
        gfx.setPos( p_pos )
        gfx.setZValue( self.POINT_Z )
        self._canvas.scene.addItem( gfx )
        if( p_id == 0 ):
            r = int( np.sqrt( self._hashpipe.threshold ) )
            gfx2 = QtWidgets.QGraphicsEllipseItem( (-r/2), (-r/2), r, r, parent=gfx )
            gfx2.setPen( QtGui.QPen( QtCore.Qt.yellow, 1, QtCore.Qt.SolidLine ) )
            #gfx2.setPos( 0, 0 )
            gfx2.setZValue( self.POINT_Z )

        # add a prior as well.
        gfx = QtWidgets.QGraphicsEllipseItem( -2, -2, 4, 4 )
        gfx.setPen( QtGui.QPen( QtCore.Qt.blue, 2, QtCore.Qt.SolidLine ) )
        gfx.setToolTip( "Prior {}".format( p_id ) )
        self._proir_gfx[ p_id ] = gfx
        gfx.setPos( p_pos )
        gfx.setZValue( self.PRIOR_Z )
        self._canvas.scene.addItem( gfx )

        # and the offset visualization.
        gfx = QtWidgets.QGraphicsEllipseItem( 0, 0, 5, 5 )
        gfx.setPen( QtGui.QPen( QtCore.Qt.green, 2, QtCore.Qt.SolidLine ) )
        self._offs_gfx[ p_id ] = gfx
        gfx.setPos( p_pos )
        gfx.setZValue( self.PRIOR_Z )
        gfx.setVisible( False )
        self._canvas.scene.addItem( gfx )

        # set this point's delta
        self._deltas.append( np.random.uniform( -12.0, 12.0, size=2 ).tolist() )

        # set up the tracks
        self._tracks[ p_id ] = [ p_pos for _ in range( self._track_len ) ]
        path = QtGui.QPainterPath()
        path.moveTo( p_pos )
        path.lineTo( p_pos  )

        gfx = QtWidgets.QGraphicsPathItem()
        gfx.setPath( path )
        gfx.setPen( QtGui.QPen( QtCore.Qt.darkBlue, 2, QtCore.Qt.DotLine ) )
        gfx.setZValue( self.PRIOR_Z )
        gfx.setVisible( bool( self.chk_tail.isChecked() ) )
        self._canvas.scene.addItem( gfx )
        self._track_gfx[ p_id ] = gfx

    def doAuto( self ):
        if( bool( self.but_auto.isChecked() ) ):
            if( not self._playing ):
                self._playTimer.start( self._period )
                self._playing = True
            self.movePoints()

        else:
            self._playTimer.stop()
            self._playing = False

    def movePoints( self ):
        # backup to the priors list
        self._priors = deepcopy( self._points )

        # Now we're doing some tracking!
        if( self._hashpipe.prev_bin is None ):
            # first run, prime with the current thingy
            _ = self._hashpipe.push( np.asarray( self._points ) )

        for i, (pos, delta) in enumerate( zip( self._points, self._deltas ) ):
            noise = np.random.uniform( -3.0, 3.0, size=2 ).tolist()
            pos[0], pos[1] = pos[0] + delta[0] + noise[0], pos[1] + delta[1] + noise[1]
            # bounce off the walls
            if( pos[0] < 0.0 or pos[1] < 0.0 ):
                self._deltas[i][0] *= -1.0
                self._deltas[i][1] *= -1.0
                pos[0] += delta[0]
                pos[1] += delta[1]

            if (pos[0] > (self.dims[0] - delta[0]) or pos[1] > (self.dims[1] - delta[1])):
                self._deltas[i][0] *= -1.0
                self._deltas[i][1] *= -1.0

        self.updateGfx()
        mapping = self._hashpipe.push( np.asarray( self._points ) )
        for i in range( len( self._points ) ):
            itm = self.tab_pts.item( i, 0 )
            lab = self.tab_pts.item( i, 2 )
            idx = itm.data( QtCore.Qt.UserRole )
            lab.setText( "{}".format( self._hashpipe.labels[idx] ) )

        # TODO:  Do this better
        # update the track of the assigned ID (may be wrong
        for i, id in enumerate( mapping ):
            if( id < 0):
                continue

            pos = self._points[ i ]
            _ = self._tracks[ id ].pop( self._track_len - 1 )
            self._tracks[ id ].insert( 0, QtCore.QPointF( pos[ 0 ], pos[ 1 ] ) )

    def updateGfx( self ):
        for i, (pos, pri, offs) in enumerate( zip( self._points, self._priors, self._hashpipe.hasher._offset_data ) ):
            gfx = self._point_gfx[ i ]
            gfx.setPos( QtCore.QPointF( *pos ) )

            gfx = self._proir_gfx[ i ]
            gfx.setPos( QtCore.QPointF( *pri ) )

            gfx = self._offs_gfx[ i ]
            gfx.setPos( QtCore.QPointF( *offs ) )

            gfx = self._track_gfx[ i ]

            # rebuild the path as QT insists on trying to be cleaver
            path = QtGui.QPainterPath()
            path.moveTo( self._tracks[ i ][0] )
            for t_pos in self._tracks[ i ][1:]:
                path.lineTo( t_pos )
            gfx.setPath( path )

        if( self._hashpipe.matching_mode == HashPipe.PRED_MODE_VELO ):
            for i, pos in enumerate( self._hashpipe.predictions ):
                gfx = self._offs_gfx[ i ]
                gfx.setPos( QtCore.QPointF( *pos ) )


    def _togTail( self ):
        for gfx in self._track_gfx.values():
            gfx.setVisible( bool( self.chk_tail.isChecked() ) )

    def _togOffs( self ):
        for gfx in self._offs_gfx.values():
            gfx.setVisible( bool( self.chk_offs.isChecked() ) )

    def _togGrid( self ):
        self._grid.setVisible( bool( self.chk_grid.isChecked() ) )

    def _onModeChange( self, _txt ):
        mode = str( self.pred_mode.currentText() )
        if( mode == "Ofsset Prior" ):
            self._hashpipe.matching_mode = HashPipe.PRED_MODE_PRIOR

        elif( mode == "Velocity Prediction" ):
            self._hashpipe.matching_mode = HashPipe.PRED_MODE_VELO

    def _onOrderChange( self,  _txt ):
        mode = str( self.pred_order.currentText() )
        if (mode == "First"):
            self._hashpipe.velo_order = HashPipe.VELO_ORDER_FIRST

        elif (mode == "Second"):
            self._hashpipe.velo_order = HashPipe.VELO_ORDER_SECOND

    def _buildUI( self ):
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget( self.widget )

        # Display
        self._canvas = Viewer( self )
        self._canvas.setFixedSize( *self.dims )
        self._canvas.setSceneRect( 0, 0, self.dims[0], self.dims[1] )
        self._canvas.fitInView( 0, 0, self.dims[0], self.dims[1], QtCore.Qt.KeepAspectRatio )

        # the grid
        path = QtGui.QPainterPath()
        h = self._hashpipe.hasher
        for i in range( h.bins + 1 ):
            path.moveTo( i*h.cell_width, 0 )
            path.lineTo( i*h.cell_width, self.dims[1] )
            path.moveTo( 0, i*h.cell_height )
            path.lineTo( self.dims[ 0 ], i*h.cell_height )

        self._grid = QtWidgets.QGraphicsPathItem( path )
        self._grid.setPen( QtGui.QPen( QtCore.Qt.darkGray, 1, QtCore.Qt.DashLine ) )
        self._canvas.scene.addItem( self._grid )

        # Tools
        tools = QtWidgets.QVBoxLayout()

        # Point list
        point_buts = QtWidgets.QHBoxLayout()
        self.but_point_add = QtWidgets.QPushButton( "Add Point(s)" )
        self.but_point_add.setCheckable( True )

        point_buts.addWidget( self.but_point_add )
        self.but_point_rem = QtWidgets.QPushButton( "Remove Point" )
        point_buts.addWidget( self.but_point_rem )
        tools.addLayout( point_buts )

        # Mask list
        self.tab_pts = QtWidgets.QTableWidget( self )
        self.tab_pts.setRowCount( 0 )
        self.tab_pts.setColumnCount( 3 )
        self.tab_pts.setHorizontalHeaderLabels( ["Point", "Index", "Label ID"] )
        self.tab_pts.resizeColumnsToContents()
        self.tab_pts.resizeRowsToContents()
        tools.addWidget( self.tab_pts )

        # Transformations
        xform_buts = QtWidgets.QHBoxLayout()
        self.but_move = QtWidgets.QPushButton( "Move Points" )
        xform_buts.addWidget( self.but_move )

        self.but_auto = QtWidgets.QPushButton( "Animate Points" )
        self.but_auto.setCheckable( True )
        xform_buts.addWidget( self.but_auto )
        tools.addLayout( xform_buts )

        # Options
        opts = QtWidgets.QHBoxLayout()
        lab = QtWidgets.QLabel( "Prediction Mode:", self )
        opts.addWidget( lab )

        self.pred_mode = QtWidgets.QComboBox(self)
        self.pred_mode.addItems( ["Ofsset Prior", "Velocity Prediction"] )
        opts.addWidget( self.pred_mode )

        self.pred_order = QtWidgets.QComboBox(self)
        self.pred_order.addItems( ["First", "Second"] )
        self.pred_order.setCurrentText( "Second" )
        opts.addWidget( self.pred_order )

        tools.addLayout( opts )

        # drawing
        draw_buts = QtWidgets.QHBoxLayout()
        self.chk_offs = QtWidgets.QCheckBox( "Show Prediction" )
        self.chk_offs.setChecked( False )
        draw_buts.addWidget( self.chk_offs )
        self.chk_grid = QtWidgets.QCheckBox( "Show Grid" )
        self.chk_grid.setChecked( False )
        draw_buts.addWidget( self.chk_grid )
        self.chk_tail = QtWidgets.QCheckBox( "Show Trails" )
        self.chk_tail.setChecked( False )
        draw_buts.addWidget( self.chk_tail )

        tools.addLayout( draw_buts )

        # Main Layout
        layout = QtWidgets.QHBoxLayout( self.widget )
        layout.addWidget( self._canvas )
        layout.addLayout( tools )

        # Buttons etc
        self.but_move.clicked.connect( self.movePoints )
        self.but_auto.clicked.connect( self.doAuto )
        self.chk_offs.clicked.connect( self._togOffs )
        self.chk_grid.clicked.connect( self._togGrid )
        self.chk_tail.clicked.connect( self._togTail )

        # other CBs
        self.pred_mode.currentTextChanged.connect( self._onModeChange )
        self.pred_order.currentTextChanged.connect( self._onOrderChange )

        # set the drawing
        self._togOffs()
        self._togGrid()
        self._togTail()
        
        # set prediction Mode
        self._onModeChange( None )
        self._onOrderChange( None )

def main():
    app = QtWidgets.QApplication( sys.argv )
    app.setStyle( "Fusion" )
    player = Player()
    player.show()
    player.resize (800, 600 )
    sys.exit( app.exec_() )

if __name__ == "__main__":
    main()
