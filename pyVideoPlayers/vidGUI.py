import logging
log = logging.getLogger( __name__ )

from PySide2 import QtWidgets, QtGui, QtCore

# mouse
RMB = QtCore.Qt.RightButton
LMB = QtCore.Qt.LeftButton
MMB = QtCore.Qt.MiddleButton

# Keyboard
MOD_ALT   = QtCore.Qt.AltModifier 
MOD_SHIFT = QtCore.Qt.ShiftModifier

class LnF( object ):

    CLOSE = QtWidgets.QStyle.SP_DockWidgetCloseButton

    WARN = QtWidgets.QStyle.SP_MessageBoxWarning
    CRIT = QtWidgets.QStyle.SP_MessageBoxCritical

    NO   = QtWidgets.QStyle.SP_DialogNoButton  # red dot
    YES  = QtWidgets.QStyle.SP_DialogYesButton # green dot
    HELP = QtWidgets.QStyle.SP_DialogHelpButton
    TICK = QtWidgets.QStyle.SP_DialogApplyButton
    CROS = QtWidgets.QStyle.SP_DialogCancelButton

    DOWN = QtWidgets.QStyle.SP_ArrowDown
    SAVE = QtWidgets.QStyle.SP_DialogSaveButton
    OPEN = QtWidgets.QStyle.SP_DialogOpenButton

    PLAY = QtWidgets.QStyle.SP_MediaPlay
    STOP = QtWidgets.QStyle.SP_MediaStop
    FFWD = QtWidgets.QStyle.SP_MediaSeekForward
    RRWD = QtWidgets.QStyle.SP_MediaSeekBackward
    SKFW = QtWidgets.QStyle.SP_MediaSkipForward
    SKBW = QtWidgets.QStyle.SP_MediaSkipBackward

    INFO = QtWidgets.QStyle.SP_FileDialogInfoView
    DEAT = QtWidgets.QStyle.SP_FileDialogDetailedView
    LIST = QtWidgets.QStyle.SP_FileDialogListView
    
    MAGF = QtWidgets.QStyle.SP_FileDialogContentsView
    BIGX = QtWidgets.QStyle.SP_BrowserStop

    FLDR = QtWidgets.QStyle.SP_DialogOpenButton
    RELD = QtWidgets.QStyle.SP_BrowserReload

    NETD = QtWidgets.QStyle.SP_DriveNetIcon
    FLPD = QtWidgets.QStyle.SP_DriveFDIcon

    @staticmethod
    def getIcon( icon_enum ):
        return QtGui.QIcon( QtWidgets.QApplication.style().standardIcon( icon_enum ) )

    @staticmethod
    def asPixMap( icon_enum, sz ):
        return LnF.getIcon(icon_enum).pixmap( sz )


class QTimeline( QtWidgets.QWidget ):
    # Signals
    # emits the new frame number (int) when frame changes
    requestFrame = QtCore.Signal( int )

    # anounce a rate change. emiting frame period
    rateChanged = QtCore.Signal( float )

    # frame changed, not due to playback
    frameSkipped = QtCore.Signal()

    RATE_DATA = {
    #   Human rate  : rate, divisor, frame period
        "23.976fps" : ( 24, 1.001,   41.708333333333336),
        "24fps"     : ( 24, 1.000,   41.666666666666664),
        "25fps"     : ( 25, 1.000,   40.0),
        "29.97fps"  : ( 30, 1.001,   33.36666666666667 ),
        "30fps"     : ( 30, 1.000,   33.333333333333336),
        "47.952fps" : ( 48, 1.001,   20.854166666666668),
        "48fps"     : ( 48, 1.000,   20.833333333333332),
        "50fps"     : ( 50, 1.000,   20.0),
        "59.94fps"  : ( 60, 1.001,   16.683333333333334),
        "60fps"     : ( 60, 1.000,   16.666666666666668),
    }
    DEFAULT_RATE = "60fps"

    def __init__( self, parent=None ):
        super( QTimeline, self ).__init__( parent )
        self.setObjectName( "QTimeline" )

        # Playing Flag
        self._is_playing = False
        self.loop_play = False

        # timeline defaults
        self._lo = 0
        self._hi = 100
        self._frame = 0

        # frame period
        self._current_rate = self.DEFAULT_RATE
        self._period = int( self.RATE_DATA[ self.DEFAULT_RATE ][2] )

        # frame increment
        self._frameStep = 1

        # Master clock
        self._playTimer = QtCore.QTimer( self )
        self._playTimer.setTimerType( QtCore.Qt.PreciseTimer )
        self._playTimer.timeout.connect( self.doNextFrame )

        self._buildUI()
        self.setDuration( 100 )

    def _buildUI( self ):
        layout = QtWidgets.QGridLayout( self )
        layout.setContentsMargins( 1, 1, 1, 1 )
        layout.setHorizontalSpacing( 2 )
        layout.setVerticalSpacing( 2 )

        # Timebar
        x, y = 0, 0

        # Play Bar
        self.timeslider = QtWidgets.QSlider( self )
        #self.timeslider.setToolTip( "" )
        self.timeslider.setObjectName( "TimeSlider" )
        self.timeslider.setContentsMargins( 2, 2, 2, 2 )
        self.timeslider.setOrientation( QtCore.Qt.Horizontal )
        self.timeslider.setRange( self._lo, self._hi )
        self.timeslider.setValue( 0 )
        self.timeslider.setSizePolicy( QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum )
        layout.addWidget( self.timeslider, y, x, 1, 1, alignment=QtCore.Qt.AlignTop )
        y = 1

        # Spin Boxes
        sub_layout = QtWidgets.QGridLayout()

        self.startSB = QtWidgets.QSpinBox( self )
        self.startSB.setStatusTip( "Start Frame" )
        self.startSB.setButtonSymbols( QtWidgets.QAbstractSpinBox.NoButtons )
        self.startSB.setKeyboardTracking( False )
        sub_layout.addWidget( self.startSB, 0, 0, 1, 1, alignment=QtCore.Qt.AlignLeft )

        self.currentSB = QtWidgets.QSpinBox( self )
        self.currentSB.setStatusTip( "Current Frame" )
        self.currentSB.setButtonSymbols( QtWidgets.QAbstractSpinBox.NoButtons )
        self.currentSB.setKeyboardTracking( False )
        self.currentSB.setWrapping( True )
        sub_layout.addWidget( self.currentSB, 0, 1, 1, 1, alignment=QtCore.Qt.AlignCenter )

        self.finishSB = QtWidgets.QSpinBox( self )
        self.finishSB.setStatusTip( "End Frame" )
        self.finishSB.setButtonSymbols( QtWidgets.QAbstractSpinBox.NoButtons )
        self.finishSB.setKeyboardTracking( False )
        sub_layout.addWidget( self.finishSB, 0, 2, 1, 1, alignment=QtCore.Qt.AlignRight )
        layout.addLayout( sub_layout, y, x, 1, 1, alignment=QtCore.Qt.AlignTop )

        x += 1
        y = 0

        # Transport Controls
        # Two state "Toggle button"
        two_state = QtGui.QIcon()
        two_state.addPixmap( LnF.asPixMap(LnF.PLAY, 32), state=QtGui.QIcon.State.Off )
        two_state.addPixmap( LnF.asPixMap(LnF.STOP, 32), state=QtGui.QIcon.State.On  )
        self.playBut = QtWidgets.QPushButton( two_state, "", parent=self )
        self.playBut.setCheckable( True )

        # The other buttons
        self.saveBut = QtWidgets.QPushButton( LnF.getIcon(LnF.SAVE), "", parent=self )
        self.ffwdBut = QtWidgets.QPushButton( LnF.getIcon(LnF.FFWD), "", parent=self )
        self.rewdBut = QtWidgets.QPushButton( LnF.getIcon(LnF.RRWD), "", parent=self )
        self.jgedBut = QtWidgets.QPushButton( LnF.getIcon(LnF.SKFW), "", parent=self )
        self.jgbgBut = QtWidgets.QPushButton( LnF.getIcon(LnF.SKBW), "", parent=self )

        upper_buts = [ self.jgbgBut, self.playBut, self.jgedBut ]
        lower_buts = [ self.rewdBut, self.saveBut, self.ffwdBut ]

        for i, but in enumerate( upper_buts ):
            layout.addWidget( but, y, x+i, 1, 1 )

        for i, but in enumerate( lower_buts ):
            layout.addWidget( but, y+1, x+i, 1, 1 )        

        x += len( upper_buts )

        # Framerate
        self.rateComboBox = QtWidgets.QComboBox( )
        self.rateComboBox.setStatusTip( "Framerate" )
        self.rateComboBox.addItems( list( self.RATE_DATA.keys() ) )
        self.rateComboBox.setCurrentIndex( self.rateComboBox.findText( self.DEFAULT_RATE ) )
        self.rateComboBox.setObjectName( "RateComboBox" )
        layout.addWidget( self.rateComboBox, y, x, 1, 1 )
        y += 1

        # Loop Play
        self.loop_play = QtWidgets.QCheckBox( "Loop Play", self )
        self.loop_play.setChecked( True )
        layout.addWidget( self.loop_play, y, x, 1, 1 )

        # UI setup
        self.setSizePolicy( QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum )

        # Signals
        self.playBut.clicked.connect( self.doToggle )
        #self.stopBut.clicked.connect( self.doStop )
        self.jgedBut.clicked.connect( self.doEnd )
        self.jgbgBut.clicked.connect( self.doBegin )
        self.ffwdBut.clicked.connect( self.doFwd )
        self.rewdBut.clicked.connect( self.doBwd )

        self.currentSB.valueChanged.connect( self.timeslider.setValue )

        self.rateComboBox.currentIndexChanged.connect( self._cbChangeRate )

        self.timeslider.sliderReleased.connect( self.frameSkipped.emit )
        self.timeslider.valueChanged.connect( self.currentSB.setValue )
        self.timeslider.valueChanged.connect( self.requestFrame )

        # Logic

    # external functions
    def setDuration( self, num_frames ):
        self._hi = num_frames
        self.startSB.setMinimum( self._lo )
        self.startSB.setMaximum( self._hi )
        self.startSB.setValue( self._lo )
        self.currentSB.setMinimum( self._lo )
        self.currentSB.setMaximum( self._hi )
        self.finishSB.setMinimum( self._lo + 1 )
        self.finishSB.setMaximum( self._hi )
        self.finishSB.setValue( self._hi )
        self.timeslider.setRange( self._lo, self._hi )

    # Call backs
    def _triggerFrame( self, frame ):
        self.requestFrame.emit( frame )
        self._frame = frame

    def _cbChangeRate( self, index ):
        self._current_rate = self.rateComboBox.itemText( index )
        self._period = int( self.RATE_DATA[ self._current_rate ][2] )

        if( self._is_playing ):
            self._playTimer.stop()
            self._playTimer.start( self._period )

        self.rateChanged.emit( self._period ) 

    # Transport control buttons
    def doPlay( self ):
        self._is_playing = True
        self._playTimer.start( self._period )

    def doStop( self ):
        self._is_playing = False
        self._playTimer.stop()

    def doToggle( self ):
        if( self._is_playing ):
            self._playTimer.stop()

        else:
            self._playTimer.start( self._period )

        self._is_playing = not self._is_playing

    def doNextFrame( self, delta=1 ):
        frame = self.timeslider.value() + delta
        max_f = self.timeslider.maximum()

        if( frame >= max_f ):
            if( self.loop_play.isChecked() ):
                frame = self.timeslider.minimum()
            else:
                self.doStop()

        self.timeslider.setValue( frame )

    def doFwd( self ):
        frames = self.RATE_DATA[ self._current_rate ][0]
        self.doNextFrame( delta=frames )
        self.frameSkipped.emit()

    def doBwd( self ):
        frames = self.RATE_DATA[ self._current_rate ][0] * -1
        self.doNextFrame( delta=frames )
        self.frameSkipped.emit()
        
    def doBegin( self ):
        self.timeslider.setValue( self._lo )
        self.frameSkipped.emit()

    def doEnd( self ):
        self.timeslider.setValue( self._hi )
        self.frameSkipped.emit()


POS_CHANGE = QtWidgets.QGraphicsItem.ItemPositionChange
POS_HAS_CHANGED = QtWidgets.QGraphicsItem.ItemPositionHasChanged

class Communicate( QtCore.QObject ):
    moving = QtCore.Signal( QtCore.QPointF )

class PathHandle( QtWidgets.QGraphicsEllipseItem ):

    DEF_HIGHLIGHT = QtCore.Qt.yellow
    
    def __init__( self, path, index, colour=QtCore.Qt.green, rad=5, thick=1.3 ):
        super( PathHandle, self ).__init__( -rad, -rad, 2*rad, 2*rad )
        
        self.setAcceptHoverEvents( True )
        self.thickness = thick
        self.highlight = self.DEF_HIGHLIGHT
        self.colour = colour
        self.updateDrawing()
        self.path = path
        self.index = index
        self.movable = False
        self.touched = False
        
        self.coms = Communicate()

        self.setZValue( 1 ) # above the path

        self.setFlag( QtWidgets.QGraphicsItem.ItemIsMovable )
        self.setFlag( QtWidgets.QGraphicsItem.ItemSendsGeometryChanges )
        
    def setColour( self, colour ):
        self.colour = colour
        self.updateDrawing()
        
    def setHighlight( self, colour ):
        self.highlight = colour
        
    def updateDrawing( self, colour=None ):
        colour = colour or self.colour
        self.setPen( QtGui.QPen( colour, self.thickness, QtCore.Qt.SolidLine ) )
    
    # Overloads
    def itemChange( self, change, value ):
        if( change == POS_HAS_CHANGED and self.movable ):
            self.path.updateElement( self.index, value )
            if( self.touched ):
                # Human directed motion, emit event
                self.coms.moving.emit( value )

        return QtWidgets.QGraphicsEllipseItem.itemChange( self, change, value) 

    def hoverEnterEvent( self, event ):
        self.updateDrawing( self.highlight )
        super( PathHandle, self ).hoverEnterEvent( event )

    def hoverLeaveEvent( self, event ):
        self.updateDrawing()
        super( PathHandle, self ).hoverLeaveEvent( event )

    def mousePressEvent( self, event ):
        if( event.button() == LMB ):
            self.touched = True
            self.path.hideLine( True )

        super( PathHandle, self).mousePressEvent( event )

    def mouseReleaseEvent( self, event ):
        if( event.button() == LMB ):
            self.touched = False
            self.path.hideLine( False )

        super( PathHandle, self ).mouseReleaseEvent( event )


class OpenPath( QtWidgets.QGraphicsPathItem ):
    
    SZ = 1.75
    LINE_SOLID = QtCore.Qt.SolidLine
    LINE_DASH  = QtCore.Qt.DashLine
    LINE_DOTS  = QtCore.Qt.DotLine
    LINE_NONE  = QtCore.Qt.NoPen
    
    def __init__( self, path, scene, colour=QtCore.Qt.black, receiver=None ):
        super( OpenPath, self ).__init__( path )
        self.colour = colour
        self.line_style = self.LINE_SOLID
        self.can_hide = False
        
        num_cvs = path.elementCount()
        self._handles = {}
        
        for i in range( num_cvs ):
            handle = PathHandle( self, i )
            handle.setPos( QtCore.QPointF( path.elementAt( i ) ) )
            scene.addItem( handle )
            self._handles[ i ] = handle
            if( receiver is not None ):
                handle.coms.moving.connect( receiver )

        for i in range( num_cvs ):
            self._handles[ i ].movable = True

        self.setPen( QtGui.QPen( self.colour, self.SZ, self.line_style ) )

        #self.setFlag( QtWidgets.QGraphicsItem.ItemIsSelectable, True )
        #self.setFlag( QtWidgets.QGraphicsItem.ItemIsMovable, True )
        self.setFlag( QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True )
        
    def hideLine( self, state ):
        if( not self.can_hide ):
            return

        if( state ):
            self.setStyle( OpenPath.LINE_NONE )
        else:
            self.setStyle( self.line_style )

    def setColour( self, colour ):
        self.colour = colour
        self.setPen( QtGui.QPen( self.colour, self.SZ, self.line_style ) )
        
    def setStyle( self, style ):
        self.setPen( QtGui.QPen( self.colour, self.SZ, style ) )
        
    def updateElement( self, index, pos ):
        path = self.path()           
        path.setElementPositionAt( index, pos.x(), pos.y() )
        self.setPath( path )

    def reportCVs( self ):
        path = self.path()
        ret = ""
        for i in range( path.elementCount() ):
            el = path.elementAt( i )
            ret += "({},{}) ".format( el.x, el.y )
        print( ret )

    def styleHandles( self, colour=None, thick=None ):
        for hand in self._handles.values():
            if( colour is not None ):
                hand.colour = colour
                
            if( thick is not None ):
                hand.thickness = thick

            hand.updateDrawing()

    def shape( self ):
        qp = QtGui.QPainterPathStroker()
        qp.setWidth( 10 )
        qp.setCapStyle( QtCore.Qt.SquareCap )
        shape = qp.createStroke( self.path() )
        return shape

    def itemChange( self, change, value ):
        if( change == POS_CHANGE and self.isSelected() ):
            # update Handles with new positions
            path = self.path()
            for i in range( path.elementCount() ):
                hand = self._handles[ i ]
                hand.movable = False
                hand.setPos( QtCore.QPointF( path.elementAt( i ) ) + value )
                hand.movable = True
                hand.update()

        return super( OpenPath, self ).itemChange( change, value )

            
class ClosedPath( OpenPath ):

    def __init__( self, path, scene, colour=QtCore.Qt.black, receiver=None ):
        num_cvs = path.elementCount()
        self._roots = { 0 : num_cvs-1, num_cvs-1 : 0 }
        super( ClosedPath, self ).__init__( path, scene, colour, receiver )
        
    def updateElement( self, index, pos ):
        """ Overload to move 1st and last handles at once """
        path = self.path()
        if( index in self._roots ):
            # get the "other" node if this is the root
            other_idx = self._roots[ index ]
            other = self._handles[ other_idx ]
            # Update path
            path.setElementPositionAt( other_idx, pos.x(), pos.y() )
            # Update Handle
            other.movable = False
            other.setPos( pos )
            other.movable = True
            
        path.setElementPositionAt( index, pos.x(), pos.y() )
        self.setPath( path )

    def setFillAlpha( self, alpha=0 ):
        col = QtGui.QColor( self.colour )
        col.setAlpha( alpha )
        self.setBrush( QtGui.QBrush( col ) )
