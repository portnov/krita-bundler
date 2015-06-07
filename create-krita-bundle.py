#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
import sys
from os.path import join, basename, isdir
import hashlib
from fnmatch import fnmatch
from zipfile import ZipFile, ZIP_STORED
from xml.sax.saxutils import escape as xmlescape
from lxml import etree
from lxml.builder import ElementMaker

try:
    import ConfigParser as configparser
except ImportError:
    try:
        import configparser
    except ImportError:
        raise ImportError("Neither ConfigParser nor configparser module not found")

from extractor import KPP

VERSION="0.0.1"

META_NAMESPACE = "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
#META = "{" + META_NAMESPACE + "}"
DC_NAMESPACE = "http://dublincore.org/documents/dcmi-namespace/"
#DC = "{" + DC_NAMESPACE + "}"
NSMAP = dict(meta=META_NAMESPACE, dc=DC_NAMESPACE)

META = ElementMaker(namespace=META_NAMESPACE, nsmap=NSMAP)
DC = ElementMaker(namespace=DC_NAMESPACE, nsmap=NSMAP)

class Meta(object):

    def __init__(self):
        self.author = "Unknown Artist"
        self.description = "Not provided"
        self.initial_creator = self.author
        self.creator = self.author
        self.date = "Unknown"
        self.email = ""
        self.license = ""
        self.website = ""

    def toxml(self):
        meta = META.meta(
                    META.generator("Krita resource bundle creator v.{}".format(VERSION)),
                    DC.author(self.author),
                    DC.description(self.description),
                    META("initial-creator", self.initial_creator),
                    DC.creator(self.creator),
                    META("creation-date", self.date),
                    META("dc-date", self.date),
                    META("meta-userdefined", name="email", value=self.email),
                    META("meta-userdefined", name="license", value=self.license),
                    META("meta-userdefined", name="website", value=self.website)
              )
        return meta

    def tostring(self):
        return etree.tostring(self.toxml(), xml_declaration=True, pretty_print=True, encoding="UTF-8")

    def wrap(self):
        res = dict()
        for k, v in self.iteritems():
            res[k] = xmlescape(v)
        return res

class Bundle(object):
    def __init__(self):
        self.brushes = []
        self.presets = []
        self.patterns = []
        self.meta = None

    def fnmatch(self, name, mask):
        masks = mask.split(";")
        for m in masks:
            if fnmatch(name, m):
                return True
        return False

    def get_files(self, dir, masks):
        result = []
        for (d, _, files) in os.walk(dir):
            for f in files:
                if f.startswith('.'):
                    continue
                if not self.fnmatch(f, masks):
                    continue
                path = join(d,f)
                result.append(path)
        return result

    def read_brushes(self, brushdir, mask):
        if not brushdir:
            return
        self.brushes.extend(self.get_files(brushdir, mask))

    def read_presets(self, presetsdir, mask):
        if not presetsdir:
            return
        self.presets.extend(self.get_files(presetsdir, mask))

    def read_patterns(self, patdir, mask):
        if not patdir:
            return
        self.brushes.extend(self.get_files(patdir, mask))

    def find_brush(self, name):
        #print("Checking for {}".format(name))
        for brush in self.brushes:
            if basename(brush) == name:
                #print("Found")
                return True
        return False

    def check(self):
        result = True
        for fname in self.presets:
            #print("Checking {}".format(fname))
            kpp = KPP(fname)
            links = kpp.get_links()
            requiredBrushFile = links.get('requiredBrushFile', None)
            #print("Required brush file: {}".format(requiredBrushFile))
            if requiredBrushFile:
                ok = self.find_brush(requiredBrushFile)
                if not ok:
                    print("Warning: required brush file {} not found for preset {}".format(requiredBrushFile, fname))
                    result = False
        return result


    def md5(self, fname):
        m = hashlib.md5()
        f = open(fname, 'r')
        s = f.read()
        f.close()
        m.update(s)
        return m.hexdigest()

    def manifest_entry(self, mtype, fname):
        vs = dict(mtype=mtype, fname=fname.decode('utf-8'), md5=self.md5(fname))
        return u"""<manifest:file-entry manifest:media-type="{mtype}" manifest:full-path="{fname}" manifest:md5sum="{md5}"/>
""".format(**vs)

    def format_manifest(self):
        s = u"""<?xml version="1.0" encoding="UTF-8"?>
"""
        s += u"""<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">
"""
        s += u"""<manifest:file-entry manifest:media-type="application/x-krita-resourcebundle" manifest:full-path="/"/>
"""
        for fname in self.brushes:
            s += self.manifest_entry('brushes', fname)
        for fname in self.patterns:
            s += self.manifest_entry('patterns', fname)
        for fname in self.presets:
            s += self.manifest_entry('paintoppresets', fname)
        s += u"""</manifest:manifest>"""
        return s.encode('utf-8')

    def prepare(self, brushdir, brushmask, presetsdir, presetmask, patdir, patmask):
        self.read_brushes(brushdir, brushmask)
        self.read_presets(presetsdir, presetmask)
        self.read_patterns(patdir, patmask)

    def create(self, zipname, meta, preview):
        manifest = self.format_manifest()

        zf = ZipFile(zipname, 'w', ZIP_STORED)
        zf.writestr("mimetype", "application/x-krita-resourcebundle")
        zf.writestr("META-INF/manifest.xml", manifest)
        zf.writestr("meta.xml", meta.tostring())
        zf.write(preview, "preview.png")
        for fname in self.brushes:
            zf.write(fname, fname)
        for fname in self.patterns:
            zf.write(fname, fname)
        for fname in self.presets:
            zf.write(fname, fname)

        zf.close()

class Config(configparser.ConfigParser):
    SECTION = "Bundle"

    def __init__(self, filename=None):
        configparser.ConfigParser.__init__(self)
        self._filename = filename
        if filename is not None:
            self.read(filename)

    def ask(self, option, default=None):
        if self._filename is None:
            t = " [{}]: ".format(default) if default is not None else ": "
            r = raw_input(option + t)
            if not r:
                return default
            else:
                return r.decode('utf-8')
        else:
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
    preview = config.ask("Preview", "preview.png")

    bundle = Bundle()
    bundle.prepare(brushdir, brushmask, presetsdir, presetmask, patdir, patmask)
    ok = bundle.check()
    if not ok:
        print("Bundle contains references to resources outside the bundle. You probably need to put required resources to the bundle itself.")
    bundle.create(zipname, meta, preview)

