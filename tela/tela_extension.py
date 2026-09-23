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


#region Imports

# Python Module
import zipfile
import json
# Krita Module
from krita import *
# PyQt6 Modules
from PyQt6 import QtWidgets, QtCore, QtGui, uic
from PyQt6.QtWidgets import QAbstractScrollArea
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
# Project Pages Modules
from .tela_modulo import (
    MirrorFix_Button,
    Color_Display,
    Color_Panel,
    )
from .tela_settings import Layout_Settings_Dialog

#endregion
#region Global Variables

EXTENSION_NAME = "Tela"

#endregion


class Tela_Extension( Extension ):
    """
    Tela ToolBox
    """

    #region Initialize

    def __init__(self, parent):
        super().__init__(parent)
    def setup(self):
        self.User_Interface()
        self.Variables()
        self.Modules()

    def User_Interface( self ):
        # Operating System
        self.OS = str( QSysInfo.kernelType() ) # WINDOWS=winnt & LINUX=linux
        if self.OS == 'winnt': # Unlocks icons in Krita for Menu Mode
            QApplication.setAttribute( Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False )
        # Path Name
        self.directory_plugin = str( os.path.dirname( os.path.realpath( __file__ ) ) )
        # Color Picker
        color_picker_ui = os.path.join( self.directory_plugin, "color_picker.ui" )
        self.color_picker = uic.loadUi( color_picker_ui, QWidget() )
    def Variables( self ):
        # None Variables
        self.qmenu = None
        self.stacked_widget = None
        self.qmdiarea = None
        self.canvas_widget = None
        self.window_list = list()

        # Variables
        ki = Krita.instance()
        # Vector
        icon_select_tool        = ki.icon( "select" )
        icon_text_tool          = ki.icon( "draw-text" )
        icon_edit_tool          = ki.icon( "shape_handling" )
        icon_calligraphy_tool   = ki.icon( "calligraphy" )
        icon_comic_tool         = ki.icon( "tool_comic_panel" )
        # Brush
        icon_freehand_brush     = ki.icon( "krita_tool_freehand" )
        icon_line_brush         = ki.icon( "krita_tool_line" )
        icon_rectangle_brush    = ki.icon( "krita_tool_rectangle" )
        icon_ellipse_brush      = ki.icon( "krita_tool_ellipse" )
        icon_polygon_brush      = ki.icon( "krita_tool_polygon" )
        icon_polyline_brush     = ki.icon( "polyline" )
        icon_bezier_brush       = ki.icon( "krita_draw_path" )
        icon_path_brush         = ki.icon( "krita_tool_freehandvector" )
        icon_dynamic_brush      = ki.icon( "krita_tool_dyna" )
        icon_multi_brush        = ki.icon( "krita_tool_multihand" )
        # Transform
        icon_transform_tool     = ki.icon( "krita_tool_transform" )
        icon_move_tool          = ki.icon( "krita_tool_move" )
        icon_crop_tool          = ki.icon( "tool_crop" )
        # Color
        icon_gradient_tool      = ki.icon( "krita_tool_gradient" )
        icon_sampler_tool       = ki.icon( "krita_tool_color_sampler" )
        icon_colorize_tool      = ki.icon( "krita_tool_lazybrush" )
        icon_patch_tool         = ki.icon( "krita_tool_smart_patch" )
        icon_fill_tool          = ki.icon( "krita_tool_color_fill" )
        icon_enclose_tool       = ki.icon( "krita_tool_enclose_and_fill" )
        # Overlay
        icon_assistant_tool     = ki.icon( "krita_tool_assistant" )
        icon_measure_tool       = ki.icon( "krita_tool_measure" )
        icon_reference_tool     = ki.icon( "krita_tool_reference_images" )
        # Select
        icon_rectangle_select   = ki.icon( "tool_rect_selection" )
        icon_elliptical_select  = ki.icon( "tool_elliptical_selection" )
        icon_polygon_select     = ki.icon( "tool_polygonal_selection" )
        icon_freehand_select    = ki.icon( "tool_outline_selection")
        icon_contiguous_select  = ki.icon( "tool_contiguous_selection" )
        icon_color_select       = ki.icon( "tool_similar_selection")
        icon_bezier_select      = ki.icon( "tool_path_selection")
        icon_magnetic_select    = ki.icon( "tool_magnetic_selection" )
        # Camera
        icon_zoom_tool          = ki.icon( "tool_zoom" )
        icon_pan_tool           = ki.icon( "tool_pan" )
        # Mirror Fix
        self.icon_mirrorfix = "wraparound"

        # Toolbox ( name, pykrita, qicon )
        self.tool = {
            "vector" : {
                "select_tool"        : [ "Select",      "InteractionTool",                   icon_select_tool,        0 ],
                "text_tool"          : [ "Text",        "SvgTextTool",                       icon_text_tool,          1 ],
                "edit_tool"          : [ "Edit",        "PathTool",                          icon_edit_tool,          2 ],
                "calligraphy_tool"   : [ "Calligraphy", "KarbonCalligraphyTool",             icon_calligraphy_tool,   3 ],
                "comic_tool"         : [ "Comic",       "KritaShape/KisToolKnife",           icon_comic_tool,         4 ],
                },
            "brush" : {
                "freehand_brush"     : [ "Freehand",    "KritaShape/KisToolBrush",           icon_freehand_brush,     0 ],
                "line_brush"         : [ "Line",        "KritaShape/KisToolLine",            icon_line_brush,         1 ],
                "rectangle_brush"    : [ "Rectangle",   "KritaShape/KisToolRectangle",       icon_rectangle_brush,    2 ],
                "ellipse_brush"      : [ "Ellipse",     "KritaShape/KisToolEllipse",         icon_ellipse_brush,      3 ],
                "polygon_brush"      : [ "Polygon",     "KisToolPolygon",                    icon_polygon_brush,      4 ],
                "polyline_brush"     : [ "Polyline",    "KisToolPolyline",                   icon_polyline_brush,     5 ],
                "bezier_brush"       : [ "Bezier",      "KisToolPath",                       icon_bezier_brush,       6 ],
                "path_brush"         : [ "Path",        "KisToolPencil",                     icon_path_brush,         7 ],
                "dynamic_brush"      : [ "Dynamic",     "KritaShape/KisToolDyna",            icon_dynamic_brush,      8 ],
                "multi_brush"        : [ "Multibrush",  "KritaShape/KisToolMultiBrush",      icon_multi_brush,        9 ],
                },
            "transform" : {
                "transform_tool"     : [ "Transform",   "KisToolTransform",                  icon_transform_tool,     0 ],
                "move_tool"          : [ "Move",        "KritaTransform/KisToolMove",        icon_move_tool,          1 ],
                "crop_tool"          : [ "Crop",        "KisToolCrop",                       icon_crop_tool,          2 ],
                },
            "color" : {
                "gradient_tool"      : [ "Gradient",    "KritaFill/KisToolGradient",         icon_gradient_tool,      0 ],
                "sampler_tool"       : [ "Sampler",     "KritaSelected/KisToolColorSampler", icon_sampler_tool,       1 ],
                "colorize_tool"      : [ "Colorize",    "KritaShape/KisToolLazyBrush",       icon_colorize_tool,      2 ],
                "patch_tool"         : [ "Patch",       "KritaShape/KisToolSmartPatch",      icon_patch_tool,         3 ],
                "fill_tool"          : [ "Fill",        "KritaFill/KisToolFill",             icon_fill_tool,          4 ],
                "enclose_tool"       : [ "Enclose",     "KisToolEncloseAndFill",             icon_enclose_tool,       5 ],
                },
            "overlay" : {
                "assistant_tool"     : [ "Assistant",   "KisAssistantTool",                  icon_assistant_tool,     0 ],
                "measure_tool"       : [ "Measure",     "KritaShape/KisToolMeasure",         icon_measure_tool,       1 ],
                "reference_tool"     : [ "Reference",   "ToolReferenceImages",               icon_reference_tool,     2 ],
                },
            "select" : {
                "rectangle_select"   : [ "Rectangle",   "KisToolSelectRectangular",          icon_rectangle_select,   0 ],
                "elliptical_select"  : [ "Elliptical",  "KisToolSelectElliptical",           icon_elliptical_select,  1 ],
                "polygon_select"     : [ "Polygon",     "KisToolSelectPolygonal",            icon_polygon_select,     2 ],
                "freehand_select"    : [ "Freehand",    "KisToolSelectOutline",              icon_freehand_select,    3 ],
                "contiguous_select"  : [ "Contiguous",  "KisToolSelectContiguous",           icon_contiguous_select,  4 ],
                "color_select"       : [ "Color",       "KisToolSelectSimilar",              icon_color_select,       5 ],
                "bezier_select"      : [ "Bezier",      "KisToolSelectPath",                 icon_bezier_select,      6 ],
                "magnetic_select"    : [ "Magnetic",    "KisToolSelectMagnetic",             icon_magnetic_select,    7 ],
                },
            "camera" : {
                "zoom_tool"          : [ "Zoom",        "ZoomTool",                          icon_zoom_tool,          0 ],
                "pan_tool"           : [ "Pan",         "PanTool",                           icon_pan_tool,           1 ],
                },
        }
        # Flatten the fixed tool set above into a catalog, then build the
        # runtime grouping ( primaries + secondaries ) from user config.
        # This replaces the old hardcoded seven-group model. See Layout_Init.
        self.Layout_Init()
        # Krita ToolBox ( Install Event Filter )
        self.krita_toolbox = list()

        # Tool Box Widget — primary buttons keyed by group id ( built in
        # Interface_Create ). Fly-out buttons live in self.flyout_buttons.
        self.primary = dict()
        self.flyout_buttons = list()
        self.flyout_items = list()   # [ ( button, gid, toolkey ) ] for hit-testing
        # Progress Bar Widget
        self.progress_bar = None
        # Actions Widget
        self.menu_mirror_fix = None
        self.menu_color_picker = None
        # Widgets Widget
        self.menu_tela = None

        # State
        self.show_option = False
        self.show_extra = False
        self.hide_tela = False

        # Pushbutton Size
        self.pba = 52
        self.pbb = 34
        self.pbc = 24
        self.pbs = 5
        # Menu Margin
        self.mx = 10
        self.my = 10

        # Menu — self.press_time ( hold duration ) is set from config in Layout_Init.
        self.menu_hold = None

        # Color Picker Module
        self.pigmento_picker = None
        self.pigmento_picker_pyid = "pykrita_pigment_o_picker_docker"

        # ProgressBar
        self.krita_progress_bar_id = "ProgressBar"
        self.krita_progress_bar_module = None

        # Color Picker
        self.qpixmap_list = list()
        self.hue = 360 # 360
        self.svl = 255 # 255
        self.wheel_space = None # HSV HSL HCY ARD
        self.s1 = 0 # 0-360
        self.s2 = 0 # 0-255
        self.s3 = 0 # 0-255
        self.cor = None # Pigment.o color object
    def Modules( self ):
        #region Notifier
        self.notifier = Krita.instance().notifier()
        self.notifier.applicationClosing.connect( self.Application_Closing )
        self.notifier.configurationChanged.connect( self.Configuration_Changed )
        self.notifier.imageClosed.connect( self.Image_Closed )
        self.notifier.imageCreated.connect( self.Image_Created )
        self.notifier.imageSaved.connect( self.Image_Saved )
        self.notifier.viewClosed.connect( self.View_Closed )
        self.notifier.viewCreated.connect( self.View_Created )
        self.notifier.windowCreated.connect( self.Window_Created )
        self.notifier.windowIsBeingCreated.connect( self.Window_IsBeingCreated )

        #endregion
        #region Color Picker

        self.color_display = Color_Display( self.color_picker.color_display )
        self.color_panel = Color_Panel( self.color_picker.color_panel )
        self.color_panel.SIGNAL_PREVIEW.connect( self.Color_Panel_Preview )
        self.color_panel.SIGNAL_APPLY.connect( self.Color_Panel_Apply )

        #endregion

    #endregion
    #region Management

    # Kritarc
    def Kritarc_Read( self, group, key, default, mode ):
        value = Krita.instance().readSetting( group, key, "" )
        invalid = [ "", None ]
        if value not in invalid:
            value = mode( value )
        else:
            value = default
            self.Kritarc_Write( group, key, default )
        return value
    def Kritarc_Write( self, group, key, value ):
        Krita.instance().writeSetting( group, key, str( value ) )

    # Layout ( configurable primaries / secondaries )
    def Layout_Init( self ):
        # At this point self.tool still holds the hardcoded nested literal.
        # Flatten it into a flat catalog ( the fixed Krita tool set ) and
        # capture the literal's grouping as the default layout. The catalog
        # keeps the SAME list objects, so Style_Icon updates propagate to
        # every group that references a tool.
        self.tool_catalog = dict()
        default_groups = list()
        for group in self.tool.values():
            keys = list( group.keys() )
            default_groups.append( keys )
            for k in keys:
                self.tool_catalog[k] = group[k]
        # Keep the literal's grouping around for the settings dialog's
        # "Restore Defaults".
        self.default_groups = default_groups
        # Load config, then build runtime structures.
        self.layout = self.Layout_Load( default_groups )
        self.press_time = self.layout["hold_ms"]
        self.Layout_Build()
    def Layout_Default( self, default_groups ):
        return { "groups": default_groups, "hold_ms": 300 }
    def Layout_Load( self, default_groups ):
        default = self.Layout_Default( default_groups )
        raw = Krita.instance().readSetting( EXTENSION_NAME, "layout", "" )
        if raw in [ "", None ]:
            self.Layout_Save( default )
            return default
        try:
            data = json.loads( raw )
            # Drop unknown tool keys and empty groups.
            groups = [ [ k for k in g if k in self.tool_catalog ] for g in data["groups"] ]
            groups = [ g for g in groups if len( g ) > 0 ]
            if len( groups ) == 0:
                raise ValueError( "no valid groups in layout config" )
            hold_ms = int( data.get( "hold_ms", 300 ) )
            return { "groups": groups, "hold_ms": hold_ms }
        except Exception:
            # Corrupt config — fall back to default rather than crash on load.
            self.Layout_Save( default )
            return default
    def Layout_Save( self, layout ):
        Krita.instance().writeSetting( EXTENSION_NAME, "layout", json.dumps( layout ) )
    def Layout_Build( self ):
        # Rebuild self.tool ( now keyed by opaque group id ) plus the per-group
        # runtime state, all from the catalog + loaded layout. Group members
        # reference the shared catalog lists. First member of each group is its
        # primary / resting tool.
        self.group_ids = list()
        self.tool = dict()            # gid -> { toolkey: [label, action, icon, _] }
        self.group_primary = dict()   # gid -> primary toolkey
        self.index = dict()           # gid -> currently active toolkey
        self.operation = dict()       # gid -> currently active action id
        for i, keys in enumerate( self.layout["groups"] ):
            gid = "g" + str( i )
            self.group_ids.append( gid )
            self.tool[gid] = dict()
            for k in keys:
                self.tool[gid][k] = self.tool_catalog[k]
            primary = keys[0]
            self.group_primary[gid] = primary
            self.index[gid] = primary
            self.operation[gid] = self.tool_catalog[primary][1]
    def Group_Of_Tool( self, toolkey ):
        # Which group id currently contains a tool key ( or None ).
        for gid in self.group_ids:
            if toolkey in self.tool[gid]:
                return gid
        return None
    def Layout_Settings( self ):
        # Open the editor; on Save, apply the new layout live.
        dialog = Layout_Settings_Dialog( self.tool_catalog, self.layout, self.default_groups, self.window.qwindow() )
        if dialog.exec():
            self.Layout_Apply( dialog.result_layout() )
    def Layout_Apply( self, new_layout ):
        # Persist and rebuild the runtime model + primary buttons in place, so a
        # layout change takes effect without restarting Krita.
        self.Menu_Reset()
        self.layout = new_layout
        self.Layout_Save( new_layout )
        self.press_time = new_layout["hold_ms"]
        self.Layout_Build()
        self.Primary_Rebuild()
        self.Style_Theme()
        self.Style_Icon()
        self.Tela_Geometry( self.show_option, self.show_extra, self.hide_tela )
        self.Tool_Update()
    def Primary_Rebuild( self ):
        # Destroy the old primary buttons and recreate one per configured group.
        # These are the only overlay widgets whose count/identity depends on the
        # layout; everything else loops over self.group_ids dynamically.
        for gid in list( self.primary.keys() ):
            button = self.primary[gid]
            button.hide()
            button.setParent( None )
            button.deleteLater()
        self.primary = dict()
        parent = self.canvas_widget   # may be None ( no document ); adopted later by Canvas_Changed
        for gid in self.group_ids:
            button = QPushButton( "primary_" + gid, parent )
            self.Interface_Push_Button( button, "primary_" + gid, self.pba, self.pba, True, True, False )
            button.setIcon( self.tool_catalog[self.index[gid]][2] )
            button.pressed.connect(  lambda g = gid: self.Hold_Primary( g ) )
            button.released.connect( lambda g = gid: self.Release_Primary( g ) )
            self.primary[gid] = button
            if parent is not None:
                button.show()
                button.raise_()

    # Warnnings
    def Message_Float( self, operation, message, icon ):
        ki = Krita.instance()
        string = f"TELA | { operation } { message }"
        try:ki.activeWindow().activeView().showFloatingMessage( string, ki.icon( icon ), 5000, 0 )
        except:pass
    # Math
    def Limit_Range( self, value, mini, maxi, minifix, maxifix ):
        if value <= mini:   value = mini + minifix
        if value >= maxi:   value = maxi + maxifix
        return value
    # Canvas
    def Check_Canvas( self ):
        # Variables
        ki = Krita.instance()
        view = ki.activeWindow().activeView()
        canvas = view.canvas()
        # Return
        if ( canvas != None ) and ( view != None ): return True
        else:                                       return False
    # Progress Bar
    def ProgressBar_StyleSheet( self, percentage, background ):
        style_sheet = str()
        style_sheet += "QProgressBar { background-color: " + background + "; border-radius: 0px; }"
        style_sheet += "QProgressBar::chunk { background-color: " + percentage + "; }"
        return style_sheet

    # Theme
    def Style_Icon( self ):
        # Variables
        ki = Krita.instance()
        # Vector
        icon_select_tool = ki.icon( "select" )
        icon_text_tool = ki.icon( "draw-text" )
        icon_edit_tool = ki.icon( "shape_handling" )
        icon_calligraphy_tool = ki.icon( "calligraphy" )
        # Brush
        icon_freehand_brush = ki.icon( "krita_tool_freehand" )
        icon_line_brush = ki.icon( "krita_tool_line" )
        icon_rectangle_brush = ki.icon( "krita_tool_rectangle" )
        icon_ellipse_brush = ki.icon( "krita_tool_ellipse" )
        icon_polygon_brush = ki.icon( "krita_tool_polygon" )
        icon_polyline_brush = ki.icon( "polyline" )
        icon_bezier_brush = ki.icon( "krita_draw_path" )
        icon_path_brush = ki.icon( "krita_tool_freehandvector" )
        icon_dynamic_brush = ki.icon( "krita_tool_dyna" )
        icon_multi_brush = ki.icon( "krita_tool_multihand" )
        # Transform
        icon_transform_tool = ki.icon( "krita_tool_transform" )
        icon_move_tool = ki.icon( "krita_tool_move" )
        icon_crop_tool = ki.icon( "tool_crop" )
        # Color
        icon_gradient_tool = ki.icon( "krita_tool_gradient" )
        icon_sampler_tool = ki.icon( "krita_tool_color_sampler" )
        icon_colorize_tool = ki.icon( "krita_tool_lazybrush" )
        icon_patch_tool = ki.icon( "krita_tool_smart_patch" )
        icon_fill_tool = ki.icon( "krita_tool_color_fill" )
        icon_enclose_tool = ki.icon( "krita_tool_enclose_and_fill" )
        # Overlay
        icon_assistant_tool = ki.icon( "krita_tool_assistant" )
        icon_measure_tool = ki.icon( "krita_tool_measure" )
        icon_reference_tool = ki.icon( "krita_tool_reference_images" )
        # Select
        icon_rectangle_select = ki.icon( "tool_rect_selection" )
        icon_elliptical_select = ki.icon( "tool_elliptical_selection" )
        icon_polygon_select = ki.icon( "tool_polygonal_selection" )
        icon_freehand_select = ki.icon( "tool_outline_selection")
        icon_contiguous_select = ki.icon( "tool_contiguous_selection" )
        icon_color_select = ki.icon( "tool_similar_selection")
        icon_bezier_select = ki.icon( "tool_path_selection")
        icon_magnetic_select = ki.icon( "tool_magnetic_selection" )
        # Camera
        icon_zoom_tool = ki.icon( "tool_zoom" )
        icon_pan_tool = ki.icon( "tool_pan" )
        # Mirror Fix
        self.icon_mirrorfix = "wraparound"

        # Toolbox ( name, pykrita, qicon ) — refresh icons on the shared catalog;
        # every group references these list objects, so primaries update too.
        self.tool_catalog["select_tool"][2]       = icon_select_tool
        self.tool_catalog["text_tool"][2]         = icon_text_tool
        self.tool_catalog["edit_tool"][2]         = icon_edit_tool
        self.tool_catalog["calligraphy_tool"][2]  = icon_calligraphy_tool
        # Brush
        self.tool_catalog["freehand_brush"][2]     = icon_freehand_brush
        self.tool_catalog["line_brush"][2]         = icon_line_brush
        self.tool_catalog["rectangle_brush"][2]    = icon_rectangle_brush
        self.tool_catalog["ellipse_brush"][2]      = icon_ellipse_brush
        self.tool_catalog["polygon_brush"][2]      = icon_polygon_brush
        self.tool_catalog["polyline_brush"][2]     = icon_polyline_brush
        self.tool_catalog["bezier_brush"][2]       = icon_bezier_brush
        self.tool_catalog["path_brush"][2]         = icon_path_brush
        self.tool_catalog["dynamic_brush"][2]      = icon_dynamic_brush
        self.tool_catalog["multi_brush"][2]        = icon_multi_brush
        # Transform
        self.tool_catalog["transform_tool"][2] = icon_transform_tool
        self.tool_catalog["move_tool"][2]      = icon_move_tool
        self.tool_catalog["crop_tool"][2]      = icon_crop_tool
        # Color
        self.tool_catalog["gradient_tool"][2]      = icon_gradient_tool
        self.tool_catalog["sampler_tool"][2]       = icon_sampler_tool
        self.tool_catalog["colorize_tool"][2]      = icon_colorize_tool
        self.tool_catalog["patch_tool"][2]         = icon_patch_tool
        self.tool_catalog["fill_tool"][2]          = icon_fill_tool
        self.tool_catalog["enclose_tool"][2]       = icon_enclose_tool
        # Overlay
        self.tool_catalog["assistant_tool"][2]   = icon_assistant_tool
        self.tool_catalog["measure_tool"][2]     = icon_measure_tool
        self.tool_catalog["reference_tool"][2]   = icon_reference_tool
        # Select
        self.tool_catalog["rectangle_select"][2]  = icon_rectangle_select
        self.tool_catalog["elliptical_select"][2] = icon_elliptical_select
        self.tool_catalog["polygon_select"][2]    = icon_polygon_select
        self.tool_catalog["freehand_select"][2]   = icon_freehand_select
        self.tool_catalog["contiguous_select"][2] = icon_contiguous_select
        self.tool_catalog["color_select"][2]      = icon_color_select
        self.tool_catalog["bezier_select"][2]     = icon_bezier_select
        self.tool_catalog["magnetic_select"][2]   = icon_magnetic_select
        # Camera
        self.tool_catalog["zoom_tool"][2]         = icon_zoom_tool
        self.tool_catalog["pan_tool"][2]          = icon_pan_tool

        # Tool Box — each primary shows its currently active tool's icon.
        for gid in self.group_ids:
            self.primary[gid].setIcon( self.tool_catalog[self.index[gid]][2] )
        # Actions
        self.menu_mirror_fix.setIcon(    ki.icon( self.icon_mirrorfix )   )
        if self.pigmento_picker != None: self.menu_color_picker.setIcon( ki.icon( "krita_tool_ellipse" ) )
        else:                            self.menu_color_picker.setIcon( ki.icon( "close-tab" ) )
        # Hide
        self.menu_tela.setIcon(             ki.icon( "arrow-up" ) )
    def Style_Theme( self ):
        # Read
        palette = QApplication.palette()
        base = palette.base().color()
        # Window
        w_alternate     = palette.alternateBase().color().name()
        w_base          = palette.base().color().name()
        w_button        = palette.button().color().name()
        w_dark          = palette.dark().color().name()
        w_light         = palette.light().color().name()
        w_mid           = palette.mid().color().name()
        w_midlight      = palette.midlight().color().name()
        w_shadow        = palette.shadow().color().name()
        w_tool_tip      = palette.toolTipBase().color().name()
        w_window        = palette.window().color().name()
        # Text
        t_bright        = palette.brightText().color().name()
        t_button        = palette.buttonText().color().name()
        t_highlighted   = palette.highlightedText().color().name()
        t_placeholder   = palette.placeholderText().color().name()
        t_text          = palette.text().color().name()
        t_tool_tip      = palette.toolTipText().color().name()
        t_window        = palette.windowText().color().name()
        # Color
        c_highlight     = palette.highlight().color().name()
        c_link          = palette.link().color().name()
        c_visited       = palette.linkVisited().color().name()
        # c_accent        = palette.accent().color().name() # qt6
        a_black       = "#00000000"

        # Colors
        win = palette.window().color().getHsvF()
        hue = palette.highlight().color().getHsvF()
        but = palette.button().color().getHsvF()
        if win[2] > 0.5:    h3 = -0.3; p3 = -0.1 # Light Theme
        else:               h3 = +0.3; p3 = +0.1 # Dark Theme
        handle   = QColor().fromHsvF( but[0], but[1], but[2] + h3 ).name()
        page     = QColor().fromHsvF( but[0], but[1], but[2] + p3 ).name()
        # QPushbuttons — main row
        self.Interface_Highlight( self.menu_krita,        "menu_krita",        c_highlight, t_bright )
        for gid in self.group_ids:
            self.Interface_Highlight( self.primary[gid], "primary_" + gid, c_highlight, t_bright )
        self.Interface_Highlight( self.menu_break,        "menu_break",        c_highlight, t_bright )
        # Remember these palette colors so fly-out buttons can be styled to match.
        self._hl_highlight = c_highlight
        self._hl_text = t_bright
        # Progress Bar
        progress_bar_style_sheet = self.ProgressBar_StyleSheet( c_highlight, a_black )
        self.progress_bar.setStyleSheet( progress_bar_style_sheet )
        # Extras
        self.Interface_Highlight( self.menu_mirror_fix,   "menu_mirror_fix",   c_highlight, t_bright )
        self.Interface_Highlight( self.menu_color_picker, "menu_color_picker", c_highlight, t_bright )
        # Sub-panel — Transform
        self.Interface_Highlight( self.spt_free,          "spt_free",          c_highlight, t_bright )
        self.Interface_Highlight( self.spt_perspective,   "spt_perspective",   c_highlight, t_bright )
        self.Interface_Highlight( self.spt_warp,          "spt_warp",          c_highlight, t_bright )
        self.Interface_Highlight( self.spt_cage,          "spt_cage",          c_highlight, t_bright )
        self.Interface_Highlight( self.spt_liquify,       "spt_liquify",       c_highlight, t_bright )
        self.Interface_Highlight( self.spt_mesh,          "spt_mesh",          c_highlight, t_bright )
        # Sub-panel — Select
        self.Interface_Highlight( self.sps_invert,        "sps_invert",        c_highlight, t_bright )
        self.Interface_Highlight( self.sps_all,           "sps_all",           c_highlight, t_bright )
        self.Interface_Highlight( self.sps_none,          "sps_none",          c_highlight, t_bright )
        # Hide
        self.Interface_Highlight( self.menu_tela,         "menu_tela",         c_highlight, t_bright )

        # Color_Picker
        self.Interface_Slider( self.color_picker.s1, handle, w_mid, page, page )
        self.Interface_Slider( self.color_picker.s2, handle, w_mid, page, page )
        self.Interface_Slider( self.color_picker.s3, handle, w_mid, page, page )
        self.color_picker.setStyleSheet( "#color_picker{ background-color: " + w_button + "; }" )

    #endregion
    #region Widgets

    # Toolbox
    def Toolbox_Display( self ):
        # Main Window
        self.stacked_widget = self.window.qwindow().centralWidget()
        self.qmdiarea = self.stacked_widget.findChild( QMdiArea )

        # Display — overlays are created with no parent for now; Canvas_Changed
        # attaches them to the active document's canvas widget. In Krita 6 the
        # canvas (QOpenGLWidget) is a native OS window that captures clicks
        # for its region, so the overlays MUST be its children (not siblings)
        # to receive mouse events.
        self.Interface_Create( None )
        # Color Picker
        self.color_picker.hide()

        # Reparent overlays onto the active subwindow's canvas, and swap them
        # over whenever the user switches documents.
        self.qmdiarea.subWindowActivated.connect( self.Canvas_Changed )
        self.Canvas_Changed( self.qmdiarea.activeSubWindow() )

        # Apply the theme stylesheet now; otherwise the buttons stay
        # un-styled until the user switches view or theme.
        self.Style_Theme()
        # Progress Bar
        self.krita_progress_bar = self.window.qwindow().statusBar().findChild( QProgressBar )
        self.krita_progress_bar.valueChanged.connect( self.Progress_Bar )

        # Import Pigment.o module
        if self.pigmento_picker == None:
            self.Import_Pigment_O()
    def Toolbox_Button( self ):
        qwindow = Krita.instance().activeWindow().qwindow()
        # Krita's native tool buttons, keyed by our tool id ( over the whole
        # catalog, independent of grouping ). Used to read the active tool.
        self.krita_button = dict()
        for key, meta in self.tool_catalog.items():
            self.krita_button[key] = qwindow.findChild( QToolButton, meta[1] )
    def Toolbox_Filter_Install( self ):
        # Variables
        app = QApplication.instance()
        list_widget = app.allWidgets()
        # Watch every tool in the catalog, whether or not it is currently grouped.
        list_key = [ meta[1] for meta in self.tool_catalog.values() ]
        # Cycle
        for widget in list_widget:
            name = widget.objectName()
            if name in list_key:
                self.krita_toolbox.append( widget )
                widget.installEventFilter( self )
    def Toolbox_Load( self ):
        # Kritarc
        show_option = self.Kritarc_Read( EXTENSION_NAME, "show_option", self.show_option, eval )
        show_extra  = self.Kritarc_Read( EXTENSION_NAME, "show_extra",  self.show_extra,  eval )
        hide_tela   = self.Kritarc_Read( EXTENSION_NAME, "hide_tela",   self.hide_tela,   eval )
        # Tela Button
        self.menu_tela.blockSignals( True )
        self.menu_tela.setChecked( hide_tela )
        self.menu_tela.blockSignals( False )
        # Geometry
        self.Tela_Geometry( show_option, show_extra, hide_tela )
    # Tool
    def Tool_Update( self ):
        # Canvas
        check_canvas = self.Check_Canvas()
        if check_canvas == True:
            # Find which catalog tool Krita currently has active ( exclusive,
            # so at most one ), then reflect it on its group's primary button.
            active_key = None
            for key, button in self.krita_button.items():
                try:
                    if button.isChecked():
                        active_key = key
                        break
                except:
                    pass
            if active_key is not None:
                gid = self.Group_Of_Tool( active_key )
                if gid is not None:
                    self.Tool_Apply( gid, active_key )
            # Clean
            self.Tela_Geometry( self.show_option, self.show_extra, self.hide_tela )
    def Tool_Apply( self, gid, tool ):
        # Reflect the active tool on its group's primary button.
        self.index[gid] = tool
        self.operation[gid] = self.tool_catalog[tool][1]
        self.primary[gid].setIcon( self.tool_catalog[tool][2] )
        self.primary[gid].setChecked( True )

    # Interface
    def Interface_Create( self, parent ):
        #region Widgets

        # Variables
        bar = ( self.pba * 7 ) + ( self.pbs * 6 )

        # Tool Box — one primary button per configured group ( variable count ).
        self.menu_krita        = QPushButton( "menu_krita", parent )
        self.primary = dict()
        for gid in self.group_ids:
            self.primary[gid] = QPushButton( "primary_" + gid, parent )
        self.menu_break        = QPushButton( "menu_break", parent )
        # Progress Bar
        self.progress_bar      = QProgressBar( parent )
        # Extras
        self.menu_mirror_fix   = QPushButton( "menu_mirror_fix", parent )
        self.menu_color_picker = QPushButton( "menu_color_picker", parent )
        # Transform
        self.spt_free          = QPushButton( "spt_free", parent )
        self.spt_perspective   = QPushButton( "spt_perspective", parent )
        self.spt_warp          = QPushButton( "spt_warp", parent )
        self.spt_cage          = QPushButton( "spt_cage", parent )
        self.spt_liquify       = QPushButton( "spt_liquify", parent )
        self.spt_mesh          = QPushButton( "spt_mesh", parent )
        # Select
        self.sps_invert        = QPushButton( "sps_invert", parent )
        self.sps_all           = QPushButton( "sps_all", parent )
        self.sps_none          = QPushButton( "sps_none", parent )
        # Hide
        self.menu_tela         = QPushButton( "hide", parent )

        # Tool Box
        self.Interface_Push_Button(  self.menu_krita,        "menu_krita",        self.pbc, self.pba, False, False, False )
        for gid in self.group_ids:
            self.Interface_Push_Button( self.primary[gid], "primary_" + gid, self.pba, self.pba, True, True, False )
        self.Interface_Push_Button(  self.menu_break,        "menu_break",        self.pbc, self.pba, False, False, False )
        # Progress Bar
        self.Interface_Progress_Bar( self.progress_bar,      "progress_bar",      bar,      self.pbs )
        # Extras
        self.Interface_Push_Button(  self.menu_mirror_fix,   "menu_mirror_fix",   self.pba, self.pba, False, False, False )
        self.Interface_Push_Button(  self.menu_color_picker, "menu_color_picker", self.pba, self.pba, False, False, False )
        # Transform
        self.Interface_Push_Button(  self.spt_free,          "spt_free",          self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_perspective,   "spt_perspective",   self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_warp,          "spt_warp",          self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_cage,          "spt_cage",          self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_liquify,       "spt_liquify",       self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_mesh,          "spt_mesh",          self.pba, self.pbb, False, False, False )
        # Select
        self.Interface_Push_Button(  self.sps_invert,        "sps_invert",        self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.sps_all,           "sps_all",           self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.sps_none,          "sps_none",          self.pba, self.pbb, False, False, False )
        # Hide
        self.Interface_Push_Button(  self.menu_tela,         "menu_tela",         50,       self.pbc, True,  False, True  )

        #endregion
        #region Connections

        # Krita Menu
        self.menu_krita.pressed.connect( self.Hold_Krita )
        self.menu_krita.released.connect( self.Release_Krita )
        # Primaries — hold reveals the group fly-out; click/release picks the primary.
        for gid in self.group_ids:
            self.primary[gid].pressed.connect(  lambda g=gid: self.Hold_Primary( g ) )
            self.primary[gid].released.connect( lambda g=gid: self.Release_Primary( g ) )
        # Break
        self.menu_break.pressed.connect( self.Hold_Break )
        self.menu_break.released.connect( self.Release_Break )
        # Transform
        self.spt_free.clicked.connect( self.Transform_Free )
        self.spt_perspective.clicked.connect( self.Transform_Perspective )
        self.spt_warp.clicked.connect( self.Transform_Warp )
        self.spt_cage.clicked.connect( self.Transform_Cage )
        self.spt_liquify.clicked.connect( self.Transform_Liquify )
        self.spt_mesh.clicked.connect( self.Transform_Mesh )
        # Select
        self.sps_invert.clicked.connect( self.Select_Invert )
        self.sps_all.clicked.connect( self.Select_All )
        self.sps_none.clicked.connect( self.Select_None )
        # Extra Color Picker
        self.menu_color_picker.clicked.connect( self.Show_Color_Picker )
        self.color_picker.s1.valueChanged.connect(   lambda: self.CS1_W( False ) )
        self.color_picker.s1.sliderReleased.connect( lambda: self.CS1_W( True ) )
        self.color_picker.s2.valueChanged.connect(   lambda: self.CS2_W( False ) )
        self.color_picker.s2.sliderReleased.connect( lambda: self.CS2_W( True ) )
        self.color_picker.s3.valueChanged.connect(   lambda: self.CS3_W( False ) )
        self.color_picker.s3.sliderReleased.connect( lambda: self.CS3_W( True ) )
        # Hide
        self.menu_tela.toggled.connect( self.Hide_Tela )

        # User Interface Update
        self.color_picker.installEventFilter( self )

        #endregion
        #region Modules

        self.mirror_fix = MirrorFix_Button( self.menu_mirror_fix )
        self.mirror_fix.SIGNAL_SIDE.connect( self.MirrorFix_Side )
        self.mirror_fix.SIGNAL_NEUTRAL.connect( self.MirrorFix_Explanation )

        #endregion
        #region Style

        # Krita Instance
        ki = Krita.instance()
        # Tool Box
        self.menu_krita.setIcon(        ki.icon( "hamburger_menu_dots" ) )
        for gid in self.group_ids:
            self.primary[gid].setIcon( self.tool_catalog[self.index[gid]][2] )
        self.menu_break.setIcon(        ki.icon( "hamburger_menu_dots" ) )
        # Transform
        self.spt_free.setIcon(          ki.icon( "transform_icons_main" ) )
        self.spt_perspective.setIcon(   ki.icon( "transform_icons_perspective" ) )
        self.spt_warp.setIcon(          ki.icon( "transform_icons_warp" ) )
        self.spt_cage.setIcon(          ki.icon( "transform_icons_cage" ) )
        self.spt_liquify.setIcon(       ki.icon( "transform_icons_liquify_main" ) )
        self.spt_mesh.setIcon(          ki.icon( "transform_icons_mesh" ) )
        # Select
        self.sps_invert.setIcon(        ki.icon( "select-invert" ) )
        self.sps_all.setIcon(           ki.icon( "select-all" ) )
        self.sps_none.setIcon(          ki.icon( "select-clear" ) )
        # Progress Bar
        self.progress_bar.setStyleSheet( "#progress_bar{ background-color: rgba( 0, 0, 0, 0 ); }" )
        # Actions
        self.menu_mirror_fix.setIcon(   ki.icon( self.icon_mirrorfix )   )
        self.menu_color_picker.setIcon( ki.icon( "close-tab" ) )
        # Hide
        self.menu_tela.setIcon( ki.icon( "arrow-up" ) )

        #endregion
    def Interface_Push_Button( self, button, name, pw, ph, check, exclusive, flat ):
        # Variables
        qsize = QSize( pw, ph )
        # QWidget
        button.setObjectName( name )
        button.setSizePolicy( QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed )
        button.setMinimumSize( qsize )
        button.setMaximumSize( qsize )
        button.setFocusPolicy( Qt.FocusPolicy.NoFocus )
        button.setCursor( Qt.CursorShape.PointingHandCursor )
        # QAbstract Button
        button.setText( "" )
        button.setCheckable( check )
        button.setAutoExclusive( exclusive )
        # QPushbutton — flat / borderless; the actual circular shape and
        # state colors are applied via stylesheet in Interface_Highlight.
        button.setFlat( True )
    def Interface_Progress_Bar( self, progress, name, pw, ph ):
        # Variables
        qsize = QSize( pw, ph )
        # QWidget
        progress.setObjectName( name )
        progress.setSizePolicy( QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed )
        progress.setMinimumSize( qsize )
        progress.setMaximumSize( qsize )
        progress.setFocusPolicy( Qt.FocusPolicy.NoFocus )
        # Pure status indicator — let clicks fall through to the buttons
        # underneath (the bar spans the full row width and would otherwise
        # eat any pixel where it overlaps a button edge).
        progress.setAttribute( Qt.WidgetAttribute.WA_TransparentForMouseEvents, True )
        # QProgress Bar
        progress.setMinimum( 0 )
        progress.setMaximum( 99 )
        progress.setValue( 0 )
        progress.setTextVisible( False )
    def Interface_Highlight( self, button, name, background, pen ):
        # Flat, circular, with six interaction states:
        #   inactive / hovered / clicked / active / active-hovered / active-clicked
        # The resting backdrop uses the theme's button colour at reduced
        # opacity so white-on-dark and dark-on-light icons both keep contrast
        # against arbitrary canvas content. Active states use the theme
        # highlight; active-clicked is darker than active so the long-press
        # interaction feels responsive even on an already-active tool.
        palette = QApplication.palette()
        btn = palette.button().color()
        h = QColor( background )
        r = min( button.minimumWidth(), button.minimumHeight() ) // 2

        # Rule: hover = a touch brighter, click = a touch darker. Same alpha
        # everywhere so the toolbar reads as one consistent translucent layer.
        alpha = 255
        def rgba( c ):
            return "rgba({0},{1},{2},{3})".format( c.red(), c.green(), c.blue(), alpha )

        inactive_bg       = rgba( btn )
        hovered_bg        = rgba( btn.lighter( 120 ) )
        clicked_bg        = rgba( btn.darker( 120 ) )
        active_bg         = rgba( h )
        active_hovered_bg = rgba( h.lighter( 120 ) )
        active_clicked_bg = rgba( h.darker( 120 ) )

        n = str( name )
        button.setStyleSheet(
            "#" + n + "{ background-color: " + inactive_bg + "; border: none; border-radius: " + str( r ) + "px; }"
            "#" + n + ":hover{ background-color: " + hovered_bg + "; }"
            "#" + n + ":pressed{ background-color: " + clicked_bg + "; }"
            "#" + n + ":checked{ background-color: " + active_bg + "; }"
            "#" + n + ":checked:hover{ background-color: " + active_hovered_bg + "; }"
            "#" + n + ":checked:pressed{ background-color: " + active_clicked_bg + "; }"
        )
    def Interface_Slider( self, widget, handle, border, page_sub, page_add ):
        style_sheet = str()
        style_sheet += "QSlider::groove:horizontal { border: 1px solid; height: 2px; }"
        style_sheet += "QSlider::handle:horizontal { background-color: " + handle + "; width: 10px; height: 10px; margin: -5px 2px; border: 1px solid " + border + "; border-radius: 5px; }"
        style_sheet += "QSlider::sub-page:horizontal { background-color: " + page_sub + "; }" # Left Side
        style_sheet += "QSlider::add-page:horizontal { background-color: " + page_add + "; }" # Right Side
        widget.setStyleSheet( style_sheet )

    # Canvas attachment
    def Overlay_Widgets( self ):
        return [
            self.menu_krita,
            *[ self.primary[gid] for gid in self.group_ids ],
            self.menu_break,
            self.progress_bar,
            self.menu_mirror_fix, self.menu_color_picker,
            self.spt_free, self.spt_perspective, self.spt_warp,
            self.spt_cage, self.spt_liquify, self.spt_mesh,
            self.sps_invert, self.sps_all, self.sps_none,
            self.menu_tela,
            self.color_picker,
            ]
    def Canvas_Changed( self, sub ):
        # Stop watching the previous canvas widget
        if self.canvas_widget is not None:
            self.canvas_widget.removeEventFilter( self )
            self.canvas_widget = None

        # No document open — detach overlays so they don't dangle
        if sub is None:
            for w in self.Overlay_Widgets():
                w.setParent( None )
                w.hide()
            return

        # Find the canvas widget inside this subwindow. Prefer QOpenGLWidget
        # (the standard OpenGL canvas); fall back to the first QWidget child
        # that contains the rendering area for the QPainter canvas path.
        canvas = sub.findChild( QOpenGLWidget )
        if canvas is None:
            scroll = sub.findChild( QAbstractScrollArea )
            canvas = scroll.viewport() if scroll is not None else sub
        self.canvas_widget = canvas
        self.canvas_widget.installEventFilter( self )

        # Reparent every overlay onto the canvas. setParent() implicitly hides
        # the widget, so we re-show after positioning.
        for w in self.Overlay_Widgets():
            w.setParent( self.canvas_widget )
        self.color_picker.hide()
        self.Tela_Geometry( self.show_option, self.show_extra, self.hide_tela )
        for w in self.Overlay_Widgets():
            if w is self.color_picker:
                continue
            w.show()
            w.raise_()

    # Geometry
    def Size_Update( self ):
        if self.canvas_widget != None:
            # Size
            wcp = self.color_picker
            pw = wcp.width()
            ph = wcp.height()
            # Position
            qpoint = self.menu_color_picker.geometry().topLeft()
            px = qpoint.x()
            py = qpoint.y() - ph - self.my
            # Geometry
            self.Tela_Geometry( self.show_option, self.show_extra, self.hide_tela )
            self.Picker_Geometry( px, py, pw, ph )
    # Tela Geometry
    def Show_Option( self, boolean ):
        self.Tela_Geometry( boolean, self.show_extra, self.hide_tela )
        self.Kritarc_Write( EXTENSION_NAME, "show_option", boolean )
    def Show_Extra( self, boolean ):
        self.Tela_Geometry( self.show_option, boolean, self.hide_tela )
        self.Kritarc_Write( EXTENSION_NAME, "show_extra", boolean )
    def Hide_Tela( self, boolean ):
        self.Tela_Geometry( self.show_option, self.show_extra, boolean )
        if boolean == True:
            self.color_picker.hide()
        self.Kritarc_Write( EXTENSION_NAME, "hide_tela", boolean )
    def Tela_Geometry( self, show_option, show_extra, hide_tela ):
        # Size Update
        self.show_option = show_option
        self.show_extra = show_extra
        self.hide_tela = hide_tela

        # Geormetry
        if self.canvas_widget != None:
            # Canvas
            qmd_w = self.canvas_widget.width()
            qmd_h = self.canvas_widget.height()
            # Levels
            l0 = 103
            l1 = 61
            l2 = 56
            l3 = 25
            # Variables
            short = 20
            wide = 50
            # Calculations
            step = self.pba + self.pbs
            n = len( self.group_ids )
            # Sub-panel widths are fixed ( 6 transform modes, 3 select ops ).
            w3 = ( self.pba * 3 ) + ( self.pbs * 2 )
            w6 = ( self.pba * 6 ) + ( self.pbs * 5 )
            px3 = qmd_w * 0.5 - w3 * 0.5
            px6 = qmd_w * 0.5 - w6 * 0.5
            # Primary row: width scales with the number of configured primaries.
            bar_w = ( self.pba * n ) + ( self.pbs * ( n - 1 ) ) if n > 0 else 0
            px = qmd_w * 0.5 - bar_w * 0.5
            offscreen = 100
            dh = int( hide_tela * offscreen )
            # Which primary ( if any ) is currently active, and its tool.
            active_tool = None
            for gid in self.group_ids:
                if self.primary[gid].isChecked():
                    active_tool = self.index[gid]
                    break
            # Sub Panel Transform — shown when the Transform tool itself is active.
            check_transform = self.show_option == True and active_tool == "transform_tool"
            if check_transform == True:     dt = dh
            else:                           dt = offscreen
            # Sub Panel Select — shown when any selection tool is active.
            select_tools = [ k for k in self.tool_catalog if k.endswith( "_select" ) ]
            check_select = self.show_option == True and active_tool in select_tools
            if check_select == True:        ds = dh
            else:                           ds = offscreen
            # Extra
            if self.show_extra == True:    de = dh
            else:                           de = offscreen

            # Tool Box — krita button, then N primaries, then break; row centered.
            self.menu_krita.setGeometry(        int( px - self.pbc*1 - self.pbs*1 ), int( qmd_h-l0+dh ),    self.pbc,  self.pba )
            for i, gid in enumerate( self.group_ids ):
                self.primary[gid].setGeometry( int( px + step*i ), int( qmd_h-l0+dh ), self.pba, self.pba )
            self.menu_break.setGeometry(        int( px + step*n ),                 int( qmd_h-l0+dh ),    self.pbc,  self.pba )
            # Progress Bar
            self.progress_bar.setGeometry(      int( px ),                          int( qmd_h-l1+dh ),    int( bar_w ), self.pbs )
            # Extras
            self.menu_mirror_fix.setGeometry(   int( px + step*(n+1) ),             int( qmd_h-l0+de ),    self.pba,  self.pba )
            self.menu_color_picker.setGeometry( int( px + step*(n+2) ),             int( qmd_h-l0+de ),    self.pba,  self.pba )
            # Transform
            self.spt_free.setGeometry(          int( px6 ),                           int( qmd_h-l2+dt ),    self.pba,  self.pbb )
            self.spt_perspective.setGeometry(   int( px6 + self.pba*1 + self.pbs*1 ), int( qmd_h-l2+dt ),    self.pba,  self.pbb )
            self.spt_warp.setGeometry(          int( px6 + self.pba*2 + self.pbs*2 ), int( qmd_h-l2+dt ),    self.pba,  self.pbb )
            self.spt_cage.setGeometry(          int( px6 + self.pba*3 + self.pbs*3 ), int( qmd_h-l2+dt ),    self.pba,  self.pbb )
            self.spt_liquify.setGeometry(       int( px6 + self.pba*4 + self.pbs*4 ), int( qmd_h-l2+dt ),    self.pba,  self.pbb )
            self.spt_mesh.setGeometry(          int( px6 + self.pba*5 + self.pbs*5 ), int( qmd_h-l2+dt ),    self.pba,  self.pbb )
            # Select
            self.sps_invert.setGeometry(        int( px3 ),                           int( qmd_h-l2+ds ),    self.pba,  self.pbb )
            self.sps_all.setGeometry(           int( px3 + self.pba*1 + self.pbs*1 ), int( qmd_h-l2+ds ),    self.pba,  self.pbb )
            self.sps_none.setGeometry(          int( px3 + self.pba*2 + self.pbs*2 ), int( qmd_h-l2+ds ),    self.pba,  self.pbb )
            # Hide
            self.menu_tela.setGeometry(         int( qmd_w*0.5-wide*0.5 ),            int( qmd_h-self.pbc ), wide,      self.pba )
    # Picker Geometry
    def Picker_to_Cursor( self ):
        if self.canvas_widget != None:
            # Cursor
            position = QCursor().pos()
            cx = position.x()
            cy = position.y()
            # Canvas
            delta = self.canvas_widget.mapFromGlobal( QPoint( 0, 0 ) )
            dx = delta.x()
            dy = delta.y()
            # Widget
            widget = self.color_picker
            ww = widget.width()
            wh = widget.height()
            # Color Panel
            colorpanel = self.color_picker.color_panel
            cpx = colorpanel.x()
            cpy = colorpanel.y()
            cpw = colorpanel.width()
            cph = colorpanel.height()
            cp_cx = cpw * self.s2
            cp_cy = cph - cph * self.s3
            cp_cx = self.Limit_Range( int( cp_cx ), 0, cpw, 0, -1 )
            cp_cy = self.Limit_Range( int( cp_cy ), 0, cph, 0, -1 )

            # Relocate Color Picker
            self.Picker_Geometry( cx+dx-cpx-cp_cx, cy+dy-cpy-cp_cy, ww, wh )
            # Toggle Visibility
            check_visible = self.color_picker.isVisible()
            if check_visible == False:
                self.color_picker.setVisible( True )
            else:
                self.color_picker.setVisible( False )
    def Picker_Geometry( self, px, py, ww, wh ):
        self.color_picker.setGeometry( int( px ), int( py ), int( ww ), int( wh ) )

    #endregion
    #region ToolBox

    # Krita
    def Hold_Krita( self ):
        self.Menu_Reset()
        self.Menu_Timer_Start( self.Menu_Krita )
    def Release_Krita( self ):
        self.Menu_Reset()
    def Menu_Krita( self ):
        # Variables
        widget = self.menu_krita
        ki = Krita.instance()
        ad = ki.activeDocument()

        # Read State
        view_docker_ui = ki.action( "view_toggledockers" ).isChecked()
        # Read Layer
        layer_isolate = ki.action( "isolate_active_layer" ).isChecked()
        # Read Canvas
        canvas_mirror = ki.action( "mirror_canvas" ).isChecked()
        canvas_wrap = ki.action( "wrap_around_mode" ).isChecked()
        canvas_grid = ki.action( "view_pixel_grid" ).isChecked()
        # Read Guides
        guides_ruler = ki.action( "view_ruler" ).isChecked()
        guides_snap = ki.action( "view_snap_to_guides" ).isChecked()
        guides_show = ad.guidesVisible()
        guides_lock = ad.guidesLocked()
        # Read View
        view_painting_assistant = ki.action( "view_toggle_painting_assistants" ).isChecked()
        view_assitant_preview = ki.action( "view_toggle_assistant_previews" ).isChecked()
        view_reference_image = ki.action( "view_toggle_reference_images" ).isChecked()

        # Menu
        self.qmenu = QMenu()

        # State
        action_view_docker_ui = self.qmenu.addAction( "View Docker UI" )
        action_view_docker_ui.setCheckable( True )
        action_view_docker_ui.setChecked( view_docker_ui )
        # Layers
        action_layer_isolate = self.qmenu.addAction( "Layer Isolate" )
        action_layer_isolate.setCheckable( True )
        action_layer_isolate.setChecked( layer_isolate )
        # Canvas
        menu_canvas = self.qmenu.addMenu( "Canvas" )
        action_canvas_mirror = menu_canvas.addAction( "Mirror" )
        action_canvas_wrap = menu_canvas.addAction( "Wrap" )
        action_canvas_mirror.setCheckable( True )
        action_canvas_wrap.setCheckable( True )
        action_canvas_mirror.setChecked( canvas_mirror )
        action_canvas_wrap.setChecked( canvas_wrap )
        # Guides
        menu_guides = self.qmenu.addMenu( "Guides" )
        action_guides_ruler = menu_guides.addAction( "Ruler" )
        action_guides_snap = menu_guides.addAction( "Snap" )
        action_guides_show = menu_guides.addAction( "Show" )
        action_guides_lock = menu_guides.addAction( "Lock" )
        action_guides_ruler.setCheckable( True )
        action_guides_snap.setCheckable( True )
        action_guides_show.setCheckable( True )
        action_guides_lock.setCheckable( True )
        action_guides_ruler.setChecked( guides_ruler )
        action_guides_snap.setChecked( guides_snap )
        action_guides_show.setChecked( guides_show )
        action_guides_lock.setChecked( guides_lock )
        # View
        menu_view = self.qmenu.addMenu( "View" )
        action_view_painting_assistant = menu_view.addAction( "Painting Assistant" )
        action_view_assitant_preview = menu_view.addAction( "Assistant Preview" )
        action_view_reference_image = menu_view.addAction( "Reference Image" )
        action_view_painting_assistant.setCheckable( True )
        action_view_assitant_preview.setCheckable( True )
        action_view_reference_image.setCheckable( True )
        action_view_painting_assistant.setChecked( view_painting_assistant )
        action_view_assitant_preview.setChecked( view_assitant_preview )
        action_view_reference_image.setChecked( view_reference_image )
        # Selection
        action_selection_overlay_mode = self.qmenu.addAction( "Selection Overlay Mode" )

        # Mapping
        item = 6
        size = 23  # 23 is the expected height of a self.qmenu item on windows at least
        height = size * item + self.my
        qpoint = widget.geometry().topLeft()
        pos = self.canvas_widget.mapToGlobal( qpoint )
        point = QPoint( pos.x(), pos.y() - height )
        action = self.qmenu.exec( point )

        # State
        if action == action_view_docker_ui:             self.View_Docker_UI()
        # Layers
        if action == action_layer_isolate:              self.Layer_Isolate()
        # Canvas
        if action == action_canvas_mirror:              self.Canvas_Mirror()
        if action == action_canvas_wrap:                self.Canvas_Wrap()
        # Guides
        if action == action_guides_ruler:               self.Guides_Ruler()
        if action == action_guides_snap:                self.Guides_Snap()
        if action == action_guides_show:                self.Guides_Show()
        if action == action_guides_lock:                self.Guides_Lock()
        # View
        if action == action_view_painting_assistant:    self.View_Painting_Assistant()
        if action == action_view_assitant_preview:      self.View_Assistant_Preview()
        if action == action_view_reference_image:       self.View_Reference_Image()
        # Selection
        if action == action_selection_overlay_mode:     self.Selection_Overlay_Mode()

        # Clean up
        self.Menu_Down()
    # Break
    def Hold_Break( self ):
        self.Menu_Reset()
        self.Menu_Timer_Start( self.Menu_Break )
    def Release_Break( self ):
        self.Menu_Reset()
    def Menu_Break( self ):
        # Variables
        widget = self.menu_break
        # Menu
        self.qmenu = QMenu()
        # State
        action_show_option = self.qmenu.addAction( "Show Option" )
        action_show_option.setCheckable( True )
        action_show_option.setChecked( self.show_option )
        # Layers
        action_show_extra = self.qmenu.addAction( "Show Extra" )
        action_show_extra.setCheckable( True )
        action_show_extra.setChecked( self.show_extra )
        # Configure
        self.qmenu.addSeparator()
        action_configure = self.qmenu.addAction( "Configure Toolbox..." )
        # Mapping
        item = 3
        size = 23  # 23 is the expected height of a self.qmenu item on windows at least
        height = size * item + self.my
        qpoint = widget.geometry().topLeft()
        pos = self.canvas_widget.mapToGlobal( qpoint )
        point = QPoint( pos.x(), pos.y() - height )
        action = self.qmenu.exec( point )
        # State
        if action == action_show_option:    self.Show_Option( not self.show_option )
        if action == action_show_extra:     self.Show_Extra( not self.show_extra )
        if action == action_configure:      self.Layout_Settings()
        # Clean up
        self.Menu_Down()

    # Hold — reveal a group's fly-out after the configured press delay.
    # A QPushButton re-emits pressed/released as the cursor crosses its edge
    # during a drag; ignore those so a press-and-drag gesture neither tears the
    # open fly-out down nor keeps resetting the open timer.
    def Hold_Primary( self, gid ):
        if len( self.flyout_items ) > 0:
            return
        if self.menu_hold is not None and self.menu_hold.isActive():
            return
        self.Menu_Reset()
        self.Menu_Timer_Start( lambda: self.Menu_Primary( gid ) )

    # Release — a plain click ( shorter than press_time ) confirms the primary.
    # If a hold already opened the fly-out, leave it up; it dismisses on pick
    # or on a click elsewhere, not when the button is released.
    def Release_Primary( self, gid ):
        if len( self.flyout_buttons ) > 0:
            return
        self.Menu_Reset()
        slot = self.group_ids.index( gid )
        if slot < len( self.action_tool ):
            self.action_tool[slot].setChecked( True )
        Krita.instance().action( self.operation[gid] ).trigger()
        self.Tela_Geometry( self.show_option, self.show_extra, self.hide_tela )
    def Release_Slot( self, slot ):
        # Krita shortcut action for primary slot N ( 0-based ).
        if slot < len( self.group_ids ):
            self.Release_Primary( self.group_ids[slot] )

    # Menu
    def Menu_Timer_Start( self, function ):
        self.menu_hold = QtCore.QTimer()
        self.menu_hold.setSingleShot( True )
        self.menu_hold.setInterval( self.press_time )
        self.menu_hold.timeout.connect( function )
        self.menu_hold.start()
    def Menu_Reset( self ):
        self.Menu_Timer_Stop()
        self.Menu_Clear()
        self.Flyout_Close()
        self.color_picker.hide()
        # Actions
        for action in self.action_tool:
            action.setChecked( False )
    def Menu_Timer_Stop( self ):
        try:self.menu_hold.stop()
        except:pass
    def Menu_Clear( self ):
        try:self.qmenu.clear()
        except:pass
    def Menu_Down( self ):
        # Krita
        self.menu_krita.setDown( False )
        # Toolbox
        for gid in self.group_ids:
            self.primary[gid].setDown( False )
        # Other
        self.menu_mirror_fix.setDown( False )
        self.menu_color_picker.setDown( False )
    # Fly-out — a vertical stack of real icon buttons above the held primary,
    # replacing the old text-only QMenu. Dismissed on pick or click elsewhere.
    def Menu_Primary( self, gid ):
        self.Flyout_Close()
        if self.canvas_widget is None:
            return
        keys = list( self.tool[gid].keys() )
        geo = self.primary[gid].geometry()
        x = geo.x()
        y = geo.y()
        # Stack upward from just above the primary; first member nearest it.
        for i, key in enumerate( keys ):
            name = "flyout_" + key
            button = QPushButton( self.canvas_widget )
            # Checkable ( non-exclusive ) so the cursor's target can be lit via
            # the :checked style while dragging — real hover events don't arrive
            # during a press-drag ( the primary holds the mouse grab ).
            self.Interface_Push_Button( button, name, self.pba, self.pba, True, False, False )
            button.setIcon( self.tool_catalog[key][2] )
            button.setToolTip( self.tool_catalog[key][0] )
            try:
                self.Interface_Highlight( button, name, self._hl_highlight, self._hl_text )
            except:
                pass
            by = y - ( self.pba + self.pbs ) * ( i + 1 )
            button.setGeometry( x, int( by ), self.pba, self.pba )
            button.show()
            button.raise_()
            self.flyout_buttons.append( button )
            self.flyout_items.append( ( button, gid, key ) )
        # We don't rely on the buttons receiving their own clicks ( on Krita 6's
        # native GL canvas they don't ). Instead an app-wide filter hit-tests the
        # cursor against the fly-out on press ( click ) and release ( drag ).
        QApplication.instance().installEventFilter( self )
        self.Menu_Down()
    def Flyout_Hit( self, global_point ):
        for button, gid, key in self.flyout_items:
            top_left = button.mapToGlobal( QtCore.QPoint( 0, 0 ) )
            if QtCore.QRect( top_left, button.size() ).contains( global_point ):
                return ( gid, key )
        return None
    def Flyout_Highlight( self, global_point ):
        # Light the button under the cursor ( :checked ), clear the rest.
        for button, gid, key in self.flyout_items:
            top_left = button.mapToGlobal( QtCore.QPoint( 0, 0 ) )
            inside = QtCore.QRect( top_left, button.size() ).contains( global_point )
            button.setChecked( inside )
    def Flyout_Pick( self, gid, tool ):
        operation = self.tool_catalog[tool][1]
        Krita.instance().action( operation ).trigger()
        self.index[gid] = tool
        self.operation[gid] = operation
        self.primary[gid].setIcon( self.tool_catalog[tool][2] )
        self.primary[gid].setChecked( True )
        self.Flyout_Close()
        self.Menu_Down()
        self.Tela_Geometry( self.show_option, self.show_extra, self.hide_tela )
    def Flyout_Close( self ):
        if len( self.flyout_buttons ) == 0:
            return
        for button in self.flyout_buttons:
            button.hide()
            button.setParent( None )
            button.deleteLater()
        self.flyout_buttons = list()
        self.flyout_items = list()
        try:
            QApplication.instance().removeEventFilter( self )
        except:
            pass

    # Progress Bar
    def Progress_Bar( self, value ):
        if value >= 99:
            value = 0
        self.progress_bar.setValue( int( value ) )

    #endregion
    #region Actions

    def Transform_Free( self ):
        Krita.instance().action( "KisToolTransformFree" ).trigger()
    def Transform_Perspective( self ):
        Krita.instance().action( "KisToolTransformPerspective" ).trigger()
    def Transform_Warp( self ):
        Krita.instance().action( "KisToolTransformWarp" ).trigger()
    def Transform_Cage( self ):
        Krita.instance().action( "KisToolTransformCage" ).trigger()
    def Transform_Liquify( self ):
        Krita.instance().action( "KisToolTransformLiquify" ).trigger()
    def Transform_Mesh( self ):
        Krita.instance().action( "KisToolTransformMesh" ).trigger()

    # Select
    def Select_All( self ):
        Krita.instance().action( "select_all" ).trigger()
    def Select_None( self ):
        Krita.instance().action( "deselect" ).trigger()
    def Select_Invert( self ):
        Krita.instance().action( "invert_selection" ).trigger()
    def Select_Display( self ):
        Krita.instance().action( "toggle-selection-overlay-mode" ).trigger()

    # Edit
    def Edit_Cut_Sharp( self ):
        Krita.instance().action( "cut_sharp" ).trigger()
    def Edit_Copy_Sharp( self ):
        Krita.instance().action( "copy_sharp" ).trigger()

    # Dockers
    def View_Docker_UI( self ):
        Krita.instance().action( "view_toggledockers" ).trigger()
    def View_Docker_Title( self ):
        Krita.instance().action( "view_toggledockertitlebars" ).trigger()
    # Layer
    def Layer_Isolate( self ):
        Krita.instance().action( "isolate_active_layer" ).trigger()
    # Canvas
    def Canvas_Mirror( self ):
        Krita.instance().action( "mirror_canvas" ).trigger()
    def Canvas_Wrap( self ):
        Krita.instance().action( "wrap_around_mode" ).trigger()
    # Guides
    def Guides_Ruler( self ):
        Krita.instance().action( "view_ruler" ).trigger()
    def Guides_Snap( self ):
        Krita.instance().action( "view_snap_to_guides" ).trigger()
    def Guides_Show( self ):
        Krita.instance().action( "view_show_guides" ).trigger()
    def Guides_Lock( self ):
        Krita.instance().action( "view_lock_guides" ).trigger()
    # View
    def View_Painting_Assistant( self ):
        Krita.instance().action( "view_toggle_painting_assistants" ).trigger()
    def View_Assistant_Preview( self ):
        Krita.instance().action( "view_toggle_assistant_previews" ).trigger()
    def View_Reference_Image( self ):
        Krita.instance().action( "view_toggle_reference_images" ).trigger()
    # Selection
    def Selection_Overlay_Mode( self ):
        Krita.instance().action( "toggle-selection-overlay-mode" ).trigger()

    #endregion
    #region Export Selection

    def Export_Selection( self ):
        if ( ( self.canvas() != None ) and ( self.canvas().view() != None ) ):
            # File
            file_dialog = QFileDialog( QWidget( self ) )
            file_dialog.setFileMode( QFileDialog.FileMode.AnyFile )
            save_path = file_dialog.getSaveFileName( self, "Export Location", "", "*.png" )[0]

            # Run the Export
            if save_path != None:
                self.Export_RUN( save_path )
    def Export_RUN( self, save_path ):
        # Read
        ki = Krita.instance()
        ad = ki.activeDocument()
        node = ad.activeNode()
        adw = ad.width()
        adh = ad.height()

        # Selection
        ss = ad.selection()
        if ss == None: # Create a selection
            px = 0
            py = 0
            pw = ad.width()
            ph = ad.height()
        else: # Custom
            px = ss.x()
            py = ss.y()
            pw = ss.width()
            ph = ss.height()

        # QImage
        qimage_thumbnail = ad.thumbnail( adw, adh )
        qimage_selection = qimage_thumbnail.copy( int( px ), int( py ), int( pw ), int( ph ) )
        mode = Qt.TransformationMode.SmoothTransformation
        if ( self.export_width_state == True and self.export_height_state == False ):
            qimage_scale = qimage_selection.scaledToWidth( int( self.export_width_value ), mode )
        elif ( self.export_width_state == False and self.export_height_state == True ):
            qimage_scale = qimage_selection.scaledToHeight( int( self.export_height_value ), mode )
        else:
            qimage_scale = qimage_selection
        qimage_scale.save( save_path )

    #endregion
    #region Mirror Fix

    def MirrorFix_Explanation( self ):
        self.Menu_Reset()
        self.Message_Float( "MIRROR FIX", f"Press and hold LMB then do a vertical or horizontal drag and release", self.icon_mirrorfix )
        self.Menu_Clear()

    def MirrorFix_Side( self, SIGNAL_SIDE ):
        self.Menu_Reset()
        check_canvas = self.Check_Canvas()
        if check_canvas == True:
            boolean = QMessageBox.question( None, "TELA", f"Mirror Fix Selected Layer(s) ?\nSource = { SIGNAL_SIDE }", QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No )
            if ( boolean == QMessageBox.StandardButton.Yes and SIGNAL_SIDE != None ):
                self.MirrorFix_Run( SIGNAL_SIDE )
    def MirrorFix_Run( self, side ):
        check_canvas = self.Check_Canvas()
        if check_canvas == True:
            # Warnning
            self.Message_Float( "MIRROR FIX", f"START", self.icon_mirrorfix )

            # State
            ki = Krita.instance()
            ad = ki.activeDocument()
            av = ki.activeWindow().activeView()
            # Variables
            width = int( ad.width() )
            height = int( ad.height() )
            w2 = int( width * 0.5 )
            h2 = int( height * 0.5 )

            # Selection
            ss = ad.selection()
            if ss == None: # Square
                state = True
                # Correction
                if side in ( "LEFT", "RIGHT" ):
                    r = width % 2
                    if r == 0:m = 0
                    else:m = 1
                if side in ( "TOP", "DOWN" ):
                    r = height % 2
                    if r == 0:m = 0
                    else:m = 1
                # Variables
                if side == "LEFT":
                    px = 0
                    py = 0
                    pw = w2 + m
                    ph = height
                if side == "RIGHT":
                    px = w2
                    py = 0
                    pw = w2 + m
                    ph = height
                if side == "TOP":
                    px = 0
                    py = 0
                    pw = width
                    ph = h2 + m
                if side == "DOWN":
                    px = 0
                    py = h2
                    pw = width
                    ph = h2 + m
                # Selection
                sel = Selection()
                sel.select( int( px ), int( py ), int( pw ), int( ph ), 255 )
                ad.setSelection( sel )
            else: # Custom
                state = False
                sel = ss
                px = sel.x()
                py = sel.y()
                pw = sel.width()
                ph = sel.height()
            sel.invert()
            selection_data = sel.pixelData( 0, 0, width, height )
            ki.action( 'deselect' ).trigger()

            # Cycle
            old_node_list = av.selectedNodes()
            for old_node in old_node_list:
                node_type = old_node.type()
                if str( node_type ) == "paintlayer":
                    # Variables
                    old_name = old_node.name()
                    new_name = f"Mirror Fix : { old_name }"
                    parent = old_node.parentNode()
                    # Old Node
                    ad.setActiveNode( old_node )
                    self.Wait( ad )
                    # New Node
                    new_node = ad.createNode( new_name, "paintLayer" )
                    parent.addChildNode( new_node, old_node )
                    # Copy Paste
                    if state == True:
                        pixel_array = old_node.pixelData( int( px ), int( py ), int( pw ), int( ph ) )
                        new_node.setPixelData( pixel_array, int( px ), int( py ), int( pw ), int( ph ) )
                    if state == False:
                        pixel_array = old_node.pixelData( int( 0 ), int( 0 ), int( width ), int( height ) )
                        new_node.setPixelData( pixel_array, int( 0 ), int( 0 ), int( width ), int( height ) )

            # Re-Select
            sel = Selection()
            sel.setPixelData( selection_data, 0, 0, width, height )
            ad.setSelection( sel )
            # Cycle
            for old_node in old_node_list:
                node_type = old_node.type()
                if str( node_type ) == "paintlayer":
                    # Old Node
                    ad.setActiveNode( old_node )
                    self.Wait( ad )
                    # Clear
                    ki.action( 'clear' ).trigger()
            # De-Select
            ki.action( 'deselect' ).trigger()

            # Cycle
            for old_node in old_node_list:
                node_type = old_node.type()
                if str( node_type ) == "paintlayer":
                    # Variables
                    old_name = old_node.name()
                    new_name = f"Mirror Fix : { old_name }"
                    # Old Node
                    ad.setActiveNode( old_node )
                    self.Wait( ad )
                    # Mirror
                    if ( side == "LEFT" or side == "RIGHT" ):
                        ki.action( 'mirrorNodeX' ).trigger()
                    if ( side == "TOP" or side == "DOWN" ):
                        ki.action( 'mirrorNodeY' ).trigger()
                    self.Wait( ad )
                    # Re-Order
                    ki.action( 'move_layer_up' ).trigger()
                    self.Wait( ad )
                    # Merge ( this solves a alpha compositing issue )
                    ki.action( 'merge_layer' ).trigger()
                    self.Wait( ad )
                    # Merge
                    merge_node = ad.nodeByName( new_name )
                    self.Wait( ad )
                    ad.setActiveNode( merge_node )
                    self.Wait( ad )
                    merge_node.setName( old_name )
                    self.Wait( ad )

            # Warnning
            self.Message_Float( "MIRROR FIX", "END", self.icon_mirrorfix )
    def Wait( self, active_document ):
        active_document.waitForDone()
        active_document.refreshProjection()

    #endregion
    #region Color Picker

    # Module
    def Import_Pigment_O( self ):
        try:
            # Tela
            self.menu_color_picker.setEnabled( False )
            # Krita
            ki = Krita.instance()
            docker_list = ki.dockers()
            for docker in docker_list:
                if docker.objectName() == self.pigmento_picker_pyid:
                    # Variables
                    self.pigmento_picker = docker
                    # Styling
                    self.menu_color_picker.setEnabled( True )
                    self.menu_color_picker.setIcon( ki.icon( "krita_tool_ellipse" ) )
                    break
        except:
            pass
    # Ui
    def Show_Color_Picker( self ):
        if self.color_picker.isVisible() == False:
            self.Menu_Reset()
            self.Size_Update()
            self.Color_READ()
            self.color_picker.show()
        else:
            self.color_picker.hide()

    # Color Panel
    def Color_Panel_Preview( self, lista ):
        self.Color_Sliders_READ( lista[0], lista[1], lista[2] )
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, False )
    def Color_Panel_Apply( self, lista ):
        self.Color_Sliders_READ( lista[0], lista[1], lista[2] )
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, True )

    # Sliders Read
    def CS1_R( self, value ):
        self.s1 = value
        self.color_picker.s1.blockSignals( True )
        self.color_picker.s1.setValue( int( self.s1 * self.hue ) )
        self.color_picker.s1.blockSignals( False )
    def CS2_R( self, value ):
        self.s2 = value
        self.color_picker.s2.blockSignals( True )
        self.color_picker.s2.setValue( int( self.s2 * self.svl ) )
        self.color_picker.s2.blockSignals( False )
    def CS3_R( self, value ):
        self.s3 = value
        self.color_picker.s3.blockSignals( True )
        self.color_picker.s3.setValue( int( self.s3 * self.svl ) )
        self.color_picker.s3.blockSignals( False )
    def Color_Sliders_READ( self, s1, s2, s3 ):
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.color_picker.s1.blockSignals( True )
        self.color_picker.s2.blockSignals( True )
        self.color_picker.s3.blockSignals( True )
        self.color_picker.s1.setValue( int( self.s1 * self.hue ) )
        self.color_picker.s2.setValue( int( self.s2 * self.svl ) )
        self.color_picker.s3.setValue( int( self.s3 * self.svl ) )
        self.color_picker.s1.blockSignals( False )
        self.color_picker.s2.blockSignals( False )
        self.color_picker.s3.blockSignals( False )
    # Sliders Write
    def CS1_W( self, action ):
        self.s1 = self.color_picker.s1.value() / self.hue
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, action )
    def CS2_W( self, action ):
        self.s2 = self.color_picker.s2.value() / self.svl
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, action )
    def CS3_W( self, action ):
        self.s3 = self.color_picker.s3.value() / self.svl
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, action )
    def Color_Sliders_WRITE( self, s1, s2, s3 ):
        self.s1 = s1 / self.hue
        self.s2 = s2 / self.svl
        self.s3 = s3 / self.svl
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3 )

    # Read and Write
    def Color_READ( self ):
        if self.pigmento_picker != None:
            # Read
            self.cor = self.pigmento_picker.API_Request_FG()
            wheel_space = self.pigmento_picker.API_Request_Wheel_Space()

            # Wheel Space
            if wheel_space != self.wheel_space:
                # Variables
                self.wheel_space = wheel_space
                panel_path = self.directory_plugin.replace( "tela", "pigment_o\\PANEL")
                zip_path = os.path.join( panel_path, f"SRGB_{ self.wheel_space }_S4.zip" )
                # QPixmap List
                self.qpixmap_list = self.Read_Zip( zip_path )
                self.color_panel.Set_Gradient( self.qpixmap_list )

            # Variables
            hex6 = self.cor["display"]
            if self.wheel_space == "HSV":
                s1 = self.cor["hsv_1"]
                s2 = self.cor["hsv_2"]
                s3 = self.cor["hsv_3"]
            elif self.wheel_space == "HSL":
                s1 = self.cor["hsl_1"]
                s2 = self.cor["hsl_2"]
                s3 = self.cor["hsl_3"]
            elif self.wheel_space == "HCY":
                s1 = self.cor["hcy_1"]
                s2 = self.cor["hcy_2"]
                s3 = self.cor["hcy_3"]
            elif self.wheel_space == "ARD":
                s1 = self.cor["ard_1"]
                s2 = self.cor["ard_2"]
                s3 = self.cor["ard_3"]

            # Preview
            self.color_display.Set_Color( hex6 )
            # Panel
            self.color_panel.Set_Color( s1, s2, s3 )
            # Sliders
            self.Color_Sliders_READ( s1, s2, s3 )
    def Color_WRITE( self, wheel_space, s1, s2, s3, action=True ):
        # if self.pigmento_module != None:
        if self.pigmento_picker != None:
            # Pigment.O
            if action == False: self.cor = self.pigmento_picker.API_Input_Preview( str( wheel_space ), float( s1 ), float( s2 ), float( s3 ), 0.0 )
            if action == True:  self.cor = self.pigmento_picker.API_Input_Apply( str( wheel_space ), float( s1 ), float( s2 ), float( s3 ), 0.0 )
            # Update
            self.color_display.Set_Color( self.cor["display"] )
            self.color_panel.Set_Color( s1, s2, s3 )

    # Extras
    def Color_BlockSignals( self, boolean ):
        self.color_picker.color_display.blockSignals( boolean )
        self.color_picker.color_panel.blockSignals( boolean )
        self.color_picker.s1.blockSignals( boolean )
        self.color_picker.s2.blockSignals( boolean )
        self.color_picker.s3.blockSignals( boolean )
    def Read_Zip( self, url ):
        list_qpixmap = list()
        try:
            if zipfile.is_zipfile( url ):
                archive = zipfile.ZipFile( url, "r" )
                name_list = archive.namelist()
                name_list.sort()
                for name in name_list:
                    # Archive
                    extract = archive.open( name )
                    image_data = extract.read()
                    # Buffer
                    byte_array = QByteArray( image_data )
                    buffer = QBuffer()
                    buffer.setData( byte_array )
                    buffer.open( QIODevice.OpenModeFlag.ReadOnly )
                    # Image
                    reader = QImageReader( buffer )
                    qpixmap = QPixmap().fromImageReader( reader )
                    list_qpixmap.append( qpixmap )
        except Exception as e:
            try:QtCore.qDebug( f"TELA | ERROR request failed\n{ e }" )
            except:pass
        return list_qpixmap

    #endregion
    #region Notifier

    def Application_Closing( self ):
        pass
    def Configuration_Changed( self ):
        pass
    def Image_Closed( self ):
        pass
    def Image_Created( self ):
        pass
    def Image_Saved( self ):
        pass
    def View_Closed( self ):
        pass
    def View_Created( self ):
        pass
    def Window_Created( self ):
        # Window
        ki = Krita.instance()
        self.window = ki.activeWindow()

        # Signals
        self.window.activeViewChanged.connect( self.View_Changed )
        self.window.themeChanged.connect( self.Theme_Changed )
        self.window.windowClosed.connect( self.Window_Closed )

        # Toolbox
        self.Toolbox_Display()
        self.Toolbox_Button()
        self.Toolbox_Filter_Install()
        self.Toolbox_Load()
    def Window_IsBeingCreated( self ):
        pass

    # Window
    def View_Changed( self ):
        self.Menu_Reset()
        self.Tool_Update()
        self.Theme_Changed()
    def Theme_Changed( self ):
        self.Style_Theme()
        self.Style_Icon()
    def Window_Closed( self ):
        pass

    #endregion
    #region Widget Events

    def eventFilter( self, source, event ):
        # Variables
        et = event.type()
        transform_widgets = list()
        # Fly-out interaction, by cursor position ( not event target — the native
        # GL canvas eats clicks meant for the overlay buttons ):
        #   - press  over a secondary -> select it ( click model )
        #   - release over a secondary -> select it ( press-drag-release model )
        #   - press  outside          -> dismiss
        #   - release outside         -> leave open ( ends the hold, keeps the menu )
        if ( len( self.flyout_items ) > 0 and et in [ QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease ] ):
            try:    gp = event.globalPosition().toPoint()
            except: gp = QCursor().pos()
            hit = self.Flyout_Hit( gp )
            if hit is not None:
                self.Flyout_Pick( hit[0], hit[1] )
                return True
            if et == QEvent.Type.MouseButtonPress:
                self.Flyout_Close()
        # Live feedback: highlight the secondary under the cursor while open.
        if ( len( self.flyout_items ) > 0 and et == QEvent.Type.MouseMove ):
            try:    gp = event.globalPosition().toPoint()
            except: gp = QCursor().pos()
            self.Flyout_Highlight( gp )
        # Geometry ( resize )
        if self.canvas_widget != None:
            if ( event.type() == QEvent.Type.Resize and source == self.canvas_widget ):
                self.Size_Update()
        # Krita ToolBox Signals
        if ( et in [ QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease, QEvent.Type.PaletteChange ] and source in self.krita_toolbox ):
            self.Tool_Update()
        # Color Picker
        if ( et == QEvent.Type.Enter and source is self.color_picker ):
            self.Color_READ()
            return True
        return super().eventFilter( source, event )

    #endregion
    #region Actions

    def createActions(self, window):
        # Main Menu
        menu_tela = QtWidgets.QMenu( "tela_menu", window.qwindow() )
        action_tela = window.createAction( "tela_menu", "Tela", "tools/scripts" )
        action_tela.setMenu( menu_tela )
        # Tool Menu
        menu_toolbox = QtWidgets.QMenu( "toolbox_menu", window.qwindow() )
        action_toolbox = window.createAction( "toolbox_menu", "Toolbox", "tools/scripts/tela_menu" )
        action_toolbox.setMenu( menu_toolbox )
        # Mirror Fix Menu
        menu_mirror_fix = QtWidgets.QMenu( "mirror_fix_menu", window.qwindow() )
        action_mirror_fix = window.createAction( "mirror_fix_menu", "Mirror Fix", "tools/scripts/tela_menu" )
        action_mirror_fix.setMenu( menu_mirror_fix )

        # Toolbox — seven shortcut slots that select primary 1..7 by position.
        # The action ids are kept from the old fixed-group scheme so any
        # keyboard shortcuts users already assigned keep working. Slots past
        # the number of configured primaries simply do nothing.
        slot_ids = [
            "tela_extension_tool_vector", "tela_extension_tool_brush",
            "tela_extension_tool_transform", "tela_extension_tool_color",
            "tela_extension_tool_overlay", "tela_extension_tool_select",
            "tela_extension_tool_camera",
        ]
        self.action_tool = list()
        for i, aid in enumerate( slot_ids ):
            action = window.createAction( aid, "Tela Primary " + str( i + 1 ), "tools/scripts/tela_menu/toolbox_menu" )
            action.setCheckable( True )
            action.triggered.connect( lambda checked = False, s = i: self.Release_Slot( s ) )
            self.action_tool.append( action )

        # Actions Mirror Fix
        action_mirror_fix_left  = window.createAction( "tela_extension_mirror_fix_left",  "Mirror Fix [LEFT]",  "tools/scripts/tela_menu/mirror_fix_menu" )
        action_mirror_fix_right = window.createAction( "tela_extension_mirror_fix_right", "Mirror Fix [RIGHT]", "tools/scripts/tela_menu/mirror_fix_menu" )
        action_mirror_fix_top   = window.createAction( "tela_extension_mirror_fix_top",   "Mirror Fix [TOP]",   "tools/scripts/tela_menu/mirror_fix_menu" )
        action_mirror_fix_down  = window.createAction( "tela_extension_mirror_fix_down",  "Mirror Fix [DOWN]",  "tools/scripts/tela_menu/mirror_fix_menu" )
        action_mirror_fix_left.triggered.connect(  lambda: self.MirrorFix_Side( "LEFT" ) )
        action_mirror_fix_right.triggered.connect( lambda: self.MirrorFix_Side( "RIGHT" ) )
        action_mirror_fix_top.triggered.connect(   lambda: self.MirrorFix_Side( "TOP" ) )
        action_mirror_fix_down.triggered.connect(  lambda: self.MirrorFix_Side( "DOWN" ) )

        # Actions Picker
        action_picker_to_cursor = window.createAction( "tela_extension_picker_to_cursor", "Picker to Cursor", "tools/scripts/tela_menu" )
        action_picker_to_cursor.triggered.connect( self.Picker_to_Cursor )

    #endregion
    #region Notes

    """
    # Label Message
    self.layout.label.setText( "message" )

    # Pop Up Message
    QMessageBox.information( QWidget(), i18n( "Warnning" ), i18n( "message" ) )

    # Log Viewer Message
    QtCore.qDebug( f"value = { value }" )
    QtCore.qDebug( "message" )
    QtCore.qWarning( "message" )
    QtCore.qCritical( "message" )

    """

    """
    # self.setWindowFlags( QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint )
    """

    """
    QTimer.singleShot( 0, lambda: self.MirrorFix_Invert( ki, ad, side, new_node ) )
    """

    """
    # Docker
    pyid = "ToolBox"
    dockers = Krita.instance().dockers()
    for d in dockers:
        if d.objectName() == pyid:
            tool_box = d
            break
    # Krita Tool Box
    key_mg = self.tool.keys()
    for mg in key_mg:
        key_sg = self.tool[mg].keys()
        for sg in key_sg:
            item = self.tool[mg][sg][1]
            child = tool_box.findChild( QToolButton, item )
            self.krita_toolbox.append( child )
            child.installEventFilter( self )
    """

    """
    if hide_tela == True:
        for i in range( 0, limit+1, +1 ):
            index = ( i / limit ) ** curve
            self.Tela_Geometry( show_extra, index, True )
            self.color_picker.hide()
    if hide_tela == False:
        for i in range( limit, -1, -1 ):
            index = ( i / limit ) ** curve
            self.Tela_Geometry( show_extra, index, True )
    """

    #endregion

"""
New:
- Animated toolBox for Hide/Show
- Ui File destroyed, now widgets are code based
- Auto updates when Krita changes tool
- Show Extras
- Keeps memory of extras state
"""
