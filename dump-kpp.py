#!/usr/bin/python3
# -*- coding: utf-8 -*- 

import sys
from lxml import etree
from extractor import KPP

if len(sys.argv) == 2:
    filename = sys.argv[1]
    kpp = KPP(filename)
    xml = kpp.check()
    if xml is None:
        text = kpp.get_preset_text()
    else:
        text = etree.tostring(xml, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(text)
else:
    print("Usage: dump-kpp filename.kpp")
