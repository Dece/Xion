Xion
====

WORK IN PROGRESS

Xion is a JSON interface to Xfconf, using a slightly modified xfconf-query
bin. Backup and restore Xfce settings in VCS-friendly files.

This can be useful to synchronise custom keybinds across several Xfce
installations.



Usage
-----

```bash
# Export custom commands to JSON.
$ xion -e xfce4-keyboard-shortcuts /commands/custom commands.json
# Import them on another machine.
$ xion -i commands.json
# Want to clear existing commands to keep only those in commands.json?
$ xion -i commands.json -r
```

More info with `xion --help`.



Features
--------

- Export channel settings, filtering on user-provided root, to JSON files.
- Import channel settings from those JSON files.
- Imported settings are immediately applied to your session.
- Replace entire channel setting trees, or just update with provided values.
- JSON files have a predictable formatting for easy versioning.



Context
-------

Xion comes from the need to share parts of the Xfce settings between several
computers.

> Why don't you just version the Xfconf XML files?

I got frustrated with the way Xfconf stored settings on disk: its XML files have
unpredictable tag sorting and some volatile values, and Xfconf does not read
those settings unless you log back in, and this is if you don't overwrite them
in the process. This makes diffing modifications cumbersome, especially when
trying to share parts of my settings in a Git repository. I needed a way to dump
and restore only some parts of my settings.

Xfconf is the daemon storing and providing most Xfce configuration values,
called properties. Sadly, it is not possible to manipulate these values without
building against libxfconf, which itself uses Glib, which I simply don't know
and don't want to use, either as a C program or using FFI. The lazy way is to
use xion-query, a modified build of the xfconf-query CLI tool.

> Why don't you just use xfconf-query?

It simply does not have a very machine-readable interface, so Xion uses a
modified build to work smoothly, removing some output aimed at humans and adding
value types to its output. I tried to make it easy to get xion-query.



Installation
------------

### Get xion-query

Go to my [Xfconf fork](https://github.com/Dece/xfconf/releases/) to get a build
or find instructions on how to build it.

If you want to build it manually, checkout the tags named "xion-<VERSION>". It
is possible to build xion-query with Docker if you don't want to mess around
finding the various dependencies.

Once you have your build, name it `xion-query`, make it executable and place it
somewhere in your path, e.g. in `/usr/local/bin/`.

### Get xion

Right now Xion is not packaged, just download the repo, this is on the todolist.
