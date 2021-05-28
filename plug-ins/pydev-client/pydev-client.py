#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

import gettext
import os
import sys

import pydevd_pycharm
import multiprocessing as mp


def set_trace():
    return pydevd_pycharm.settrace(
        'localhost',
        port=10002,
        stdoutToServer=True,
        stderrToServer=True
    )


# Set-up localization for your plug-in with your own text domain.
# This is complementary to the gimp_plug_in_set_translation_domain()
# which is only useful for the menu entries inside GIMP interface,
# whereas the below calls are used for localization within the plug-in.
textdomain = 'gimp30-std-plug-ins'
gettext.bindtextdomain(textdomain, Gimp.locale_directory())
gettext.bind_textdomain_codeset(textdomain, 'UTF-8')
gettext.textdomain(textdomain)
_ = gettext.gettext
def N_(message): return message


head_text = _("""
This plug-in enables the capacity to connect to a PyDev debugger in order to be able to run Python
code inside GIMP from an external IDE such as PyCharm or Eclipse. 
""")


class PyDevClient(Gimp.PlugIn):
    ## Properties: parameters ##
    @GObject.Property(type=Gimp.RunMode,
                      default=Gimp.RunMode.NONINTERACTIVE,
                      nick="Run mode", blurb="The run mode")
    def run_mode(self):
        """Read-write integer property."""
        return self.runmode

    @run_mode.setter
    def run_mode(self, runmode):
        self.runmode = runmode


    def do_query_procedures(self):
        # Localization for the menu entries. It has to be called in the
        # query function only.
        self.set_translation_domain(
            textdomain,
            Gio.file_new_for_path(Gimp.locale_directory())
        )

        return ["pydev-client"]

    def do_create_procedure(self, name):
        procedure = Gimp.Procedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.run, None
        )

        # procedure.set_image_types("*")

        procedure.set_menu_label(N_("Run PyDev client"))
        # procedure.set_icon_name(GimpUi.ICON_GEGL)
        procedure.add_menu_path('<Image>/Filters/Development/Python/')

        procedure.set_documentation(
            N_("Run a PyDev client"),
            N_("Run a PyDev client"),
            name
        )
        procedure.set_attribution("Ismael Benito", "Ismael Benito", "2021")

        procedure.add_argument_from_property(self, "run-mode")

        return procedure

    def run(self, procedure, args, run_data):

        GimpUi.init("pydev-client")

        dialog = GimpUi.Dialog(
            use_header_bar=True,
            title=_("PyDev Client"),
            role="pydev-client"
        )

        dialog.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("_Source"), Gtk.ResponseType.APPLY)
        dialog.add_button(_("_OK"), Gtk.ResponseType.OK)

        geometry = Gdk.Geometry()
        # geometry.min_aspect = 0.5
        # geometry.max_aspect = 1.0
        # dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        dialog.get_content_area().add(box)
        box.show()

        label = Gtk.Label(label=head_text)
        box.pack_start(label, False, False, 1)
        label.show()

        contents = "Hola Mundo!"

        if contents is not None:
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_vexpand(True)
            box.pack_start(scrolled, True, True, 1)
            scrolled.show()

            view = Gtk.TextView()
            view.set_wrap_mode(Gtk.WrapMode.WORD)
            view.set_editable(False)
            buffer = view.get_buffer()
            buffer.set_text(contents, -1)
            scrolled.add(view)
            view.show()

        th = mp.Process(target=set_trace)
        th.start()

        while True:
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                dialog.destroy()
                break
            elif response == Gtk.ResponseType.APPLY:
                url = "https://github.com/isman7/gimp-python-development"
                Gio.app_info_launch_default_for_uri(url, None)
                continue
            else:
                th.terminate()
                dialog.destroy()
                return procedure.new_return_values(
                    Gimp.PDBStatusType.CANCEL,
                    GLib.Error()
                )

        th.terminate()

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(PyDevClient.__gtype__, sys.argv)

