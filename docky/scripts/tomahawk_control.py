#!/usr/bin/env python2

#
#  Copyright (C) 2011 Hugo Lindstrom (hugolm84@gmail.com)
#  Thanks to Jason Smith, Rico Tzschichholz, Robert Dyer, Par Eriksson which 
#  code this is based on
#    
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import atexit
import gobject
import glib
import dbus
import dbus.glib
import sys
import os

try:
    import gtk
    from dockmanager.dockmanager import DockManagerItem, DockManagerSink, DOCKITEM_IFACE
    from dockmanager.dockmanager import RESOURCESDIR
    from signal import signal, SIGTERM
    from sys import exit
except ImportError, e:
    print e
    exit()

tomahawkbus = "org.mpris.MediaPlayer2.tomahawk"
playerpath = "/org/mpris/MediaPlayer2"
playeriface = "org.mpris.MediaPlayer2.Player"
playerproperties = "org.freedesktop.DBus.Properties"

class tomahawkItem(DockManagerItem):
    def __init__(self, sink, path):
        DockManagerItem.__init__(self, sink, path)
        self.player = None
        self.properties = None

        self.bus.add_signal_receiver(self.name_owner_changed_cb,
                                             dbus_interface='org.freedesktop.DBus',
                                             signal_name='NameOwnerChanged')

        obj = self.bus.get_object ("org.freedesktop.DBus", "/org/freedesktop/DBus")
        self.bus_interface = dbus.Interface(obj, "org.freedesktop.DBus")

        self.bus_interface.ListNames (reply_handler=self.list_names_handler, error_handler=self.list_names_error_handler)

    def list_names_handler(self, names):
        if tomahawkbus in names:
            self.init_tomahawk_objects()
            self.set_menu_buttons()

    def list_names_error_handler(self, error):
        print "error getting bus names - %s" % str(error)

    def name_owner_changed_cb(self, name, old_owner, new_owner):
        if name == tomahawkbus:
            if new_owner:
                self.init_tomahawk_objects()
                self.set_menu_buttons()
            else:
                self.player = None
                self.properties = None
                self.set_menu_buttons()

    def init_tomahawk_objects(self):
        obj = self.bus.get_object(tomahawkbus, playerpath)
        self.player = dbus.Interface(obj, playeriface)
        obj = self.bus.get_object(tomahawkbus, playerpath)
        self.properties = dbus.Interface(obj, playerproperties)

    def menu_pressed(self, menu_id):
        if not self.player:
            return False

        if self.id_map[menu_id] == "Play":
            self.player.PlayPause()
        elif self.id_map[menu_id] == "Pause":
            self.player.PlayPause()
        elif self.id_map[menu_id] == "Next":
            self.player.Next()
        elif self.id_map[menu_id] == "Previous":
            self.player.Previous()
        self.set_menu_buttons()

    def tomahawk_is_playing(self):
        if self.properties:
            try:
                return self.properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus") == "Playing"
            except dbus.DBusException, e:
                return False
        return False

    def clear_menu_buttons(self):
        for k in self.id_map.keys():
            self.remove_menu_item(k)

    def set_menu_buttons(self):
        self.clear_menu_buttons()

        if not self.player:
            return

        self.add_menu_item("Previous", "media-skip-backward")
        if self.tomahawk_is_playing():
            self.add_menu_item("Pause", "media-playback-pause")
        else:
            self.add_menu_item("Play", "media-playback-start")
        self.add_menu_item("Next", "media-skip-forward")

class tomahawkSink(DockManagerSink):
    def item_path_found(self, pathtoitem, item):
        if item.Get(DOCKITEM_IFACE, "DesktopFile", dbus_interface="org.freedesktop.DBus.Properties").endswith ("tomahawk.desktop"):
            self.items[pathtoitem] = tomahawkItem(self, pathtoitem)

tomahawksink = tomahawkSink()

def cleanup ():
    tomahawksink.dispose ()

if __name__ == "__main__":
    mainloop = gobject.MainLoop(is_running=True)

    atexit.register (cleanup)
    signal(SIGTERM, lambda signum, stack_frame: exit(1))

    mainloop.run()
