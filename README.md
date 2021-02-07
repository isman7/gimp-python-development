# gimp-python-development
Some ideas and tools to develope Python 3.8 plugins for GIMP 2.99.4. GIMP 2.99.4 is the latest unstable pre-release of GIMP 3. It suppots Python 3,
however it's documentation is rather poor, and also one thing that always annoyed me was it uses the system Python distribution and adds on top
of it some libreries. Also, a GIMP plugin must run inside GIMP... So, let's hack to have a proper developing environment!

## Install GIMP 2.99.4

GIMP 2.99.4 cames with pre-compiled binaries in a flatpak distribution. So first of all if you don't have flatpak, assuming you are on a Debian-based
Linux distro: 

```
$ sudo apt install flatpak
```

Flatpak is a distribution system, like Apt, but focused on end-user applications and isolation. Like Docker, it isolates the compiled application
in it's own Sandbox, however it is not actually virtualized. Let's install GIMP 2.99.4: 

```
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/beta-repo/flathub.flatpakrepo
flatpak install --user https://flathub.org/beta-repo/appstream/org.gimp.GIMP.flatpakref
```
Say yes to permissions, etc. Then you will be able to run GIMP from flatpak: 

```
flatpak run org.gimp.GIMP//beta
```

## Understanding which Python is using GIMP 

So, in order to start developing we must understad which Python executable is using GIMP. This was tricky to me at first, but it actually has 
a very nice outcome. As I mentioned, GIMP uses the system Python executable, if we go to the menu entry 
`Filters > Development > Python-Fu > Python Console` a window will be promt with a Python console that will say: 

```
GIMP 2.99.4 Python Console
Python 3.8.6 (default, Nov 10 2011, 15:00:00) 
[GCC 10.2.0]
>>> 
```

My main issue here to locate this Python was that I didn't have this Python installed in my system, because I'm using Python 3.9. Although, I don't
have any experience with Flatpak, Docker experience suggested that was using the Python provided by its isolation environment. So, searching 
the Flatpak documentation I found this approach: 

```
flatpak run --command=python org.gimp.GIMP//beta
```

And magic happened: 

```
Python 3.8.6 (default, Nov 10 2011, 15:00:00) 
[GCC 10.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

Then, if we use this trick using `--comand=bash` instead of Python executable we will be having the shell of the Sandbox. So, when you thought it
this is very good news. Because, we finally have an isolated Python environment for GIMP, a tricky one, but we have it!!

## Prepare the environment

As it is thought as a minimal environment, it lacks some basic tools for developing Python code, let's install some of them. First, things 
firts, let's ensure pip is installed: 

```
$ python -m ensurepip
```

Once installed, update pip using pip to check pip works!

```
$ python -m pip install -U pip
```

One pip is updated let's grab at least IPython:

```
$ python -m pip install ipython
```


