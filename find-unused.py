#!/usr/bin/python3
# -*- encoding: utf-8 -*- 

import os
import sys
import argparse
from glob import glob
from os.path import join, basename

from extractor import KPP
from bundle import Bundle

def find_used(filenames):

    def process_kpp(kpp):
        links = kpp.get_links()
        requiredBrushFile = links.get('requiredBrushFile', None)
        if requiredBrushFile:
            return [requiredBrushFile]
        else:
            return []

    def process(filename):
        if filename.endswith(".bundle"):
            bundle = Bundle.open(filename)
            presets = bundle.presets_data
        else:
            presets = [KPP(filename)]
        result = []
        for kpp in presets:
            result.extend(process_kpp(kpp))
        return result

    result = []
    for filename in filenames:
        result.extend(process(filename))
    return result

def parse_cmdline():
    parser = argparse.ArgumentParser(description="Find unused brush files")
    parser.add_argument('-b', '--brushes', nargs=1, metavar='DIRECTORY', help='Directory with brush files')
    parser.add_argument('-p', '--presets', nargs=1, metavar='DIRECTORY', help='Directory with preset files (*.kpp)', required=True)
    parser.add_argument('-B', '--bundles', nargs=1, metavar='DIRECTORY', help='Directory with bundle files (*.bundle)')
    parser.add_argument('-i', '--invert', action='store_true', help='Find used brushes instead of unused')
    parser.add_argument('--remove', action='store_true', help='Remove unused brush files')
    return parser.parse_args()

if __name__ == '__main__':

    args = parse_cmdline()
    #print(args)
    if not args.invert and not args.brushes:
        print("Error: brush files directory must be specified if -i/--invert is not used")
        sys.exit(1)

    presets = []
    for p in args.presets:
        presets.extend(glob(join(p, '*')))
    if args.bundles:
        for p in args.bundles:
            presets.extend(glob(join(p, '*')))

    used = set()
    used.update( find_used(presets) )

    if args.invert:
        for b in used:
            print(b)
    else:

        brushes = set()
        brushmap = dict()
        for p in args.brushes:
            for b in glob(join(p, '*')):
                brushes.add(basename(b))
                brushmap[basename(b)] = b
        result = brushes.difference(used)
        if args.remove:
            for b in result:
                try:
                    os.remove(brushmap[b])
                except Exception as e:
                    print("Can't remove {}: {}".format(b, e))
                else:
                    print("Removed " + brushmap[b])
        else:
            for b in result:
                print(b)

