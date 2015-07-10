#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
import sys
from os.path import join, basename, isdir, isfile, expanduser
import shutil
import hashlib
from fnmatch import fnmatch
from glob import glob
from zipfile import ZipFile, ZIP_STORED
#from xml.sax.saxutils import escape as xmlescape
from lxml import etree
from lxml.builder import ElementMaker

try:
    import ConfigParser as configparser
except ImportError:
    try:
        import configparser
    except ImportError:
        raise ImportError("Neither ConfigParser nor configparser module not found")

from bundle import Meta, Bundle

class Config(configparser.ConfigParser):
    SECTION = "Bundle"

    def __init__(self, filename=None):
        configparser.ConfigParser.__init__(self)
        self._filename = filename
        if filename is not None:
            self.read(filename)

    def ask(self, option, default=None, config_option=None):
        if self._filename is None:
            t = " [{}]: ".format(default) if default is not None else ": "
            r = raw_input(option + t)
            if not r:
                return default
            else:
                return r.decode('utf-8')
        else:
            if config_option is not None:
                option = config_option
            if self.has_option(self.SECTION, option):
                return self.get(self.SECTION, option).decode('utf-8')
            else:
                return default

if __name__ == "__main__":

    if len(sys.argv) == 2:
        cfgfile = sys.argv[1]
    else:
        cfgfile = None
    config = Config(cfgfile)

    meta = Meta()
    author = meta.author = config.ask("Author")
    meta.description = config.ask("Description")
    meta.initial_creator = config.ask("Initial creator", author)
    meta.creator = config.ask("Creator", author)
    meta.date = config.ask("Date")
    meta.email = config.ask("Email")
    meta.website = config.ask("Website")
    meta.license = config.ask("License")

    zipname = config.ask("Bundle file name")
    brushdir = config.ask("Brushes directory", "brushes")
    brushmask = config.ask("Brush files mask", "*.gbr;*.gih;*.png")
    patdir = config.ask("Patterns directory", "patterns")
    patmask = config.ask("Pattern files mask", "*.pat")
    presetsdir = config.ask("Presets directory", "paintoppresets")
    presetmask = config.ask("Preset files mask", "*.kpp")
    skip_bad = config.ask("Skip presets with broken references", default=False, config_option="Skip bad presets")
    skip_unused_brushes = config.ask("Skip unused brushes", default=False)
    autopopulate = config.ask("Automatically add resources from directory", default=None, config_option="Auto add resources")
    if autopopulate is not None:
        autopopulate = autopopulate.split(";")
        autopopulate = map(expanduser, autopopulate)
        autopopulate = sum(map(glob, autopopulate), [])
    preview = config.ask("Preview", "preview.png")

    bundle = Bundle()
    bundle.prepare(brushdir, brushmask, presetsdir, presetmask, patdir, patmask)
    ok = bundle.check(skip_bad=skip_bad, resourcedir=autopopulate, skip_unused_brushes=skip_unused_brushes)
    if not ok:
        print("Bundle contains references to resources outside the bundle. You probably need to put required resources to the bundle itself.")
    bundle.create(zipname, meta, preview)

