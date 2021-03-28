First ideas on modify the GIMP Python interpreter to be more interactive.

As for now, code from two sources has been grabbed: 

- [GIMP's Python Console](https://gitlab.gnome.org/GNOME/gimp/-/tree/master/plug-ins/python/python-console) under GPLv3
- [SvenFestersen's GtkPyInterpreter](https://github.com/SvenFestersen/GtkPyInterpreter) under GPLv3

### Update (28/03/21):

- Huge refactor in original source codes. 
- A namespace python package structure has been implemented, adapted to GIMPs needs. 
- Logic from pure GTK3 is being split from GIMPs logic, then "apps" should have an isolated layer which runs outside GIMP.
- Running 4 different Python Console approaches only changing a flag, to explore them:
    - [console.ConsoleDialog.run](gimp/plugins/console/gtk/pyconsole.py): The current GIMP python console with the GIMP logic.
    - [pyconsole.run](gimp/plugins/console/gtk/pyconsole.py): Only the widget of the python console of the current GIMP pyhthon console.
    - [gtkpyinterpreter.run](gimp/plugins/console/gtk/gtkpyinterpreter.py): SvenFestersen's Python Console. Has a problem with a constant `None: None` output.
    - [gtkmatplotlibshell.run](gimp/plugins/console/gtk/gtkpyinterpreter.py): SvenFestersen's Python Console with matplotlib integration!
    
- The main problem integrating IPython is that the current approach (by importing it and call `IPython.embed()`) yields 
to a problem with the parsing of the inputs. For example:

```
In [1]: import os
  File "<ipython-input-1-5c84a8230b9f>", line 1
    invalid syntax (<string>, line 1)
            ^
SyntaxError: invalid syntax


In [2]: a = 10
  File "<ipython-input-2-5c84a8230b9f>", line 1
    invalid syntax (<string>, line 1)
            ^
SyntaxError: invalid syntax


In [3]: hola
  File "<ipython-input-3-74399d33e912>", line 1
    name 'hola' is not defined
         ^
SyntaxError: invalid syntax
```