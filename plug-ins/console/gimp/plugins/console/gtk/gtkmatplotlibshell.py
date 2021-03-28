import tempfile
import time

from gi.repository import Gtk
from gi.repository import GdkPixbuf

import matplotlib
matplotlib.use('Gtk3Agg')
import matplotlib.pylab

from .gtkpyinterpreter import GtkPyInterpreterWidget


class GtkMatplotlibShellWidget(GtkPyInterpreterWidget):
    _figsize = (8, 6)
    _dpi = 72
    banner = '\nWelcome to the matplotlib demo!'

    def __init__(self, interpreter_locals={}, history_fn=None):
        self._auto_plot = True
        this_locals = {}
        this_locals.update(matplotlib.pylab.__dict__)
        this_locals['pylab'] = matplotlib.pylab
        this_locals['autoplot'] = self._toggle_auto_plot
        this_locals['show'] = self._pylab_show
        this_locals['plot'] = self._pylab_plot
        this_locals['xlabel'] = self._pylab_xlabel
        this_locals['ylabel'] = self._pylab_ylabel
        this_locals['clabel'] = self._pylab_clabel
        this_locals['legend'] = self._pylab_legend
        this_locals['title'] = self._pylab_title
        this_locals['errorbar'] = self._pylab_errorbar
        this_locals['semilogy'] = self._pylab_semilogy
        this_locals['pie'] = self._pylab_pie
        this_locals['bar'] = self._pylab_bar
        this_locals['hist'] = self._pylab_hist
        this_locals['imshow'] = self._pylab_imshow
        this_locals['contour'] = self._pylab_contour
        this_locals['contourf'] = self._pylab_contourf
        this_locals['colorbar'] = self._pylab_colorbar
        this_locals.update(interpreter_locals)
        super(GtkMatplotlibShellWidget, self).__init__(this_locals, history_fn)

    def _toggle_auto_plot(self, enable=True):
        self._auto_plot = enable

    def _pylab_show(self):
        fig = matplotlib.pylab.gcf()
        temp_fn = tempfile.NamedTemporaryFile(suffix=".png")
        fig.savefig(temp_fn, dpi=self._dpi)
        self.gtk_stdout.write_image(temp_fn.name)

    def _pylab_plot(self, *args, **kwargs):
        matplotlib.pylab.plot(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_xlabel(self, *args, **kwargs):
        matplotlib.pylab.xlabel(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_ylabel(self, *args, **kwargs):
        matplotlib.pylab.ylabel(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_clabel(self, *args, **kwargs):
        matplotlib.pylab.clabel(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_legend(self, *args, **kwargs):
        matplotlib.pylab.legend(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_title(self, *args, **kwargs):
        matplotlib.pylab.title(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_errorbar(self, *args, **kwargs):
        matplotlib.pylab.errorbar(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_semilogy(self, *args, **kwargs):
        matplotlib.pylab.semilogy(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_pie(self, *args, **kwargs):
        matplotlib.pylab.pie(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_bar(self, *args, **kwargs):
        matplotlib.pylab.bar(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_hist(self, *args, **kwargs):
        matplotlib.pylab.hist(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_imshow(self, *args, **kwargs):
        matplotlib.pylab.imshow(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_contour(self, *args, **kwargs):
        matplotlib.pylab.contour(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_contourf(self, *args, **kwargs):
        matplotlib.pylab.contourf(*args, **kwargs)
        if self._auto_plot: self._pylab_show()

    def _pylab_colorbar(self, *args, **kwargs):
        matplotlib.pylab.colorbar(*args, **kwargs)
        if self._auto_plot: self._pylab_show()


def run():
    w = Gtk.Window()
    w.set_title('Gtk3 Matplotlib shell')
    w.set_default_size(800, 600)
    w.connect('destroy', Gtk.main_quit)
    c = GtkMatplotlibShellWidget({'window': w}, '/tmp/matplotlib.pyrc')
    c.set_font('LiberationMono 10')
    w.add(c)
    w.show_all()
    Gtk.main()


if __name__ == '__main__':
    run()
