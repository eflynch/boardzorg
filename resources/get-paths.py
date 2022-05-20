#!/usr/bin/env python

from __future__ import print_function
import sys

import xml.etree.ElementTree as ET
import os
import subprocess
import json

DIR = "./sectors"

for filename in filter(lambda x: ".png" in x, os.listdir(DIR)):
    name, ext = filename.split(".")
    if (not os.path.exists(os.path.join(DIR, name) +".svg")):
        print("svg-ing: ", name, file=sys.stderr)
        subprocess.check_output(["./make-path.sh", os.path.join(DIR, name)])

all_paths = {}

for filename in filter(lambda x: ".svg" in x, os.listdir(DIR)):
    name, ext = filename.split(".")
    print("processing: ", name, file=sys.stderr)
    tree = ET.parse(os.path.join(DIR, filename))
    root = tree.getroot()
    g = root[1]
    all_paths[name] = []
    for child in g:
        all_paths[name].append(child.attrib['d'])

print("module.exports="+json.dumps({"paths": all_paths})+";")
