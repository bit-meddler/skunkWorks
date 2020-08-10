
# libs
from PySide2 import QtGui, QtCore, QtWidgets

import copy
from functools import partial
from glob import glob
import json
import os
import random
import sys
from threading import Lock, Thread
from time import sleep
import uuid

# mouse
RMB = QtCore.Qt.RightButton
LMB = QtCore.Qt.LeftButton
MMB = QtCore.Qt.MiddleButton

# Keyboard
MOD_ALT   = QtCore.Qt.AltModifier 
MOD_SHIFT = QtCore.Qt.ShiftModifier


class MoveHandle( QtWidgets.QGraphicsObject ):

    resizeSignal = QtCore.Signal( QtCore.QPointF )

    HANDLE_SIZE = 5

    SIZE_CURSOR = QtCore.Qt.SizeFDiagCursor
    MOVE_CURSOR = QtCore.Qt.SizeAllCursor
    NORM_CURSOR = QtCore.Qt.ArrowCursor

    def __init__( self, rect=None, colour=None, parent=None, cursor=None ):
        super( MoveHandle, self ).__init__( parent )

        self.setFlag( QtWidgets.QGraphicsItem.ItemIsMovable, True )
        self.setFlag( QtWidgets.QGraphicsItem.ItemIsSelectable, True )
        self.setFlag( QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True )

        self.setAcceptHoverEvents( True )

        self._cursor = cursor or self.SIZE_CURSOR

        self.rect = QtCore.QRectF(0, 0, self.HANDLE_SIZE*2, self.HANDLE_SIZE*2) if rect is None else rect

        self._col = QtGui.QColor( 0, 0, 0 ) if colour is None else colour
        self._col.setAlpha( SizeableRegion.ALPHA_HI_BOARDER )
        self._pen = QtGui.QPen()
        self._pen.setColor( self._col )
        self._pen.setStyle( QtCore.Qt.SolidLine )

    def boundingRect( self ):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setPen( self._pen )
        painter.drawRect( self.rect )

    def itemChange(self, change, value):
        if( change == QtWidgets.QGraphicsItem.ItemPositionChange ):
            if( self.isSelected() ):
                self.resizeSignal.emit( value - self.pos() )
        return value

    def hoverMoveEvent( self,  event ):
        if( event.modifiers() & MOD_ALT ):
            self.setCursor( self._cursor )
        super( MoveHandle, self ).hoverMoveEvent( event )

    def hoverLeaveEvent( self, event ):
        self.setCursor( self.NORM_CURSOR )
        super( MoveHandle, self ).hoverLeaveEvent( event )


class SizeableRegion( QtWidgets.QGraphicsRectItem ):

    SOLID_PATTERN = QtCore.Qt.SolidPattern
    BOARDER_SZ = 2
    ALPHA_HI_BOARDER = 180
    ALPHA_HI_FILL = 100
    ALPHA_LO_BOARDER = 90
    ALPHA_LO_FILL = 45

    BOT_LEFT = QtCore.Qt.AlignLeft   | QtCore.Qt.AlignBottom

    def __init__(self, pos, rect=None, colour=None, parent=None, name="", viewer=None, item=None ):
        self._can_paint = False
        rect = QtCore.QRectF(0, 0, 150, 150) if rect is None else rect
        super( SizeableRegion, self ).__init__( rect, parent )

        self._parent = viewer
        self._item = item

        self.activated = True

        self.setFlag( QtWidgets.QGraphicsItem.ItemIsSelectable, True )
        self.setFlag( QtWidgets.QGraphicsItem.ItemIsMovable, False )
        self.setFlag( QtWidgets.QGraphicsItem.ItemIsFocusable, True )
        self.setFlag( QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True )

        self.setPos( pos - rect.center() )

        self._size_br = MoveHandle( colour=colour, parent=self )
        self._size_tl = MoveHandle( colour=colour, parent=self )
        self._mover   = MoveHandle( colour=colour, parent=self, cursor=MoveHandle.MOVE_CURSOR )

        # Sizers
        handle_width = self._size_br.rect.width() / 2
        handle_offset = QtCore.QPointF( handle_width, handle_width )
        self._size_br.setPos( self.rect().bottomRight() - handle_offset )
        self._size_tl.setPos( self.rect().topLeft() - handle_offset )
        self._size_br.resizeSignal.connect( self.resizeBR )
        self._size_tl.resizeSignal.connect( self.resizeTL )

        self._mover.setPos( rect.center() - handle_offset )
        self._mover.resizeSignal.connect( self.move )

        self._text_bounds = None
        self.name = ""

        self._setName( name )

        self.colour = QtGui.QColor( 0, 0, 0 ) if colour is None else colour

        # drawing
        self.show_label = True

        self._col_boarder = QtGui.QColor( self.colour )
        self._pen = QtGui.QPen()
        self._pen.setWidth( 3 )

        self._col_fill = QtGui.QColor( self.colour )
        self._brush = QtGui.QBrush()
        self._brush.setStyle( self.SOLID_PATTERN )

        self._font_col = QtGui.QColor( 0, 0, 0 )
        self._font_bg = QtGui.QColor( 250, 250, 250 )
        self._font = QtGui.QFont( "Arial", 14 )

        self.qp = QtGui.QPainter()
        self.qp.setFont( self._font )

        # data
        self.traits = set()
        self.tags = set()

        # Done
        self._can_paint = True

    def toString( self ):
        rect = self.rect()
        pos = self.pos()
        data = list( map( int, [ pos.x(), pos.y(), rect.x(), rect.y(), rect.width(), rect.height() ] ) )
        return "{},{}:{},{},{},{}".format( *data )

    @staticmethod
    def prFromString( string_enc ):
        pos, rect = string_enc.split( ":" )
        x, y = pos.split( "," )
        i, j, w, h = rect.split( "," )
        pos = QtCore.QPointF( int( x ), int( y ) )
        rect = QtCore.QRectF( int( i ), int( j ), int( w ), int( h ) )
        return pos, rect

    def paint( self, painter, option, widget=None ):
        if( not self._can_paint ):
            return
        rectF = self.rect()
        rect = rectF.toAlignedRect()

        center = rectF.center()
        cx, cy = int( center.x() ), int( center.y() )

        # set colour
        if( self.activated ):
            self._col_fill.setAlpha( self.ALPHA_HI_FILL )
            self._col_boarder.setAlpha( self.ALPHA_HI_BOARDER )

        else:
            self._col_fill.setAlpha( self.ALPHA_LO_FILL )
            self._col_boarder.setAlpha( self.ALPHA_LO_BOARDER )

        self._pen.setColor( self._col_boarder )
        self._brush.setColor( self._col_fill )

        # paint region
        self._pen.setWidth( self.BOARDER_SZ )
        painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
        painter.setPen( self._pen )
        painter.setBrush( self._brush )

        painter.drawRect( rectF )

        # label
        if (self.show_label):
            self._pen.setColor( self._font_col )
            painter.setPen( self._pen )
            if( self._text_bounds is None ):
                metrics = painter.fontMetrics()
                self._text_bounds = metrics.boundingRect( self.name ).adjusted( 0, 0, 4, 0 )
            text_bg = QtCore.QRect( rect.bottomLeft(), self._text_bounds.size() )
            painter.fillRect( text_bg,  self._font_bg)
            painter.drawText( text_bg, self.name )

        # Done

    def boundingRect( self ):
        rect = self.rect().toAlignedRect()
        if( self._text_bounds is not None ):
            rect.adjust( -MoveHandle.HANDLE_SIZE, -MoveHandle.HANDLE_SIZE, MoveHandle.HANDLE_SIZE, self._text_bounds.height() )
        return rect

    def _setName( self, name ):
        self.name = name
        #metrics = self._font.fontMetrics()
        #self._text_bounds = metrics.boundingRect( self.name ).adjusted( 0, 0, 4, 0 )


    def resizeBR( self, change ):
        self.setRect( self.rect().adjusted( 0, 0, change.x(), change.y() ) )
        self.prepareGeometryChange()
        self.update()
        #self._report()


    def resizeTL( self, change ):
        self.setRect( self.rect().adjusted( change.x(), change.y(), 0, 0 ) )
        self.prepareGeometryChange()
        self.update()
        #self._report()

    def move( self, change ):
        self.setPos( self.pos() + QtCore.QPointF( change.x(), change.y() ) )
        self.prepareGeometryChange()
        self.update()
        #self._report()

    def _report( self ):
        print( self.toString() )

class Viewer( QtWidgets.QGraphicsView ):

    DEFAULT_ZOOM = 1.05 #(5%)

    def __init__( self, scene, main ):
        super( Viewer, self ).__init__( scene, main )
        self._main = main

        # Vars
        self._zoom = 1.0
        self._pan_mode = False
        self._panning = False
        self._pan_start = None

        self.cur_img = None
        self.regions = []
        self._reg_lut = {}
        self._reg_rev = {}

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
        pressed_alt = event.modifiers() & MOD_ALT

        # clicked regions
        under_items = self.scene().items( self.mapToScene( event.pos() ) )

        if pressed_left :
            if( not (pressed_alt or self._pan_mode) ):
                if (self._main.mode == "regions"):
                    # Create Region
                    self._main.createRegion( self.mapToScene( event.pos() ), anno_item=self._main.anos.pending )

            else: # Alt or panning
                if( self._pan_mode ):
                    self.setCursor( QtCore.Qt.ClosedHandCursor )
                    self._panning = True
                    self._pan_start = event.pos()
                else: # Alt mode
                    self._main._clearActivations()
                    for item in under_items:
                        if( type( item ) == MoveHandle ):
                            # Dont re-highlight an underneaith item
                            break
                        if( type( item ) == SizeableRegion ):
                            item.activated = True
                            break # first in the list is on top

        elif pressed_right :
            if( self._pan_mode ):
                self.setCursor( QtCore.Qt.ClosedHandCursor )
                self._panning = True
                self._pan_start = event.pos()
            else:
                if( self._main.mode == "regions" ):
                    self._main.anos.skipPending()

        elif pressed_mid:
            # this does nothing!
            if (self._pan_mode):
                return

            # use Pending as Tag
            active_region = None
            to_find = 1
            if( pressed_alt ):
                # one under mode
                to_find = 2
            found = 0
            for item in under_items:
                if (type( item ) == SizeableRegion):
                    active_region = item
                    found += 1
                if( found == to_find ):
                    self._main._clearActivations()
                    active_region.activated = True
                    break
                    
            if active_region is not None:
                # pop-up tagging menu for the pending tag/trait
                self._main.tagRegion( active_region, self.mapToGlobal( event.pos() ) )

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

        if( key == QtCore.Qt.Key_Space ):
            self._pan_mode = True
            self.setCursor( QtCore.Qt.OpenHandCursor )

    def keyReleaseEvent( self, event ):
        super( Viewer, self ).keyReleaseEvent( event )
        key = event.key()
        if( key == QtCore.Qt.Key_Space ):
            self.setCursor( QtCore.Qt.ArrowCursor )
            self._pan_mode = False

    # internals
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


class CacheMan( Thread ):
    
    def __init__( self, img_table ):
        super( CacheMan, self ).__init__()
        self.deamon = True
        self.running = True
        self.table = img_table

    def halt( self ):
        self.running = False

    def run( self ):
        while( self.running ):
            for i, task in enumerate( list( self.table._cache_stat ) ):
                if( task == "drop" ):
                    self.table._lock_stat.acquire()
                    if( i in self.table._img_cache ):
                        del( self.table._img_cache[ i ] )
                    self.table._cache_stat[ i ] = "no"
                    self.table._lock_stat.release()
                    load = self.table.item( i, 1 )
                    load.setIcon( self.table._icon_NO )
                elif( task == "req" ):
                    self.table._lock_stat.acquire()
                    name = self.table._row_lut[ i ]
                    self.table._img_cache[ i ] = QtWidgets.QGraphicsPixmapItem( self.table._img_paths[ name ] )
                    self.table._cache_stat[ i ] = "yes"
                    self.table._lock_stat.release()
                    load = self.table.item( i, 1 )
                    load.setIcon( self.table._icon_YES )
            sleep( 3 )


class ImageTable( QtWidgets.QTableWidget ):
    
    def __init__( self, rows=None, columns=None, parent=None, main=None ):
        super( ImageTable, self ).__init__( rows, columns, parent )

        # reference to the main window
        self._main = main

        # Dissable Dropping
        self.setDragEnabled( False )
        self.setAcceptDrops( False )
        self.viewport().setAcceptDrops( False )
        self.setDragDropOverwriteMode( False )
        self.setDropIndicatorShown( False )

        # set Dropping Mode
        self.setSelectionMode( QtWidgets.QAbstractItemView.SingleSelection ) 
        self.setSelectionBehavior( QtWidgets.QAbstractItemView.SelectRows )

        # cache and annotation icons
        # http://nukesaq88.hatenablog.com/entry/2013/04/12/005525
        self._icon_OK  = QtGui.QIcon( QtWidgets.QApplication.style().standardIcon( QtWidgets.QStyle.SP_DialogApplyButton ) )
        self._icon_QUE = QtGui.QIcon( QtWidgets.QApplication.style().standardIcon( QtWidgets.QStyle.SP_MessageBoxQuestion ) )
        self._icon_YES = QtGui.QIcon( QtWidgets.QApplication.style().standardIcon( QtWidgets.QStyle.SP_DialogYesButton ) )
        self._icon_NO  = QtGui.QIcon( QtWidgets.QApplication.style().standardIcon( QtWidgets.QStyle.SP_DialogNoButton ) )

        # settings
        self.cache_sz = 20
        self.h_cache  = self.cache_sz // 2

        # variables
        self._img_paths = {} # name -> path
        self._row_lut   = {} # row -> name
        self._img_cache = {} # row -> pixmap
        self._img_idx   = -1
        self._lock_stat = Lock()
        self._cache_stat = [] # list of cache commands (no, yes, drop, req)

        # cache Manager
        self._cache_man = CacheMan( self )
        self._cache_man.start()

    def isAnnotated( self, idx ):
        image = self.item( idx, 0 )
        icon = image.icon().cacheKey()
        return icon == self._icon_OK.cacheKey()

    def selectionChanged( self, new, old ):
        indexs = new.indexes()
        if( len( indexs ) < 1 ):
            return

        row = indexs[ 0 ].row()
        self._img_idx = row
        if( self._cache_stat[ row ] != "yes" ): # cache miss
            self._lock_stat.acquire()
            name = self._row_lut[ row ]
            self._img_cache[ row ] = QtWidgets.QGraphicsPixmapItem( self._img_paths[ name ] )
            self._cache_stat[ row ] = "yes"
            load = self.item( row, 1 )
            load.setIcon( self._icon_YES )
            self._lock_stat.release()

        self._main._changeImageCB( row )

        self.marshelCache()
        super( ImageTable, self ).selectionChanged( new, old )

    def marshelCache( self ):
        self._lock_stat.acquire()
        num_rows = self.rowCount()

        if( self._img_idx > self.h_cache ):
            # 0 to idx-h can be dropped
            for i in range( 0, self._img_idx - self.h_cache ):
                if( self._cache_stat[ i ] == "no" ):
                    continue
                self._cache_stat[ i ] = "drop"
        else:
            # 0 to idx can be requested
            for i in range( 0, self._img_idx ):
                if( self._cache_stat[ i ] == "yes" ):
                    continue
                self._cache_stat[ i ] = "req"
        
        # idx to idx + sz can be requested
        max_sz = min( num_rows, self._img_idx + self.h_cache )
        for i in range( self._img_idx, max_sz ):
                if( self._cache_stat[ i ] == "yes" ):
                    continue
                self._cache_stat[ i ] = "req"

        # idx + sz to end can be dropped
        for i in range( max_sz, num_rows ):
                if( self._cache_stat[ i ] == "no" ):
                    continue
                self._cache_stat[ i ] = "drop"
        self._lock_stat.release()

    def populate( self, img_list, ano_list ):
        self._lock_stat.acquire()
        self._cache_stat = []

        have_anos = set( ano_list )
        num_imgs = len( img_list )
        self.setRowCount( num_imgs )
        for i, file_fq in enumerate( img_list ):

            name, ext = os.path.basename( file_fq ).split(".",1)

            img_name = QtWidgets.QTableWidgetItem( str( name ) )
            img_load = QtWidgets.QTableWidgetItem( "" )

            # test for anotations
            if( name in have_anos ):
                img_name.setIcon( self._icon_OK )
            else:
                img_name.setIcon( self._icon_QUE )

            # image caching
            self._cache_stat.append( "no" )
            img_load.setIcon( self._icon_NO )

            self.setItem( i, 0, img_name )
            self.setItem( i, 1, img_load )

            # register file
            self._img_paths[ name ] = file_fq
            self._row_lut[ i ] = name

        self._lock_stat.release()
        self.marshelCache()
        self._main._setLog( "loaded {} Images".format( num_imgs ) )

class AnoTree( QtWidgets.QTreeWidget ):

    CLEAR_SEL_ROW = QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Rows

    def __init__( self, main=None ):
        super( AnoTree, self ).__init__()
        # setup appearance
        self.setHeaderLabels( [ 'Type', "Region" ] )
        self.setAlternatingRowColors( True )
        self.setIndentation( 10 )
        self.setSelectionBehavior( QtWidgets.QTableView.SelectRows )

        self.setColumnWidth( 0, 120 )
        self.setColumnWidth( 1, 75 )

        # data
        self.current = None
        self.pending = None

        self._main = main #QAnnotator

    def _reset( self ):
        self.current = None
        self.pending = None
        # clear
        self.clear()

    def newFromTemplate( self, ano_tpl ):
        root_id = ano_tpl[ "_ROOT_" ]
        root = self._createItem( self, root_id )
        root.setDisabled( True )
        for region in ano_tpl[ root_id ]:
            reg = self._createItem( root, region )
            reg.setDisabled( True )
            if (region[ -1 ].isupper()):
                trait_id = region[ :-1 ]
            else:
                trait_id = region
            for trait in ano_tpl[ trait_id ]:
                trait_node = self._createItem( reg, trait )
                trait_node.setDisabled( True )

        self._expandChildren( root )
        self.prime( root )

    def _recLoad( self, sub_dict, parent_item ):
        for reg_name in sub_dict:
            if (reg_name == "__REGION__"):
                # parent's Region
                str_enc = sub_dict[ reg_name ]
                pos, rect = SizeableRegion.prFromString( str_enc )
                reg = self._main.createRegion( pos, rect, parent_item )
                reg.setPos( pos )
                reg.traits = set( sub_dict.get( "__TRAITS__", [] ) )
                reg.tags = set( sub_dict.get( "__TAGS__", [] ) )
                reg.activated = False
                parent_item.setText( 1, reg.toString() )
                continue
            elif( reg_name.startswith( "__" ) ):
                # parent's Tags & Traits
                continue

            reg_itm = self._createItem( parent_item, reg_name )
            reg_itm.setDisabled( True )
            child_dict = sub_dict[ reg_name ]
            self._recLoad( child_dict, reg_itm )

    def loadDict( self, reg_dict ):
        self.clear()
        for k, v in reg_dict.items():
            if( k in ("__ALL_TAGS__", "__IMG_META__") ): # Metadata
                continue
            root = self._createItem( self, k )
            root.setDisabled( True )
            self._recLoad( v, root )
            self._expandChildren( root )

    def _createItem( self, parent, name ):
        if( (id(parent) == id(self)) and (not name[-2:].isdigit()) ):
            # Top level, and no trailing digits - prevent collisions, auto add decimal
            count = 0
            new_name = "{}_{:0>2}".format( name, count )
            existing = []
            root = self.invisibleRootItem()
            for i in range( root.childCount() ):
                item = root.child( i )
                existing.append(  item.text( 0 ) )

            while( new_name in existing ):
                count += 1
                new_name = "{}_{:0>2}".format( name, count )
            name = new_name

        return QtWidgets.QTreeWidgetItem( parent, [ name, "" ] )

    def _expandChildren( self, item ):
        for i in range( item.childCount() ):
            self._expandChildren( item.child( i ) )
        self.expandItem( item )

    def toDict( self ):
        d = {}
        self._rec2Dict( d, self.invisibleRootItem() )
        return d

    def _rec2Dict( self, ret_dict, root ):
        for i in range( root.childCount() ):
            item = root.child( i )
            name = item.text( 0 )
            ret_dict[ name ] = {}
            self._rec2Dict( ret_dict[ name ], item )
        else:
            ret_dict["__ITEM__"] = root

    def prime( self, item ):
        self.pending = item
        if( self.pending ):
            self.selectionModel().select( self.indexFromItem( item ), self.CLEAR_SEL_ROW )
            name = self.pending.text( 0 )
            num = len( self._main.tag_dict.get( name, [] ) )
            self._main._line_hint.setText( "{} ({} tags)".format( name, num ) )
        else:
            self._main._line_hint.setText( "Regions Complete" )
            self._main.tag_mode.setChecked( True )
            
    def skipPending( self ):
        if( self.pending ):
            it = QtWidgets.QTreeWidgetItemIterator( self.pending )
            skip_item = it.value()
            parent = skip_item.parent()

            if( parent is not None ):
                parent.removeChild( skip_item )

            self.prime( it.value() )

    def _getTopLv( self, item ):
        parent = item.parent()
        if( parent is None ):
            return item
        else:
            return self._getTopLv( parent )

    def _skip2Next( self ):
        if( self.pending ):
            root = self._getTopLv( self.pending )
            it = QtWidgets.QTreeWidgetItemIterator( self.pending )
            skip_item = it.value()
            parent = skip_item.parent()
            if( id( parent ) == id( root ) ):
                self.skipPending()
                return

            while( id( parent ) == id( skip_item.parent() ) ):
                if( parent is not None ):
                    parent.removeChild( skip_item )
                    skip_item = it.value()
                else:
                    break
                    
            self.prime( it.value() )
            
    def _skip2End( self ):
        if( self.pending ):
            it = QtWidgets.QTreeWidgetItemIterator( self.pending )
            skip_item = it.value()
            while( skip_item ):
                parent = skip_item.parent()
                if( parent is not None ):
                    parent.removeChild( skip_item )
                else:
                    return
                skip_item = it.value()
                
        self.prime( None )
        
    def delPrevious( self ):
        it = QtWidgets.QTreeWidgetItemIterator( self.pending )
        it -= 1
        del_item = it.value()
        parent = del_item.parent()

        if( parent is not None ):
            parent.removeChild( del_item )

        self.prime( it.value() )

    def primeNext( self ):
        if( self.pending ):
            it = QtWidgets.QTreeWidgetItemIterator( self.pending )
            self.current = it.value()
            it += 1
            self.prime( it.value() )


class QtAnnotator( QtWidgets.QMainWindow ):

    RECT_SCALE_FACTOR = 110
    DEFAULT_CFG_PATH = r"C:\temp"
    DEFAULT_TGT_PATH = r"C:\temp\sort"
    DEFAULT_IMG_PATH = r"C:\temp\testImgs"
    DEFUALT_DEL_PATH = r"C:\temp\demoted"

    def __init__( self, parent ):
        super( QtAnnotator, self ).__init__()
        self._parent = parent

        # variables


        self.templates = {}

        self.img_idx = 0

        self.mode = "regions"

        # Region Lists
        self.regions = []
        self._reg_lut = {}

        # load inital data
        self._loadTemplates()
        #self.cur_template = "person" # TODO: cfg file

        # Build interface
        self.scene = QtWidgets.QGraphicsScene()
        self.view_pane = Viewer( scene=self.scene, main=self )
        self.anos = AnoTree( main=self )
        self._tabl_imgs = ImageTable( parent=parent, main=self )

        self._SHORTCUT_MAP = {
            QtCore.Qt.Key_F         : self.view_pane._fit2Scene,
            QtCore.Qt.Key_W         : self.anos._skip2Next,
            QtCore.Qt.Key_E         : self.anos._skip2End,
            QtCore.Qt.Key_Backspace : self.delLastReg,
        }
        for key, action in self._SHORTCUT_MAP.items():
            short_cut = QtWidgets.QShortcut( QtGui.QKeySequence( key ), self )
            short_cut.activated.connect( action )
            
        self.traitMenus = [ {}, {}, {} ]
        self._combos = [ None, None, None ]
        self.cur_preset = 0
        self.cur_template = ""
        self.cur_reg = None

        self._rect_sz = 150

        # Finaly setup the UI
        # Kill thread on exit
        parent.aboutToQuit.connect( self._tabl_imgs._cache_man.halt )
        self._buildUI()

    def _clearActivations( self ):
        for r in self.regions:
            r.activated = False

    def delLastReg( self ):
        if( len( self.regions ) > 0 ):
            old_reg = self.regions.pop()
            self.scene.removeItem( old_reg )
            # Clear previous entry in tree
            self.anos.delPrevious()

    def createRegion( self, pos, rect=None, anno_item=None ):
        # publish the last? one

        r = random.randint( 0, 256 )
        g = random.randint( 0, 256 )
        b = random.randint( 0, 256 )
        col = QtGui.QColor( r, g, b )

        name = "Bounding_{:0>2}".format( len( self.regions ) ) if anno_item is None else anno_item.text(0)
        QtCore.QRectF(0, 0, self._rect_sz, self._rect_sz) if rect is None else rect

        try:
            self.regions[ -1 ].selected = False
        except IndexError:
            pass
        reg = SizeableRegion( pos, rect=rect, parent=self.view_pane.cur_img, colour=col, name=name, viewer=self.view_pane, item=anno_item )

        #self._clearActivations()

        self.regions.append( reg )
        self._reg_lut[ anno_item ] = reg
        self.scene.addItem( reg )
        self.anos.primeNext()

        return reg

    def tagRegion( self, region, pos ):
        reg_name = region.name
        
        if( "_" in reg_name ):
            # It's a numbered Root Tag, so remove the numbering
            reg_name = reg_name[:-3]
            
        if( self.mode == "regions") :
            self._addTrait( "tag '{}' as '{}'".format( reg_name, self.anos.pending.text( 0 ) ) )
            region.traits.add( self.anos.pending.text( 0 ) )
            self.anos.primeNext()
        elif( self.mode == "tags"):
            self.cur_reg = region
            if( reg_name in self.traitMenus[ self.cur_preset ] ):
                self._line_hint.setText( "Tagging {}".format( reg_name ) )
                self.traitMenus[ self.cur_preset ][ reg_name ].exec_( pos )

            for trait in region.traits:
                self._line_hint.setText( "Tagging {}".format( trait ) )
                try:
                    self.traitMenus[ self.cur_preset ][ trait ].exec_( pos )
                except KeyError:
                    # Tag region with this trait
                    self.cur_reg.tags.add( trait )
                    self._addTag( trait )

    def _loadTemplates( self ):
        templates = glob( os.path.join( self.DEFAULT_CFG_PATH, "*_ano_tpl.json" ) )
        for template in templates:
            name = os.path.basename( template )
            name, _ = name.split(".",1)
            with open( template, "r" ) as fh:
                self.templates[ name[:-8] ] = json.load( fh )

    # Overloads      /////////////////////////////////////////////////////////////////////////
    def resizeEvent( self, event ):
        self.view_pane._fit2Scene()
        super( QtAnnotator, self ).resizeEvent( event )

    # Call Backs     ///////////////////////////////////////////////////////////
    def _changeImageCB( self, img_idx ):
        # clear GFX scene, preserving the PixMap
        if( self.view_pane.cur_img is not None ):
            self.scene.removeItem( self.view_pane.cur_img )
        self.scene.clear()

        # Reset Annotation Tree
        self.anos._reset()

        # reset scene managment
        self._reg_lut = {}

        # Reset Hint
        self._line_hint.setText( "" )
        self._addTrait( "----------" )
        self._addTag( "----------" )

        # get Image
        self.img_idx = img_idx
        img_item = self._tabl_imgs._img_cache[ self.img_idx ]
        self.scene.addItem( img_item )

        # reset scene rect
        img = img_item.pixmap()
        w, h = img.width(), img.height()
        self.scene.setSceneRect( 0, 0, w, h )
        self.view_pane.cur_img = img_item

        # reset the viewer
        self.view_pane._fit2Scene()

        # Set default rect Scale
        biggest = float( max( w, h ) )
        self._rect_sz = int( ( biggest / self.RECT_SCALE_FACTOR ) ) * 10

        # if annotated, load annotations
        if( self._tabl_imgs.isAnnotated( self.img_idx ) ):
            imgs_path = str( self._line_path.text() )
            name = self._tabl_imgs._row_lut[ self.img_idx ]
            file_fq = os.path.join( imgs_path, name + ".ano" )
            self.loadAnno( file_fq )
        self.reg_mode.setChecked( True )

    def loadAnno( self, file_fq ):
        with open( file_fq, "r" ) as fh:
            anno_dict = json.load( fh )
            self.anos.loadDict( anno_dict )

    def _comboChangeCB( self, preset, index):
        self._buildMenus( preset )

    # Button Actions ///////////////////////////////////////////////////////////
    def _doPath( self ):
        # get the img path
        curr = self._line_path.text()
        path = str( QtWidgets.QFileDialog.getExistingDirectory( self, caption="Select Image Directory", dir=curr ) )
        if( path ):
            self._line_path.setText( path )
            self._populateImgs()

    def _doPathTgt( self ):
        # get the img path
        curr = self._line_expo.text()
        path = str( QtWidgets.QFileDialog.getExistingDirectory( self, caption="Select Migration Directory", dir=curr ) )
        if (path):
            self._line_expo.setText( path )

    def _doCreate( self, preset ):
        template = self._combos[ preset ].currentText()
        self.cur_preset = preset
        self.cur_template = template
        self.anos.newFromTemplate( self.templates[ self.cur_template ] )
        self.reg_mode.setChecked( True )

    def _doSkipReg( self ):
        self.anos.skipPending()

    def _doNextReg( self ):
        self.anos.primeNext()

    def _doMode( self ):
        if( self.tag_mode.isChecked() ):
            self.mode = "tags"
        elif( self.reg_mode.isChecked() ):
            self.mode = "regions"

    def _recClean( self, data ):
        new = {}
        for k, v in data.items():
            if( type(v) == dict ):
                v = self._recClean( v )
            if( type(v) == dict ):
                if( v != {} ):
                    new[ k ] = v
            else:
                new[ k ] = v
        return new

    def _dictProcess( self, data, tag_set ):
        new={}
        for k, v in data.items():
            if( type( v ) == dict ):
                v = self._dictProcess( v, tag_set )
                if( v != {} ):
                    new[k] = v
            else:
                if( k == "__ITEM__" ):
                    if( v in self._reg_lut ):
                        reg = self._reg_lut[ v ]
                        new[ "__REGION__" ] = reg.toString()
                        if (len( reg.traits ) > 0):
                            new[ "__TRAITS__" ] = list( reg.traits )
                        if (len(  reg.tags ) > 0):
                            new[ "__TAGS__" ] = list( reg.tags )
                            tag_set.update( reg.tags )
        return new

    def _doExport( self ):
        regions = self.anos.toDict()
        all_tags = set()
        regions = self._dictProcess( regions, all_tags )

        imgs_path = str( self._line_path.text() )
        name = self._tabl_imgs._row_lut[ self.img_idx ]
        orig_file_fq = os.path.join( imgs_path, name + ".jpg" )

        # Add extra metadaata
        img = self.view_pane.cur_img.pixmap()
        regions["__ALL_TAGS__"] = list( all_tags )
        regions["__IMG_META__"] = {
            "ORIG_NAME"  : name,
            "DIMENSIONS" : [img.width(), img.height()],
            "SIZE"       : os.stat( orig_file_fq ).st_size
        }
        file_fq = os.path.join( imgs_path, name + ".ano")
        out = json.dumps( regions, indent=4 )
        with open( file_fq, "w" ) as fh:
            fh.write( out )
        self._tabl_imgs.item( self.img_idx, 0 ).setIcon( self._tabl_imgs._icon_OK )

    def _doMigrate( self ):
        src_folder = str( self._line_path.text() )
        tgt_folder = str( self._line_expo.text() )

        search = os.path.join( src_folder, "*.ano" )
        anos = glob( search )
        for src_ano in anos:
            name = os.path.basename( src_ano )
            name, _ = name.rsplit( ".", 1 )

            d = { }
            with open( src_ano, "r" ) as fh:
                d = json.load( fh )

            if (not "__IMG_META__" in d):
                d[ "__IMG_META__" ] = { "ORIG_NAME": name }

            if ("UUID" in d[ "__IMG_META__" ]):
                # allready renamed
                continue

            new_name = str( uuid.uuid4() )

            d[ "__IMG_META__" ][ "UUID" ] = new_name

            with open( src_ano, "w" ) as fh:
                fh.write( json.dumps( d, indent=4 ) )

            src_img = os.path.join( src_folder, name + ".jpg" )
            if (not os.path.isfile( src_img )):
                continue

            tgt_img = os.path.join( tgt_folder, new_name + ".jpg" )
            tgt_ano = os.path.join( tgt_folder, new_name + ".ano" )

            os.rename( src_ano, tgt_ano )
            os.rename( src_img, tgt_img )

            print("Moved {}".format( name ))
        # reset IMG table
        self._populateImgs()

    # UI Updates ///////////////////////////////////////////////////////////////
    def _showImg( self, idx ):
        self.img_idx = idx
        self._updateDisplay()

    def _updateDisplay( self ):
        # load Img
        self._tabl_imgs.selectRow( self.img_idx )
        # clear Logs
        self._text_trait.clear()
        self._text_tags.clear()

    def _updateRegions( self ):
        for reg in self.regions:
            reg._item.setText( 3, reg.toString() )

    def _setLog( self, msg ):
        self._text_logs.clear()
        self._text_logs.insertPlainText( msg )

    def _addTrait( self, msg ):
        self._text_trait.append( msg )

    def _addTag( self , msg):
        self._text_tags.append( msg )

    def _populateImgs( self ):
        # reset table
        self._tabl_imgs.setRowCount( 0 )
        self._tabl_imgs._img_paths = {}
        self._tabl_imgs._img_cache = {}
        self._tabl_imgs._row_lut   = {}

        # find Images
        imgs_path = str( self._line_path.text() )
        img_list = glob( os.path.join( imgs_path, "*.jpg" ) )

        # find anotations 
        ano_list = glob( os.path.join( imgs_path, "*.ano" ) )
        anos = []
        for ano in ano_list:
            name, ext = os.path.basename( ano ).split(".",1)
            anos.append( name )
        have_anos = set( anos )

        # add Images to list
        self._tabl_imgs.populate( img_list, anos )

        # reset pointer?
        self._tabl_imgs.setFocus()
        self._tabl_imgs.selectRow( 0 )

    def _uniTagAction( self, source ):
        tag = source.data()
        tags = tag.split("/")
        tags = [ tag for tag in tags if not tag.startswith("#") ]
        tag = "/".join( tags )
        self.cur_reg.tags.add( tag )
        self._addTag( tag )

    # Main UI ////////////////////////////////////////////////////////////////////////////////
    def run( self ):
        self.show()
        self._updateDisplay()
        self._parent.exec_()

    def _submenu( self, menu, menu_dict ):
        keys = sorted( menu_dict.keys() )
        dat = menu.menuAction().data()
        left = "" if dat is None else dat
        for k in keys:
            v = menu_dict[ k ]
            name = k[1:] if k.startswith("#") else k
            path = left + "/" + k
            if( v is None ):
                act = QtWidgets.QAction( name, self )
                path = left + "/" + k
                act.setData( path )
                menu.addAction( act )
                act.triggered.connect( partial( self._uniTagAction, act ) )
            else:
                t_menu = menu.addMenu( name )
                tma = t_menu.menuAction()
                tma.setData( path )
                self._submenu( t_menu, v )

    def _buildMenus( self, preset ):
        to_build = str( self._combos[ preset ].currentText() )
        self.tag_dict = self.templates[ to_build ]["_TAGS_"]
        self.traitMenus[ preset ].clear()
        self.traitMenus[ preset ] = {}
        for trait in  self.tag_dict.keys():
            t_menu = QtWidgets.QMenu( self )
            self.traitMenus[ preset ][ trait ] = t_menu
            t_menu.menuAction().setData( trait )
            self._submenu( t_menu,  self.tag_dict[ trait ] )

    def _buildUI( self ):
        self.setWindowTitle( "Image Tagger" )

        # Main layout
        wdgt_cent = QtWidgets.QWidget()
        layt_cent = QtWidgets.QGridLayout()

        # Images Control Panel ----------------------------------------------------------------------- Image Control ---
        wdgt_imgs = QtWidgets.QWidget()
        layt_imgs = QtWidgets.QGridLayout()

        # Image Path
        self._butn_path = QtWidgets.QPushButton("Set image Path")
        layt_imgs.addWidget( self._butn_path, 0, 0, 1, 1 )

        self._line_path = QtWidgets.QLineEdit( self.DEFAULT_IMG_PATH )
        self._line_path.setSizePolicy( QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum )
        layt_imgs.addWidget( self._line_path, 0, 1, 1, 1 )

        # List of Images to Annotate
        self._tabl_imgs.setColumnCount( 2 )
        self._tabl_imgs.setHorizontalHeaderLabels( ["File", "Img"] )
        header = self._tabl_imgs.horizontalHeader()
        header.setSectionResizeMode( 0, QtWidgets.QHeaderView.Stretch )
        header.setSectionResizeMode( 1, QtWidgets.QHeaderView.ResizeToContents )
        self._tabl_imgs.verticalHeader().setVisible( False )
        self._tabl_imgs.setSizePolicy( QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding )

        layt_imgs.addWidget( self._tabl_imgs, 2, 0, 8, 2 )

        # Logging
        font_text = QtGui.QFont( "Fixed", 10, QtGui.QFont.Normal )
        self._text_logs = QtWidgets.QTextEdit( self )
        self._text_logs.setReadOnly( True )
        self._text_logs.setSizePolicy( QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred )
        self._text_logs.setMaximumHeight( 60 )
        self._text_logs.setFont( font_text )
        layt_imgs.addWidget( self._text_logs, 10, 0, 1, 2 )
        self._setLog( "" )

        self._butn_expp = QtWidgets.QPushButton( "Set Migrate Path" )
        layt_imgs.addWidget( self._butn_expp, 11, 0, 1, 1 )

        self._line_expo = QtWidgets.QLineEdit( self.DEFAULT_TGT_PATH )
        self._line_expo.setSizePolicy( QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum )
        layt_imgs.addWidget( self._line_expo, 11, 1, 1, 1 )

        self._butn_expo = QtWidgets.QPushButton( "Migrate" )
        layt_imgs.addWidget( self._butn_expo, 12, 0, 1, 1 )

        # finish control panel
        wdgt_imgs.setLayout( layt_imgs )

        # add to central
        layt_cent.addWidget( wdgt_imgs, 0, 0, 2, 1 )

        # img Area --------------------------------------------------------------------------------- Image View Area ---

        font_hint = QtGui.QFont( "Arial", 18, QtGui.QFont.Bold )
        self._line_hint = QtWidgets.QLineEdit()
        self._line_hint.setFont( font_hint )
        self._line_hint.setAlignment( QtCore.Qt.AlignCenter )
        self._line_hint.setSizePolicy( QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum )
        layt_cent.addWidget( self._line_hint, 0, 1, 1, 1 )

        self.view_pane.setSizePolicy( QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding )
        layt_cent.addWidget( self.view_pane, 1, 1, 1, 1 )

        # Tag Control Panel ----------------------------------------------------------------------- Tagging Controls ---
        wdgt_tags = QtWidgets.QWidget()
        layt_tags = QtWidgets.QGridLayout()

        x, y = 0, 0
        layt_grp = QtWidgets.QGroupBox( "Quick Presets" )
        layt_pres = QtWidgets.QGridLayout()

        # prep presets
        self._comb_aqa1 = QtWidgets.QComboBox( self )
        self._comb_aqa2 = QtWidgets.QComboBox( self )
        self._comb_aqa3 = QtWidgets.QComboBox( self )
        self._combos = [ self._comb_aqa1, self._comb_aqa2, self._comb_aqa3 ]

        # Preset 1
        self._butn_aqa1 = QtWidgets.QPushButton( "(1) Add " )
        self._butn_aqa1.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum )
        layt_pres.addWidget( self._butn_aqa1, 0, 0, 1, 1 )

        self._comb_aqa1.currentIndexChanged.connect( partial( self._comboChangeCB, 0 ) )
        self._comb_aqa1.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum )
        for template in sorted( self.templates.keys() ):
            self._comb_aqa1.addItem( template )
        layt_pres.addWidget( self._comb_aqa1, 1, 0, 1, 1 )

        # Preset 2
        self._butn_aqa2 = QtWidgets.QPushButton( "(2) Add " )
        self._butn_aqa2.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum )
        layt_pres.addWidget( self._butn_aqa2, 0, 1, 1, 1 )

        self._comb_aqa2.currentIndexChanged.connect(  partial( self._comboChangeCB, 1 ) )
        self._comb_aqa2.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum )
        for template in sorted( self.templates.keys() ):
            self._comb_aqa2.addItem( template )
        layt_pres.addWidget( self._comb_aqa2, 1, 1, 1, 1 )

        # Preset 3
        self._butn_aqa3 = QtWidgets.QPushButton( "(3) Add " )
        self._butn_aqa3.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum )
        layt_pres.addWidget( self._butn_aqa3, 0, 2, 1, 1 )

        self._comb_aqa3.currentIndexChanged.connect(  partial( self._comboChangeCB, 2 ) )
        self._comb_aqa3.setSizePolicy( QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum )
        for template in sorted( self.templates.keys() ):
            self._comb_aqa3.addItem( template )
        layt_pres.addWidget( self._comb_aqa3, 1, 2, 1, 1 )

        # Attach CBs
        self._butn_aqa1.clicked.connect( partial( self._doCreate, 0 ) )
        self._butn_aqa2.clicked.connect( partial( self._doCreate, 1 ) )
        self._butn_aqa3.clicked.connect( partial( self._doCreate, 2 ) )

        QtWidgets.QShortcut( QtGui.QKeySequence(QtCore.Qt.Key_1), self._butn_aqa1, partial( self._doCreate, 0 ) )
        QtWidgets.QShortcut( QtGui.QKeySequence(QtCore.Qt.Key_2), self._butn_aqa2, partial( self._doCreate, 1 ) )
        QtWidgets.QShortcut( QtGui.QKeySequence(QtCore.Qt.Key_3), self._butn_aqa3, partial( self._doCreate, 2 ) )
        # add to tag layout
        layt_grp.setLayout( layt_pres )
        layt_grp.setSizePolicy( QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum )
        layt_tags.addWidget( layt_grp, y, x, 1, 3 )
        y += 1; x = 0

        self._butn_save = QtWidgets.QPushButton( "Save" )
        layt_tags.addWidget( self._butn_save, y, x, 1, 1 )

        x += 1
        bg_mode = QtWidgets.QButtonGroup()
        self.reg_mode = QtWidgets.QRadioButton( "Region Mode" )
        self.tag_mode = QtWidgets.QRadioButton( "Tage Mode" )
        bg_mode.addButton( self.reg_mode )
        bg_mode.addButton( self.tag_mode )
        self.tag_mode.toggled.connect( self._doMode )
        self.reg_mode.toggled.connect( self._doMode )
        self.reg_mode.setChecked( True )

        layt_tags.addWidget( self.reg_mode, y, x, 1, 1 )
        x += 1
        layt_tags.addWidget( self.tag_mode, y, x, 1, 1 )

        y += 1; x = 0

        # anotation tree
        self.anos.setSizePolicy( QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum )
        layt_tags.addWidget( self.anos, y, x, 1, 3 )

        y += 1; x = 0

        # traits log
        self._text_trait = QtWidgets.QTextEdit( self )
        self._text_trait.setReadOnly( True )
        self._text_trait.setSizePolicy( QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum )
        self._text_trait.setMaximumHeight( 60 )
        self._text_trait.setFont( font_text )
        layt_tags.addWidget( self._text_trait, y, x, 1, 3 )

        y += 1; x = 0

        # traits log
        self._text_tags = QtWidgets.QTextEdit( self )
        self._text_tags.setReadOnly( True )
        self._text_tags.setSizePolicy( QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum )
        self._text_tags.setMaximumHeight( 120 )
        self._text_tags.setFont( font_text )
        layt_tags.addWidget( self._text_tags, y, x, 1, 3 )

        # finish tag panel
        wdgt_tags.setLayout( layt_tags )

        # add to central
        layt_cent.addWidget( wdgt_tags, 0, 2, 2, 1 )

        # finish central -----------------------------------------------------------------------------------------------
        wdgt_cent.setLayout( layt_cent )

        # finalize the appWindow
        self.setCentralWidget( wdgt_cent )

        # attach CBs and events
        self._butn_path.clicked.connect( self._doPath )
        self._butn_save.clicked.connect( self._doExport )
        self._butn_expp.clicked.connect( self._doPathTgt )
        self._butn_expo.clicked.connect( self._doMigrate )

        # populate
        self._populateImgs()

if( __name__ == "__main__" ):
    _app = QtWidgets.QApplication( sys.argv )
    anno = QtAnnotator( _app )
    anno.run()
