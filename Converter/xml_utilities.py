#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xml.etree.ElementTree as ET
import json
import os
import re

def get_XML_root(file):
    ''' Gets the root of an XML file

        Arguments:
            file: the XML file to open
        Returns:
            ElementTree
    '''
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        return root
    except RuntimeError:
        print ("There was an error opening the source file")

def init_new_XML_tree():
    ''' Create a new DOM tree for the updated text

        Returns:
            ElementTree
    '''
    root = ET.Element("work")
    body = ET.SubElement(root, "body")
    ET.SubElement(body, "text")
    tree = ET.ElementTree(root)
    return tree

def clean_file(f):
    ''' Remove all of the garbage from the input file.

        Arguments:
            f: the file to clean
        Returns:
            String: cleaned file output name
    '''
    data = f.read()

    exp = "&\w+.\w+;"
    regex = re.compile(exp)
    matches = regex.findall(data)

    removedItems = ""
    for match in matches:
        removedItems += match + "\n"

    cleanData = re.sub(exp, " ", data)

    cleanFileName = "output/linted_" + os.path.basename(f.name)

    print removedItems

    f.close()

    with open(cleanFileName, 'w') as cleanFile:
        cleanFile.write(cleanData)

    return cleanFileName