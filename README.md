Krita bundle create & validate scripts
======================================

This is a set of (python) scripts to create Krita resource bundle files, and do some operations
with them. The set consists of the following scripts:

* create-krita-bundle.py - Create bundle file from raw set of resource files.
* dump-kpp.py - dump XML preset description from `*.kpp` preset file.
* extract-external-links.py - output all references to other resource files from given resource files or bundles.
* find-unused.py - find brush tip files (`*.gbr`, `*.gih` and so on), unused by your presets.
* find-missing.py - detect brush tip files that were not included into bundle file.
* add-to-bundle.py - add resources to bundle manually.

USAGE: create-krita-bundle.py
-----------------------------

* Create a directory, say, `~/bundle`.
* Put 'brushes' and 'paintoppresets' directories from old resource archive to that new directory.
* Put also preview.png file into the same directory.
* Chdir to `~/bundle`.
* Run `create-krita-bundle.py` from console/terminal emulator.
* It will ask you several questions about the bundle being created.
* As a result, it will produce `*.bundle` file.
* Import that file to Krita to test that it works as expected.

The script can also read all answers from the config file specified as command line parameter,
for example

```
  create-krita-bundle.py test.bundleconfig
```

The bundleconfig file is INI-style config with the following options:

```
[Bundle]
Author = Author of bundle
Description = Description of the bundle
Initial creator = Initial creator of resources
Creator = Creator of the bundle file
Date = Creation date
Email = Author email
Website = Bundle website
License = Bundle license
Brushes directory = path to directory with brush tip files, by default ./brushes/
Brush files mask = by default "*.gbr;*.gih;*.png"
Patterns directory = path to directory with patterns, by default ./patterns/
Pattern files mask = by default "*.pat"
Presets directory = path to directory with presets, by default ./paintoppresets/
Preset files mask = by default "*.kpp"
Skip bad presets = set to "true" if you wish script to skip presets which refer to unexisting brush files
Skip unused brushes = set to "true" if you wish script to skip brush tip files that are not used by presets
Auto add resources = specify paths to directories with brush tip files, or bundle files, semicolon-separated;
#                    the script will automatically add brush files from these directories or bundles,
#                    if they are referred from presets
Preview = preview file name, by default preview.png
Bundle file name = test.bundle
```

See example of config file in bundles/ramon.bundleconfig.

If PIL or Pillow module is available, then the script will check references from `*.kpp` files to
required brush files. It will print a warning for each not found brush.

Script can automatically put required brush files to the bundle from specified directories or bundles.
Sample of config line:

```
Auto add resources = ~/.kde/share/apps/krita/brushes/;~/.kde/share/apps/krita/bundles/*.bundle
```

USAGE: dump-kpp.py
------------------

Run as 

```
$ dump-kpp.py filename.kpp
```

The script will dump XML description of preset from kpp file.

USAGE: extract-external-links.py
--------------------------------

Run as

```
$ extract-external-links.py file1 file2...
```

Both `*.kpp` and `*.bundle` files can be passed. The script will print all references to external resource files, used by presets specified.

USAGE: find-unused.py
---------------------

Run as

```
$ find-unused.py -p ~/.kde/share/apps/krita/paintoppresets \
    -b ~/.kde/share/apps/krita/brushes \
    -B ~/.kde/share/apps/krita/bundles
```

Run `find-unused.py --help` to list of all options available.

The script will search for brush tip files that are not used by your
presets. By default the script just prints names of such files.
With --remove option, it will remove them. NOTE: `*.abr` brushes are
currently not supported, so be very careful with `--remove` option if
you have some `*.abr` brushes.
With `-i` option, the script will search for used brushes instead of unused.

USAGE: find-missing.py
----------------------

Run as

```
$ find-missing.py filename.bundle
```

or

```
$ find-missing.py --embed \
    -b /path1/brushes \
    [ -b /path2/brushes ... ] \
    filename.bundle
```

The script will check provided bundle for references from presets to brush tip
files, that are not included into bundle. It will print names of missing brush
tips to stdout. With `--embed` option, it will also search for missing brush
tip files in directories passed via `-b` (`--brushes`) command line option, and
add brush tips that it was able to find to the bundle. Original bundle file
will be automatically saved as backup, with `.bak` suffix.

USAGE: add-to-bundle.py
-----------------------

Run as

```
$ add-to-bundle.py filename.bundle {brush|preset|pattern} /path/to/resource
```

for example

```
$ add-to-bundle.py test.bundle brush mybrush1.gih
```

The script will add specified resource file into bundle archive. It will also
update bundle's manifest.xml correspondingly. Original bundle file will be
automatically saved as backup, with `.bak` suffx.

