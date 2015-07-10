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

from extractor import KPP

VERSION="0.0.1"

MIMETYPE = "application/x-krita-resourcebundle"

META_NAMESPACE = "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
DC_NAMESPACE = "http://dublincore.org/documents/dcmi-namespace/"
MANIFEST_NAMESPACE = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" 
MANIFEST = "{"+MANIFEST_NAMESPACE+"}"

NSMAP = dict(meta=META_NAMESPACE, dc=DC_NAMESPACE, manifest=MANIFEST_NAMESPACE)

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

    def userdefined(self, name, value):
        tag = META("meta-userdefined")
        tag.attrib["{"+META_NAMESPACE+"}name"] = name
        tag.attrib["{"+META_NAMESPACE+"}value"] = value
        return tag

    def toxml(self):
        meta = META.meta(
                    META.generator("Krita resource bundle creator v.{}".format(VERSION)),
                    DC.author(self.author),
                    DC.description(self.description),
                    META("initial-creator", self.initial_creator),
                    DC.creator(self.creator),
                    META("creation-date", self.date),
                    META("dc-date", self.date),
                    self.userdefined("email", self.email),
                    self.userdefined("license", self.license),
                    self.userdefined("website", self.website)
              )
        return meta

    def tostring(self):
        return etree.tostring(self.toxml(), xml_declaration=True, pretty_print=True, encoding="UTF-8")

def md5(fname):
    m = hashlib.md5()
    f = open(fname, 'r')
    s = f.read()
    f.close()
    m.update(s)
    return m.hexdigest()

class Manifest(object):
    def __init__(self):
        pass
    
    @staticmethod
    def new():
        m = Manifest()
        m._manifest = etree.Element(MANIFEST+"manifest", nsmap=NSMAP)
        m._manifest.attrib[MANIFEST+"version"] = "1.2"
        m.manifest_entry(MIMETYPE, "/", add_md5=False)
        return m

    @staticmethod
    def parse(data):
        m = Manifest()
        m._manifest = etree.fromstring(data)
        return m

    def get_resources(self, mtype):
        result = []
        for entry in self._manifest.findall(MANIFEST+"file-entry"):
            if entry.attrib[MANIFEST+"media-type"] == mtype:
                result.append(entry.attrib[MANIFEST+"full-path"])
        return result

    def manifest_entry(self, mtype, fname, add_md5=True):
        entry = etree.SubElement(self._manifest, MANIFEST+"file-entry")
        entry.attrib[MANIFEST+"media-type"] = mtype
        entry.attrib[MANIFEST+"full-path"] = fname
        if add_md5:
            entry.attrib[MANIFEST+"md5sum"] = md5(fname)
        return entry

    def add_resource(self, mtype, resource):
        self.manifest_entry(mtype, resource)

    def to_xml(self):
        return self._manifest
    
    def to_string(self):
        return etree.tostring(self._manifest, xml_declaration=True, pretty_print=True, encoding="UTF-8")


class Bundle(object):
    def __init__(self):
        self.brushes = []
        self.presets = []
        self.patterns = []
        self.presets_data = None
        self.meta = None

    @staticmethod
    def get_presets(zipname):
        zf = ZipFile(zipname, 'r')
        m = zf.read('META-INF/manifest.xml')
        manifest = Manifest.parse(m)

        result = []
        for preset in manifest.get_resources('paintoppresets'):
            data = zf.read(preset)
            kpp = KPP(preset, data)
            result.append(kpp)
            
        zf.close()
        return result

    @staticmethod
    def open(zipname):
        zf = ZipFile(zipname, 'r')
        m = zf.read('META-INF/manifest.xml')
        manifest = Manifest.parse(m)

        def warn(resource):
            print(u"Warning: bundle {} does not contain resource {}, which is referred in its manifest.".format(zipname, resource).encode('utf-8'))

        result = Bundle()
        result.presets_data = []
        for preset in manifest.get_resources('paintoppresets'):
            if preset in zf.namelist():
                result.presets.append(preset)
                data = zf.read(preset)
                kpp = KPP(preset, data)
                result.presets_data.append(kpp)
            else:
                warn(preset)

        for brush in manifest.get_resources('brushes'):
            if brush in zf.namelist():
                result.brushes.append(brush)
            else:
                warn(brush)
        for pattern in manifest.get_resources('patterns'):
            if pattern in zf.namelist():
                result.patterns.append(pattern)
            else:
                warn(pattern)
            
        zf.close()
        return result

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
            #print("Checking {}".format(brush))
            if basename(brush) == basename(name):
                #print("Found")
                return True
        return False

    def unpack_from_bundle(self, bundle, target_directory, resource):
        zf = ZipFile(bundle, 'r')
        #print(zf.namelist())
        path = join(target_directory, resource)
        if path not in zf.namelist():
            return False
        print("Extracting {} from bundle {}".format(resource, bundle))
        zf.extract(path)
        zf.close()
        return True

    def auto_add(self, mtype, target_directory, sources, resource):
        if not isdir(target_directory):
            os.makedirs(target_directory)

        target_path = join(target_directory, resource)

        found = False
        for src in sources:
            if isfile(src) and src.endswith(".bundle"):
                found = self.unpack_from_bundle(src, target_directory, resource)
            elif isdir(src):
                path = join(src, basename(resource))
                if not isfile(path):
                    continue
                shutil.copy(path, target_path)
                found = True
            else:
                print("Error: {} is not a directory and is not a bundle file")
                continue
            if found:
                if mtype == 'brushes':
                    self.brushes.append(target_path)
                break
        return found

    def check(self, skip_bad=False, skip_unused_brushes=False, resourcedir=None):
        result = True
        presets = []
        used_brushes = set()
        for fname in self.presets:
            add = True
            #print("Checking {}".format(fname))
            kpp = KPP(fname)
            links = kpp.get_links()
            requiredBrushFile = links.get('requiredBrushFile', None)
            #print("Required brush file: {}".format(requiredBrushFile))
            if requiredBrushFile:
                ok = self.find_brush(requiredBrushFile)
                if not ok:
                    warning = "Warning: required brush file {} not found for preset {}".format(requiredBrushFile, fname)
                    if resourcedir is None:
                        print(warning)
                        if skip_bad:
                            add = False

                        result = False
                    else:
                        added = self.auto_add('brushes', self.brushdir, resourcedir, requiredBrushFile)
                        if added:
                            print("Adding missing brush file {} for preset {}".format(requiredBrushFile, fname))
                        else:
                            print(warning)
                        result = result and added
                        if skip_bad:
                            add = added
                used_brushes.add(requiredBrushFile)
            if add:
                presets.append(fname)
            else:
                print("Warning: skip preset {} since it has references to missing brush files.".format(fname))

        self.presets[:] = presets

        if skip_unused_brushes:
            brushes = []
            for brush in self.brushes:
                if basename(brush) not in used_brushes:
                    try:
                        print(u"Warning: skip brush {} since it is not used by any preset.".format(brush.decode('utf-8')).encode('utf-8'))
                    except Exception as e:
                        print(e)
                else:
                    brushes.append(brush)
            self.brushes[:] = brushes

        return result

    def format_manifest(self):
        manifest = Manifest.new()

        for fname in self.brushes:
            manifest.add_resource('brushes', fname)
        for fname in self.patterns:
            manifest.add_resource('patterns', fname)
        for fname in self.presets:
            manifest.add_resource('paintoppresets', fname)

        return manifest.to_string()

    def prepare(self, brushdir, brushmask, presetsdir, presetmask, patdir, patmask):
        self.brushdir = brushdir
        self.read_brushes(brushdir, brushmask)
        self.read_presets(presetsdir, presetmask)
        self.patdir = patdir
        self.read_patterns(patdir, patmask)

    def create(self, zipname, meta, preview):
        manifest = self.format_manifest()

        zf = ZipFile(zipname, 'w', ZIP_STORED)
        zf.writestr("mimetype", MIMETYPE)
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

