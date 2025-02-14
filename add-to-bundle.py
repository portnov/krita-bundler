#!/usr/bin/python3
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
    parser = argparse.ArgumentParser(description="Add resource (preset, brush tip or pattern) to the bundle.")
    parser.add_argument('bundle', metavar='FILE.BUNDLE', help="Path to bundle file to operate on")
    #subparsers = parser.add_subparsers(help="type of resource to be added")
    parser.add_argument('type', metavar='TYPE', help="Type of resource to be added: preset, brush or pattern.")
    parser.add_argument('path', metavar='FILENAME', nargs=argparse.REMAINDER, help="File to be added to the bundle")

    return parser.parse_args()

if __name__ == '__main__':

    args = parse_cmdline()
    #print(args)
    bundle = Bundle.open(args.bundle)
    shutil.copy(args.bundle, args.bundle+'.bak')

    if args.type == 'brush':
        bundle.add_brushes(args.bundle, args.path)
    elif args.type == 'preset':
        bundle.add_presets(args.bundle, args.path)
    elif args.type == 'pattern':
        bundle.add_patterns(args.bundle, args.path)
    else:
        print("Unknown resource type specified. Valid resource types are: brush, preset, pattern.")
        sys.exit(1)

