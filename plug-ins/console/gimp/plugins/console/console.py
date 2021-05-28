#!/usr/bin/python3

#
#   This package is part of:
#   gimp-python-development tools
#   Copyright (C) 2021  Ismael Benito <ismaelbenito@protonmail.com>
#
#   This program is free software: you can redistribute it and/or modify
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
import sys
import gi

gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')

from gi.repository import Gimp
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import Gio
from gi.repository import GLib

from gimp.plugins.console import ConsoleDialog
from gimp.plugins.console.utils import translate_str_gimp

from gimp.plugins.console.gtk.pyconsole import run as run_pyconsole
from gimp.plugins.console.gtk.gtkpyinterpreter import run as run_pyinterpreter
from gimp.plugins.console.gtk.gtkmatplotlibshell import run as run_matplotlibshell


PROC_NAME = 'console'


def run_gimp_console():
    """Run the official GIMP pyconsole"""
    return ConsoleDialog(proc_name=PROC_NAME).run()


run_funcs = dict(
    gimp=run_gimp_console,
    pyconsole=run_pyconsole,
    pyinterpreter=run_pyinterpreter,
    matplotlibshell=run_matplotlibshell
)

RUN = "gimp"


def run(procedure, args, data):
    GimpUi.init("console.py")

    run_f = run_funcs[RUN]
    run_f()

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


class PythonConsole(Gimp.PlugIn):
    def __init__(self):
        Gimp.PlugIn.__init__(self)
        self._run_mode = None

    @GObject.Property(
        type=Gimp.RunMode,
        default=Gimp.RunMode.NONINTERACTIVE,
        nick="Run mode",
        blurb="The run mode"
    )
    def run_mode(self):
        """Read-write integer property."""
        return self._run_mode

    @run_mode.setter
    def run_mode(self, runmode):
        self._run_mode = runmode

    def do_query_procedures(self):
        # Localization
        self.set_translation_domain(
            "gimp30-python",
            Gio.file_new_for_path(Gimp.locale_directory())
        )

        return [PROC_NAME]

    def do_create_procedure(self, name):
        if name == PROC_NAME:
            procedure = Gimp.Procedure.new(
                self, name,
                Gimp.PDBProcType.PLUGIN,
                run,
                None
            )
            procedure.set_menu_label(translate_str_gimp("Python Console"))
            procedure.set_documentation(
                translate_str_gimp("Interactive GIMP Python interpreter"),
                "Type in commands and see results",
                ""
            )
            procedure.set_attribution(
                "Ismael Benito",
                "Ismael Benito",
                "2021"
            )
            procedure.add_argument_from_property(self, "run-mode")
            procedure.add_menu_path("<Image>/Filters/Development/Python")

            return procedure
        return None


Gimp.main(PythonConsole.__gtype__, sys.argv)
