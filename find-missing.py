#!/usr/bin/env python
# -*- encoding: utf-8 -*- 

import os
import sys
import argparse
import shutil
from glob import glob
from os.path import join, basename, exists

from extractor import KPP
from bundle import Bundle

def parse_cmdline():
    parser = argparse.ArgumentParser(description="Find resources that are used by the bundle, but not included into it")
    parser.add_argument('-b', '--brushes', nargs=1, metavar='DIRECTORY', help='Directory with brush files')
    parser.add_argument('--embed', action='store_true', help='Automatically embed found resources to the bundle')
    parser.add_argument('bundle', metavar='FILE.BUNDLE', help="Path to bundle file to inspect")
    return parser.parse_args()

def find_used(bundle_path):

    def process_kpp(kpp):
        links = kpp.get_links()
        requiredBrushFile = links.get('requiredBrushFile', None)
        if requiredBrushFile:
            return [requiredBrushFile]
        else:
            return []

    bundle = Bundle.open(bundle_path)
    presets = bundle.presets_data
    used = []
    for kpp in presets:
        used.extend(process_kpp(kpp))
    result = [brush for brush in used if not bundle.find_brush(brush)]
    return set(result)

def find_brush(paths, name):
    for path in paths:
        b = join(path, name)
        if exists(b):
            return b
    return None

if __name__ == '__main__':

    args = parse_cmdline()
    if not args.bundle:
        print("Error: path to bundle must be specified")
        sys.exit(1)

    used = find_used(args.bundle)
    for brush in used:
        print(brush)

    if args.embed and len(used):
        if not args.brushes:
            print("Error: if --embed mode is on, --brushes must be specified")
            sys.exit(1)

        bundle = Bundle.open(args.bundle)
        shutil.copy(args.bundle, args.bundle+'.bak')
        
        found = []
        for brush in used:
            path = find_brush(args.brushes, brush)
            if path:
                found.append(path)
                print("Added " + brush)
            else:
                print("Warning: can't find "+brush)

        bundle.add_brushes(args.bundle, found)


