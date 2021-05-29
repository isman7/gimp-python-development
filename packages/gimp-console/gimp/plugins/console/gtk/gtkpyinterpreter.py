from code import InteractiveInterpreter
from rlcompleter import Completer
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Pango
import os
import sys

import builtins


def flush(): pass


class GtkInterpreter(InteractiveInterpreter):
    def __init__(self, stdout, stderr, interpreter_locals):
        InteractiveInterpreter.__init__(self, interpreter_locals)
        self.stdout = stdout
        self.stderr = stderr

    def runcode(self, cmd):
        sys.stdout = self.stdout
        # sys.stdout.flush = flush
        sys.stderr = self.stderr
        # sys.stderr.flush = flush
        result = InteractiveInterpreter.runcode(self, cmd)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        return result

    def write(self, data):
        if data.strip() != 'None':
            self.stderr.write(data)


class GtkInterpreterStandardOutput(GObject.GObject):
    __gproperties__ = {
        'auto-scroll': (
            GObject.TYPE_BOOLEAN,
            'auto-scroll',
            'Whether to automatically scroll the output.',
            True,
            GObject.PARAM_READWRITE
        ),
    }

    __gsignals__ = {
        'output-written': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (GObject.TYPE_STRING,)
        ),
    }

    def __init__(self, textview):
        super(GtkInterpreterStandardOutput, self).__init__()
        self.textview = textview
        # properties
        textbuffer = self.textview.get_buffer()
        if textbuffer.get_tag_table().lookup('protected') is None:
            textbuffer.create_tag(tag_name='protected', editable=False)
        self._input_mark = textbuffer.get_mark('input_start')
        self._prop_auto_scroll = True

    def write(self, txt, move_cursor=False, tag_names=('protected',)):
        textbuffer = self.textview.get_buffer()
        textiter = textbuffer.get_end_iter()
        textbuffer.insert_with_tags_by_name(textiter, txt, *tag_names)
        if self._prop_auto_scroll:
            self.textview.scroll_mark_onscreen(textbuffer.get_insert())
        textbuffer.move_mark(self._input_mark, textbuffer.get_end_iter())
        if move_cursor:
            textbuffer.place_cursor(textbuffer.get_iter_at_mark(self._input_mark))
        self.emit('output-written', txt)

    def write_pixbuf(self, pixbuf, move_cursor=True):
        textbuffer = self.textview.get_buffer()

        textbuffer.insert(textbuffer.get_end_iter(), '\n')
        textbuffer.insert_pixbuf(textbuffer.get_end_iter(), pixbuf)
        textbuffer.insert(textbuffer.get_end_iter(), '\n')
        textbuffer.apply_tag_by_name(
            'protected',
            textbuffer.get_iter_at_mark(self._input_mark),
            textbuffer.get_end_iter()
        )

        if self._prop_auto_scroll:
            self.textview.scroll_mark_onscreen(textbuffer.get_insert())

        textbuffer.move_mark(self._input_mark, textbuffer.get_end_iter())

        if move_cursor:
            textbuffer.place_cursor(textbuffer.get_iter_at_mark(self._input_mark))

    def write_image(self, filename, move_cursor=True):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        self.write_pixbuf(pixbuf, move_cursor)

    def do_get_property(self, prop):
        if prop.name == 'auto-scroll':
            return self._prop_auto_scroll
        else:
            return super(GtkInterpreterStandardOutput, self).get_property(prop)

    def do_set_property(self, prop, val):
        if prop.name == 'auto-scroll':
            self._prop_auto_scroll = val
        else:
            super(GtkInterpreterStandardOutput, self).set_property(prop, val)

    def get_auto_scroll(self):
        return self.get_property('auto-scroll')

    def set_auto_scroll(self, scroll):
        self.set_property('auto-scroll', scroll)


class GtkInterpreterErrorOutput(GtkInterpreterStandardOutput):
    __gproperties__ = {
        'color': (
            GObject.TYPE_STRING,
            'color',
            'Error output color.',
            '#cc0000',
            GObject.PARAM_READWRITE
        ),
    }

    def __init__(self, textview):
        super(GtkInterpreterErrorOutput, self).__init__(textview)
        self._color = '#cc0000'
        self._update_error_tag()

    def write(self, txt, move_cursor=False, tag_names=['protected', 'error']):
        super(GtkInterpreterErrorOutput, self).write(txt, move_cursor, tag_names)

    def _update_error_tag(self):
        tag_table = self.textview.get_buffer().get_tag_table()

        if tag_table.lookup('error') is None:
            self.textview.get_buffer().create_tag(tag_name='error', foreground=self._color)

        else:
            tag_table.lookup('error').set_property('foreground', self._color)

    def do_get_property(self, prop):
        if prop.name == 'color':
            return self._color

        else:
            return super(GtkInterpreterErrorOutput, self).get_property(prop)

    def do_set_property(self, prop, val):
        if prop.name == 'color':
            self._color = val
            self._update_error_tag()

        else:
            super(GtkInterpreterErrorOutput, self).set_property(prop, val)

    def get_color(self):
        return self.get_property('color')

    def set_color(self, color):
        self.set_property('color', color)


class CommandHistory(object):

    def __init__(self, filename=None):
        super(CommandHistory, self).__init__()
        self._cmds = []
        self._idx = -1
        self._filename = filename
        self._load_from_file()

    # private methods
    def _load_from_file(self):
        if self._filename is not None and os.path.exists(self._filename):
            f = open(self._filename, 'r')
            data = f.read()
            f.close()
            items = data.split('\n')
            items = filter(lambda x: x.strip != '', items)
            self._cmds = list(items)
            self._idx = len(self._cmds) - 1

    def _add_to_file(self, cmd):
        if self._filename is not None:
            f = open(self._filename, 'a')
            f.write(cmd + '\n')
            f.close()

    def _clear_file(self):
        if self._filename is not None and os.path.exists(self._filename):
            f = open(self._filename, 'w')
            f.write('')
            f.close()

    # public methods
    def add(self, cmd):
        cmd = cmd.strip()

        if cmd == '':
            return

        self._cmds.append(cmd)
        self._idx = len(self._cmds)
        self._add_to_file(cmd)

    def clear(self):
        self._cmds = []
        self._idx = -1
        self._clear_file()

    def down(self):
        if self._cmds == [] or self._idx >= len(self._cmds) - 1:
            return None

        else:
            self._idx += 1
            cmd = self._cmds[self._idx]
            return cmd

    def up(self):
        if self._cmds == [] or self._idx <= 0:
            return None

        else:
            self._idx -= 1
            cmd = self._cmds[self._idx]
            return cmd


class CommandCompleter(object):

    def __init__(self, local_vars):
        super(CommandCompleter, self).__init__()
        self._locals = local_vars
        self._make_completer()
        self._n = 0
        self._text = ''

    def _make_completer(self):
        l = {}
        l.update(builtins.__dict__)
        l.update(locals())
        l.update(self._locals)
        self._completer = Completer(l)

    def complete_start(self, text):
        self._make_completer()
        self._text = text
        self._n = -1

        return self.complete()

    def complete(self):
        self._n += 1
        suggest = self._completer.complete(self._text, self._n)

        return suggest

    def complete_back(self):
        self._n -= 1

        if self._n < 0:
            self._n = 0
            return None

        suggest = self._completer.complete(self._text, self._n)

        return suggest


class GtkPyInterpreterWidget(Gtk.VBox):
    __gproperties__ = {
        'auto-scroll': (
            GObject.TYPE_BOOLEAN,
            "auto-scroll",
            'Whether to automatically scroll the output.',
            True,
            GObject.PARAM_READWRITE
        ),
        'font': (
            GObject.TYPE_STRING, 'font',
            'Font definition for the font of the input/output TextView',
            'sans 10',
            GObject.PARAM_READWRITE
        ),
        'margins': (
            GObject.TYPE_INT, 'margins',
            'Size of left and right margin in pixels',
            0,
            100,
            8,
            GObject.PARAM_READWRITE
        ),
        'error-color': (
            GObject.TYPE_STRING,
            'error-color',
            'Error text color.',
            '#cc0000',
            GObject.PARAM_READWRITE
        ),
    }

    __gsignals__ = {
        'stdout-written': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (GObject.TYPE_STRING,)
        ),
        'stderr-written': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (GObject.TYPE_STRING,)
        ),
    }

    name = '__console__'
    line_start = '>>> '
    banner = '\nWelcome to the GtkPyInterpreterWidget :-)'

    def __init__(self, interpreter_locals={}, history_fn=None):
        super(GtkPyInterpreterWidget, self).__init__()

        # properties
        self._prop_auto_scroll = True
        self._prop_font = 'sans 10'
        self._prop_margins = 8
        self._prev_cmd = []
        self._pause_interpret = False
        self._prev_key = -1

        # history
        self._history = CommandHistory(history_fn)

        # completer
        self._completer = CommandCompleter(interpreter_locals)

        # output
        sw = Gtk.ScrolledWindow()
        self.output = Gtk.TextView()
        fontdesc = Pango.FontDescription(self._prop_font)
        self.output.modify_font(fontdesc)
        self.output.set_wrap_mode(Gtk.WrapMode.WORD)
        self.output.set_left_margin(self._prop_margins)
        self.output.set_right_margin(self._prop_margins)
        textbuffer = self.output.get_buffer()
        self._input_mark = textbuffer.create_mark(
            'input_start',
            textbuffer.get_start_iter(),
            True
        )
        sw.add(self.output)
        self.pack_start(sw, True, True, 0)
        self.output.connect('event', self._cb_textview_event)

        # in and out
        self.gtk_stdout = GtkInterpreterStandardOutput(self.output)
        self.gtk_stderr = GtkInterpreterErrorOutput(self.output)

        # locals
        if '__name__' not in interpreter_locals:
            interpreter_locals['__name__'] = self.name

        if '__doc__' not in interpreter_locals:
            interpreter_locals['__doc__'] = self.__doc__

        if '__class__' not in interpreter_locals:
            interpreter_locals['__class__'] = self.__class__.__name__

        interpreter_locals['clear'] = self._clear
        interpreter_locals['stdout'] = self.gtk_stdout
        interpreter_locals['stderr'] = self.gtk_stderr

        # interpreter
        self.interpreter = GtkInterpreter(
            self.gtk_stdout,
            self.gtk_stderr,
            interpreter_locals
        )
        self.gtk_stdout.connect('output-written', self._cb_stdout_written)
        self.gtk_stderr.connect('output-written', self._cb_stderr_written)

        # write banner to output
        self.gtk_stdout.write(self.banner + '\n\n' + self.line_start)

    # callbacks
    def _cb_textview_event(self, textview, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            textbuffer = textview.get_buffer()

            if event.keyval == 65362:
                # up
                cmd = self._history.up()

                if cmd is not None:
                    start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                    end_iter = textbuffer.get_end_iter()
                    textbuffer.delete(start_iter, end_iter)
                    start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                    textbuffer.insert(start_iter, cmd)
                self._prev_key = event.keyval

                return True

            elif event.keyval == 65364:
                # down
                cmd = self._history.down()

                if cmd is not None:
                    start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                    end_iter = textbuffer.get_end_iter()
                    textbuffer.delete(start_iter, end_iter)
                    start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                    textbuffer.insert(start_iter, cmd)

                else:
                    start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                    end_iter = textbuffer.get_end_iter()
                    textbuffer.delete(start_iter, end_iter)

                self._prev_key = event.keyval

                return True

            elif event.keyval == 65293:
                # return
                start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                end_iter = textbuffer.get_end_iter()
                txt = textbuffer.get_text(start_iter, end_iter, True)
                textbuffer.apply_tag_by_name('protected', start_iter, end_iter)
                textbuffer.insert(textbuffer.get_end_iter(), '\n')
                self._cmd_receive(txt)
                self._prev_key = event.keyval

                return True

            elif event.keyval == 65360:
                # Home
                textbuffer.place_cursor(textbuffer.get_iter_at_mark(self._input_mark))
                self._prev_key = event.keyval

                return True

            elif event.keyval == 65367:
                # End
                textbuffer.place_cursor(textbuffer.get_end_iter())
                self._prev_key = event.keyval

                return True

            elif event.keyval == 65289:
                # tab for completion
                # get suggestion
                start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                end_iter = textbuffer.get_end_iter()
                txt = textbuffer.get_text(start_iter, end_iter, True)

                if not self._prev_key in [65056, 65289]:
                    suggest = self._completer.complete_start(txt)

                else:
                    suggest = self._completer.complete()

                self._prev_key = event.keyval

                # display suggestion
                if suggest is not None:
                    start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                    end_iter = textbuffer.get_end_iter()
                    textbuffer.delete(start_iter, end_iter)
                    start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                    textbuffer.insert(start_iter, suggest)

                return True

            elif event.keyval == 65056:
                # tab (back) for completion
                # check whether completion was started
                if not self._prev_key in [65056, 65289]:
                    return True

                # get suggestion
                start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                end_iter = textbuffer.get_end_iter()
                txt = textbuffer.get_text(start_iter, end_iter, True)
                suggest = self._completer.complete_back()
                self._prev_key = event.keyval

                # display suggestion
                if suggest is not None:
                    start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                    end_iter = textbuffer.get_end_iter()
                    textbuffer.delete(start_iter, end_iter)
                    start_iter = textbuffer.get_iter_at_mark(self._input_mark)
                    textbuffer.insert(start_iter, suggest)

                return True

            elif event.keyval == 65505:
                # Shift modifier, has to be caught to prevent from setting self._prev_key
                pass

            else:
                self._prev_key = event.keyval

    def _cb_stdout_written(self, stdout, text):
        self.emit('stdout-written', text)

    def _cb_stderr_written(self, stderr, text):
        self.emit('stderr-written', text)

    # private methods
    def _clear(self):
        self.output.get_buffer().set_text('')

    def _cmd_receive(self, cmd):
        # add to history
        self._history.add(cmd)
        # add output
        line_start = '' if self._prev_cmd != [] else self.line_start
        # interpret command
        if not self._pause_interpret:
            res = self.interpreter.runsource(cmd)
            self.interpreter.showsyntaxerror()
        else:
            res = False

        if res is True:
            # wait for more input
            self.gtk_stdout.write('...', True)
            self._prev_cmd.append(cmd)
            self._pause_interpret = True

        else:
            if self._prev_cmd != [] and cmd.strip() == '':
                # compile multiline input
                self._prev_cmd.append(cmd)
                ncmd = '\n'.join(self._prev_cmd) + '\n'
                res = self.interpreter.runsource(ncmd)
                self._prev_cmd = []
                self._pause_interpret = False

            elif self._prev_cmd != []:
                self.gtk_stdout.write('...')
                self._prev_cmd.append(cmd)

            else:
                self._prev_cmd = []
                self.gtk_stdout.write(line_start, True)

    # gobject property methods
    def do_get_property(self, prop):
        if prop.name == 'auto-scroll':
            return self._prop_auto_scroll

        elif prop.name == 'font':
            return self._prop_font

        elif prop.name == 'margins':
            return self._prop_margins

        elif prop.name == 'error-color':
            return self.gtk_stderr.get_color()

        else:
            return super(GtkPyInterpreterWidget, self).do_get_property(prop)

    def do_set_property(self, prop, val):
        if prop.name == 'auto-scroll':
            self._prop_auto_scroll = val
            self._gtk_stdout.set_auto_scroll(val)
            self._gtk_stderr.set_auto_scroll(val)

        elif prop.name == 'font':
            self._prop_font = val
            fontdesc = Pango.FontDescription(self._prop_font)
            self.output.modify_font(fontdesc)

        elif prop.name == 'margins':
            self._prop_margins = val
            self.output.set_left_margin(self._prop_margins)
            self.output.set_right_margin(self._prop_margins)

        elif prop.name == 'error-color':
            self.gtk_stderr.set_color(val)

        else:
            super(GtkPyInterpreterWidget, self).set_property(prop, val)

    # public methods
    def write(self, txt):
        textbuffer = self.output.get_buffer()
        textiter = textbuffer.get_end_iter()
        textbuffer.insert(textiter, txt)

    def get_auto_scroll(self):
        return self.get_property('auto-scroll')

    def get_error_color(self):
        return self.get_property('error-color')

    def get_font(self):
        return self.get_property('font')

    def get_margins(self):
        return self.get_property('margins')

    def set_auto_scroll(self, scroll):
        self.set_property('auto-scroll', scroll)

    def set_error_color(self, color):
        self.set_property('error-color', color)

    def set_font(self, font):
        self.set_property('font', font)

    def set_margins(self, pixels):
        self.set_property('margins', pixels)

    def get_output_buffer(self):
        return self.output.get_buffer()

    def get_history(self):
        return self._history


def run():
    w = Gtk.Window()
    w.set_title('Gtk3 Interactive Python Interpreter')
    w.set_default_size(800, 600)
    w.connect('destroy', Gtk.main_quit)
    c = GtkPyInterpreterWidget({'window': w}, '/tmp/pyrc')
    c.set_font('LiberationMono 10')
    w.add(c)
    w.show_all()
    Gtk.main()


if __name__ == '__main__':
    run()
