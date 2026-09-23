# Tela is a Krita plugin for a Canvas Tool Box
# Copyright (C) 2021  Ricardo Jeremias.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Settings dialog for editing Tela's toolbox layout: which tools are primaries
# (slots) and which secondaries hide behind each. Three lists — slots, the
# selected slot's members, and the pool of unassigned tools. Convention: the
# first member of a slot is its primary / resting tool.

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (
    QDialog, QListWidget, QListWidgetItem, QPushButton, QLabel, QSpinBox,
    QHBoxLayout, QVBoxLayout, QWidget, QAbstractItemView, QDialogButtonBox,
    QMessageBox,
    )

ROLE = QtCore.Qt.ItemDataRole.UserRole


class Layout_Settings_Dialog( QDialog ):
    # catalog: { toolkey: [ label, action_id, qicon, _ ] } — the fixed tool set.
    # layout:  { "groups": [ [ primary, sec, ... ], ... ], "hold_ms": int }.
    # default_groups: list of key-lists, for "Restore Defaults".
    def __init__( self, catalog, layout, default_groups, parent = None ):
        super().__init__( parent )
        self.catalog = catalog
        self.default_groups = default_groups
        self.setWindowTitle( "Tela — Configure Toolbox" )

        # Model. Slots keyed by a stable id so drag-reorder of the slot list
        # doesn't have to be mapped back through changing row indices.
        self._next_id = 0
        self.slot_members = dict()   # id -> [ toolkey, ... ]  ( first = primary )
        self.current_id = None
        self._loading = False        # suppress the reorder handler during fills

        self._build_ui()

        order = list()
        for group in layout["groups"]:
            sid = self._new_id()
            self.slot_members[sid] = list( group )
            order.append( sid )
        self._fill_slots( order )
        self.hold_spin.setValue( int( layout.get( "hold_ms", 300 ) ) )
        if self.slots_list.count() > 0:
            self.slots_list.setCurrentRow( 0 )

    #region Build

    def _new_id( self ):
        self._next_id += 1
        return self._next_id

    def _build_ui( self ):
        # Slots column
        slots_col = QVBoxLayout()
        slots_col.addWidget( QLabel( "Slots (bar order)" ) )
        self.slots_list = QListWidget()
        self.slots_list.setDragDropMode( QAbstractItemView.DragDropMode.InternalMove )
        self.slots_list.currentRowChanged.connect( self._slot_selected )
        slots_col.addWidget( self.slots_list )
        slot_btns = QHBoxLayout()
        self.btn_slot_add = QPushButton( "Add" )
        self.btn_slot_del = QPushButton( "Remove" )
        self.btn_slot_add.clicked.connect( self._slot_add )
        self.btn_slot_del.clicked.connect( self._slot_remove )
        slot_btns.addWidget( self.btn_slot_add )
        slot_btns.addWidget( self.btn_slot_del )
        slots_col.addLayout( slot_btns )

        # Members column
        members_col = QVBoxLayout()
        members_col.addWidget( QLabel( "Slot tools (first = primary)" ) )
        self.members = QListWidget()
        self.members.setDragDropMode( QAbstractItemView.DragDropMode.InternalMove )
        self.members.model().rowsMoved.connect( lambda *a: self._members_reordered() )
        members_col.addWidget( self.members )
        member_btns = QHBoxLayout()
        self.btn_add = QPushButton( "◀ Add" )
        self.btn_del = QPushButton( "Remove ▶" )
        self.btn_add.clicked.connect( self._add_from_pool )
        self.btn_del.clicked.connect( self._remove_to_pool )
        member_btns.addWidget( self.btn_add )
        member_btns.addWidget( self.btn_del )
        members_col.addLayout( member_btns )

        # Pool column
        pool_col = QVBoxLayout()
        pool_col.addWidget( QLabel( "Available tools" ) )
        self.pool = QListWidget()
        pool_col.addWidget( self.pool )

        # Lists row
        lists = QHBoxLayout()
        lists.addLayout( slots_col )
        lists.addLayout( members_col )
        lists.addLayout( pool_col )

        # Hold time
        hold_row = QHBoxLayout()
        hold_row.addWidget( QLabel( "Hold to reveal secondaries:" ) )
        self.hold_spin = QSpinBox()
        self.hold_spin.setRange( 100, 2000 )
        self.hold_spin.setSingleStep( 50 )
        self.hold_spin.setSuffix( " ms" )
        hold_row.addWidget( self.hold_spin )
        hold_row.addStretch( 1 )

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
            )
        buttons.accepted.connect( self.accept )
        buttons.rejected.connect( self.reject )
        buttons.button( QDialogButtonBox.StandardButton.RestoreDefaults ).clicked.connect( self._restore_defaults )

        root = QVBoxLayout( self )
        root.addLayout( lists )
        root.addLayout( hold_row )
        root.addWidget( buttons )
        self.resize( 640, 420 )

    #endregion
    #region Items

    def _slot_label( self, sid ):
        keys = self.slot_members[sid]
        if len( keys ) == 0:
            return "(empty slot)"
        primary = self.catalog[keys[0]][0]
        extra = len( keys ) - 1
        return primary + ( "  +%d" % extra if extra > 0 else "" )

    def _member_item( self, key, primary ):
        text = self.catalog[key][0] + ( "  (primary)" if primary else "" )
        item = QListWidgetItem( text )
        item.setData( ROLE, key )
        icon = self.catalog[key][2]
        if icon is not None:
            item.setIcon( icon )
        font = item.font()
        font.setBold( primary )
        item.setFont( font )
        return item

    def _fill_slots( self, order ):
        self.slots_list.blockSignals( True )
        self.slots_list.clear()
        for sid in order:
            item = QListWidgetItem( self._slot_label( sid ) )
            item.setData( ROLE, sid )
            self.slots_list.addItem( item )
        self.slots_list.blockSignals( False )

    #endregion
    #region Sync

    def _commit_members( self ):
        # Read the members widget order back into the model for the current slot.
        if self.current_id is None or self.current_id not in self.slot_members:
            return
        keys = [ self.members.item( i ).data( ROLE ) for i in range( self.members.count() ) ]
        self.slot_members[self.current_id] = keys

    def _populate_members( self ):
        self._loading = True
        self.members.clear()
        if self.current_id is not None:
            for i, key in enumerate( self.slot_members[self.current_id] ):
                self.members.addItem( self._member_item( key, i == 0 ) )
        self._loading = False

    def _refresh_pool( self ):
        self._commit_members()
        assigned = set()
        for keys in self.slot_members.values():
            assigned.update( keys )
        self.pool.clear()
        for key in self.catalog:
            if key not in assigned:
                item = QListWidgetItem( self.catalog[key][0] )
                item.setData( ROLE, key )
                icon = self.catalog[key][2]
                if icon is not None:
                    item.setIcon( icon )
                self.pool.addItem( item )

    def _retag_members( self ):
        for i in range( self.members.count() ):
            item = self.members.item( i )
            key = item.data( ROLE )
            item.setText( self.catalog[key][0] + ( "  (primary)" if i == 0 else "" ) )
            font = item.font()
            font.setBold( i == 0 )
            item.setFont( font )

    def _update_slot_item( self ):
        row = self.slots_list.currentRow()
        if row >= 0:
            self.slots_list.item( row ).setText( self._slot_label( self.current_id ) )

    #endregion
    #region Actions

    def _slot_selected( self, row ):
        self._commit_members()
        if row < 0:
            self.current_id = None
            self.members.clear()
            return
        self.current_id = self.slots_list.item( row ).data( ROLE )
        self._populate_members()

    def _slot_add( self ):
        self._commit_members()
        sid = self._new_id()
        self.slot_members[sid] = list()
        item = QListWidgetItem( self._slot_label( sid ) )
        item.setData( ROLE, sid )
        self.slots_list.addItem( item )
        self.slots_list.setCurrentRow( self.slots_list.count() - 1 )

    def _slot_remove( self ):
        row = self.slots_list.currentRow()
        if row < 0 or self.slots_list.count() <= 1:
            return
        self._commit_members()
        sid = self.slots_list.item( row ).data( ROLE )
        # Drop the id first so the selection-change that takeItem triggers
        # doesn't commit the members widget back into a slot we are deleting.
        self.current_id = None
        del self.slot_members[sid]
        self.slots_list.takeItem( row )
        self._refresh_pool()

    def _add_from_pool( self ):
        if self.current_id is None:
            return
        selected = self.pool.selectedItems()
        if len( selected ) == 0:
            return
        row = self.pool.currentRow()
        for item in selected:
            key = item.data( ROLE )
            self.members.addItem( self._member_item( key, self.members.count() == 0 ) )
        self._commit_members()
        self._retag_members()
        self._update_slot_item()
        self._refresh_pool()
        # Keep selection on the item that shifted up into the freed row, so a
        # group can be moved across with repeated clicks.
        if self.pool.count() > 0:
            self.pool.setCurrentRow( min( row, self.pool.count() - 1 ) )

    def _remove_to_pool( self ):
        selected = self.members.selectedItems()
        if len( selected ) == 0:
            return
        row = self.members.currentRow()
        for item in selected:
            self.members.takeItem( self.members.row( item ) )
        self._commit_members()
        self._retag_members()
        self._update_slot_item()
        self._refresh_pool()
        if self.members.count() > 0:
            self.members.setCurrentRow( min( row, self.members.count() - 1 ) )

    def _members_reordered( self ):
        if self._loading:
            return
        self._commit_members()
        self._retag_members()
        self._update_slot_item()

    def _restore_defaults( self ):
        self.current_id = None
        self.slot_members = dict()
        order = list()
        for group in self.default_groups:
            sid = self._new_id()
            self.slot_members[sid] = list( group )
            order.append( sid )
        self._fill_slots( order )
        self.hold_spin.setValue( 300 )
        self._refresh_pool()
        if self.slots_list.count() > 0:
            self.slots_list.setCurrentRow( 0 )

    #endregion
    #region Result

    def accept( self ):
        self._commit_members()
        if not any( len( keys ) > 0 for keys in self.slot_members.values() ):
            QMessageBox.warning( self, "Tela", "Add at least one tool to a slot before saving." )
            return
        super().accept()

    def result_layout( self ):
        self._commit_members()
        groups = list()
        for i in range( self.slots_list.count() ):
            sid = self.slots_list.item( i ).data( ROLE )
            keys = self.slot_members[sid]
            if len( keys ) > 0:
                groups.append( list( keys ) )
        return { "groups": groups, "hold_ms": self.hold_spin.value() }

    #endregion
