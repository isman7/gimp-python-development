First ideas on modify the GIMP Python interpreter to be more interactive.

As for now, code from two sources has been grabbed: 

- [GIMP's Python Console](https://gitlab.gnome.org/GNOME/gimp/-/tree/master/plug-ins/python/python-console) under GPLv3
- [SvenFestersen's GtkPyInterpreter](https://github.com/SvenFestersen/GtkPyInterpreter) under GPLv3

### Update (28/03/21):

- Huge refactor in original source codes. 
- A namespace python package structure has been implemented, adapted to GIMPs needs. 
- Logic from pure GTK3 is being split from GIMPs logic, then "apps" should have an isolated layer which runs outside GIMP.
- Integrating IPython might not be possible, the current approach should be fixing this current consoles and try to mix them...