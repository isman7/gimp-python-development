import sys

import gi
from gi.repository import Gimp
from gi.repository import GimpUi
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gio
from gi.repository import GLib

from .gtk import Console
from .utils import translate_str, translate_str_gimp


RESPONSE_BROWSE, RESPONSE_CLEAR, RESPONSE_SAVE = range(3)

namespace = {
    '__builtins__': __builtins__,
    '__name__': '__main__', '__doc__': None,
    'Babl': gi.repository.Babl,
    'cairo': gi.repository.cairo,
    'Gdk': gi.repository.Gdk,
    'Gegl': gi.repository.Gegl,
    'Gimp': gi.repository.Gimp,
    'Gio': gi.repository.Gio,
    'Gtk': gi.repository.Gtk,
    'GdkPixbuf': gi.repository.GdkPixbuf,
    'GLib': gi.repository.GLib,
    'GObject': gi.repository.GObject,
    'Pango': gi.repository.Pango
}


class GimpConsole(Console):
    def __init__(self, quit_func=None):
        banner = f'GIMP {Gimp.version()} Python Console\nPython {sys.version}\n'

        Console.__init__(
            self,
            locals=namespace,
            banner=banner,
            quit_func=quit_func
        )

    def _commit(self):
        Console._commit(self)
        Gimp.displays_flush()


class ConsoleDialog(GimpUi.Dialog):
    def __init__(self, proc_name):
        use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")

        GimpUi.Dialog.__init__(self, use_header_bar=use_header_bar)

        self.set_property("help-id", proc_name)

        Gtk.Window.set_title(self, translate_str("Python Console"))
        Gtk.Window.set_role(self, proc_name)
        Gtk.Dialog.add_button(self, "_Save", Gtk.ResponseType.OK)
        Gtk.Dialog.add_button(self, "Cl_ear", RESPONSE_CLEAR)
        Gtk.Dialog.add_button(self, translate_str("_Browse..."), RESPONSE_BROWSE)
        Gtk.Dialog.add_button(self, "_Close", Gtk.ResponseType.CLOSE)

        Gtk.Widget.set_name(self, proc_name)
        GimpUi.Dialog.set_alternative_button_order_from_array(
            self,
            [Gtk.ResponseType.CLOSE, RESPONSE_BROWSE, RESPONSE_CLEAR, Gtk.ResponseType.OK]
        )

        self.cons = GimpConsole(quit_func=lambda: Gtk.main_quit())

        self.style_set(None, None)

        self.connect('response', self.response)
        self.connect('style-set', self.style_set)

        self.browse_dlg = None
        self.save_dlg = None

        vbox = Gtk.VBox(homogeneous=False, spacing=12)
        vbox.set_border_width(12)
        contents_area = Gtk.Dialog.get_content_area(self)
        contents_area.pack_start(vbox, True, True, 0)

        scrl_win = Gtk.ScrolledWindow()
        scrl_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        vbox.pack_start(scrl_win, True, True, 0)

        scrl_win.add(self.cons)

        width, height = self.cons.get_default_size()
        minreq, requisition = Gtk.Widget.get_preferred_size(scrl_win.get_vscrollbar())
        sb_width = requisition.width
        sb_height = requisition.height

        # Account for scrollbar width and border width to ensure
        # the text view gets a width of 80 characters. We don't care
        # so much whether the height will be exactly 40 characters.
        Gtk.Window.set_default_size(self, width + sb_width + 2 * 12, height)

    def style_set(self, old_style, user_data):
        pass

    def response(self, dialog, response_id):
        if response_id == RESPONSE_BROWSE:
            self.browse()
        elif response_id == RESPONSE_CLEAR:
            self.cons.banner = None
            self.cons.clear()
        elif response_id == Gtk.ResponseType.OK:
            self.save_dialog()
        else:
            Gtk.main_quit()

        self.cons.grab_focus()

    def browse_response(self, dlg, response_id):
        if response_id != Gtk.ResponseType.APPLY:
            Gtk.Widget.hide(dlg)
            return

        proc_name = dlg.get_selected()

        if not proc_name:
            return

        # TODO fix this bug, there is no pdb object in py3 gi API
        proc = pdb[proc_name]

        cmd = ''

        if len(proc.return_vals) > 0:
            cmd = ', '.join(x[1].replace('-', '_') for x in proc.return_vals) + ' = '

        cmd = cmd + f"pdb.{proc.proc_name.replace('-', '_')}"

        if len(proc.params) > 0 and proc.params[0][1] == 'run-mode':
            params = proc.params[1:]
        else:
            params = proc.params

        cmd = cmd + f"({', '.join(x[1].replace('-', '_') for x in params)})"

        buffer = self.cons.buffer

        lines = buffer.get_line_count()
        iter = buffer.get_iter_at_line_offset(lines - 1, 4)
        buffer.delete(iter, buffer.get_end_iter())
        buffer.place_cursor(buffer.get_end_iter())
        buffer.insert_at_cursor(cmd)

    def browse(self):
        if not self.browse_dlg:
            use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")

            dlg = GimpUi.ProcBrowserDialog(use_header_bar=use_header_bar)
            Gtk.Window.set_title(dlg, translate_str("Python Procedure Browser"))
            Gtk.Window.set_role(dlg, dlg.get_selected())
            Gtk.Dialog.add_button(dlg, "Apply", Gtk.ResponseType.APPLY)
            Gtk.Dialog.add_button(dlg, "Close", Gtk.ResponseType.CLOSE)

            Gtk.Dialog.set_default_response(self, Gtk.ResponseType.OK)

            GimpUi.Dialog.set_alternative_button_order_from_array(
                dlg,
                [Gtk.ResponseType.CLOSE, Gtk.ResponseType.APPLY]
            )

            dlg.connect('response', self.browse_response)
            dlg.connect('row-activated', lambda dlg: dlg.response(Gtk.ResponseType.APPLY))

            self.browse_dlg = dlg

        Gtk.Window.present(self.browse_dlg)

    def save_response(self, dlg, response_id):
        if response_id == Gtk.ResponseType.DELETE_EVENT:
            self.save_dlg = None
            return

        elif response_id == Gtk.ResponseType.OK:
            filename = dlg.get_filename()

            try:
                logfile = open(filename, 'w')

            except IOError as e:
                Gimp.message(translate_str(f"Could not open '{filename}' for writing: {e.strerror}"))
                return

            buffer = self.cons.buffer

            start = buffer.get_start_iter()
            end = buffer.get_end_iter()

            log = buffer.get_text(start, end, False)

            try:
                logfile.write(log)
                logfile.close()

            except IOError as e:
                Gimp.message(translate_str(f"Could not write to '{filename}': {e.strerror}"))
                return

        Gtk.Widget.hide(dlg)

    def save_dialog(self):
        # TODO fix this, it's not working, got:
        # TypeError: argument self: Expected GimpUi.Dialog, but got gi.overrides.Gtk.FileChooserDialog
        if not self.save_dlg:
            dlg = Gtk.FileChooserDialog()

            Gtk.Window.set_title(dlg, translate_str("Save Python-Fu Console Output"))
            Gtk.Window.set_transient_for(dlg, self)
            Gtk.Dialog.add_button(dlg, "_Cancel", Gtk.ResponseType.CANCEL)
            Gtk.Dialog.add_button(dlg, "_Save", Gtk.ResponseType.OK)
            Gtk.Dialog.set_default_response(self, Gtk.ResponseType.OK)

            GimpUi.Dialog.set_alternative_button_order_from_array(
                dlg,
                [Gtk.ResponseType.OK, Gtk.ResponseType.CANCEL]
            )

            dlg.connect('response', self.save_response)

            self.save_dlg = dlg

        self.save_dlg.present()

    def run(self):
        Gtk.Widget.show_all(self)
        Gtk.main()
