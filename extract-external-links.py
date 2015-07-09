#!/usr/bin/env python
# -*- encoding: utf-8 -*- 

import sys
from zipfile import ZipFile

from extractor import KPP
from bundle import Bundle

def process(filename):
    def process_kpp(kpp, bundle=None):
        links = kpp.get_links()
        for name, value in links.iteritems():
            if bundle is not None:
                if name == 'requiredBrushFile':
                    ok = bundle.find_brush(value)
                    if ok:
                        continue
            print(u"{}: {}".format(name, value).encode('utf-8'))

    if filename.endswith(".bundle"):
        bundle = Bundle.open(filename)
        presets = bundle.presets_data
    else:
        bundle = None
        presets = [KPP(filename)]

    for preset in presets:
        process_kpp(preset, bundle)


for fname in sys.argv[1:]:
    print(u"Processing: {}".format(fname))
    process(fname)

