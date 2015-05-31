#!/usr/bin/env python
# encoding: utf-8

import os
from os.path import join, basename, isdir
from glob import glob
import hashlib
from zipfile import ZipFile, ZIP_STORED

VERSION="0.0.1"

class Meta(dict):
    def __init__(self):
        dict.__init__(self)
        self["VERSION"] = VERSION

    def tostring(self):
        return u"""<?xml version="1.0" encoding="UTF-8"?>
<meta:meta>
        <meta:generator>Krita resource bundle creator v.{VERSION}</meta:generator>
        <dc:author>{author}</dc:author>
        <dc:description>{description}</dc:description>
        <meta:initial-creator>{initialcreator}</meta:initial-creator>
        <dc:creator>{creator}</dc:creator>
        <meta:creation-date>{date}</meta:creation-date>
        <meta:dc-date>{date}</meta:dc-date>
        <meta:meta-userdefined meta:name="email" meta:value="{email}"/>
        <meta:meta-userdefined meta:name="license" meta:value="{license}"/>
        <meta:meta-userdefined meta:name="website" meta:value="{website}"/>
</meta:meta>""".format(**self)

class Bundle(object):
    def __init__(self):
        self.brushes = []
        self.presets = []
        self.meta = None

    def get_files(self, dir):
        result = []
        for (d, _, files) in os.walk(dir):
            for f in files:
                path = join(d,f)
                result.append(path)
        return result

    def read_brushes(self, brushdir):
        if not brushdir:
            return
        #os.chdir(brushdir)
        self.brushes.extend(self.get_files(brushdir))

    def read_presets(self, presetsdir):
        if not presetsdir:
            return
        #os.chdir(presetsdir)
        self.presets.extend(self.get_files(presetsdir))

    def md5(self, fname):
        m = hashlib.md5()
        f = open(fname, 'r')
        s = f.read()
        f.close()
        m.update(s)
        return m.hexdigest()

    def manifest_entry(self, mtype, fname):
        vs = dict(mtype=mtype, fname=fname, md5=self.md5(fname))
        return """<manifest:file-entry manifest:media-type="{mtype}" manifest:full-path="{fname}" manifest:md5sum="{md5}"/>
""".format(**vs)

    def format_manifest(self):
        s = """<?xml version="1.0" encoding="UTF-8"?>
"""
        s += """<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">
"""
        s += """<manifest:file-entry manifest:media-type="application/x-krita-resourcebundle" manifest:full-path="/"/>
"""
        for fname in self.brushes:
            s += self.manifest_entry('brushes', fname)
        for fname in self.presets:
            s += self.manifest_entry('paintoppresets', fname)
        s += """</manifest:manifest>"""
        return s

    def create(self, zipname, meta, brushdir, presetsdir, preview):
        self.read_brushes(brushdir)
        self.read_presets(presetsdir)

        manifest = self.format_manifest()

        zf = ZipFile(zipname, 'w', ZIP_STORED)
        zf.writestr("mimetype", "application/x-krita-resourcebundle")
        zf.writestr("META-INF/manifest.xml", manifest)
        zf.writestr("meta.xml", meta.tostring())
        zf.write(preview, "preview.png")
        for fname in self.brushes:
            zf.write(fname, fname)
        for fname in self.presets:
            zf.write(fname, fname)

        zf.close()

def ask(prompt, default=None):
    t = " [{}]: ".format(default) if default is not None else ": "
    r = raw_input(prompt + t)
    if not r:
        return default
    else:
        return r

if __name__ == "__main__":
    meta = Meta()
    author = meta["author"] = ask("Author")
    meta["description"] = ask("Description")
    meta["initialcreator"] = ask("Initial creator", author)
    meta["creator"] = ask("Creator", author)
    meta["date"] = ask("Date")
    meta["email"] = ask("Email")
    meta["website"] = ask("Website")
    meta["license"] = ask("License")

    zipname = ask("Bundle file name")
    brushdir = ask("Brushes directory", "brushes")
    presetsdir = ask("Presets directory", "paintoppresets")
    preview = ask("Preview", "preview.png")

    bundle = Bundle()
    bundle.create(zipname, meta, brushdir, presetsdir, preview)








