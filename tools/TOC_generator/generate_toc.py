import sys
import xml.etree.ElementTree as ET
import json
import os
import re

def get_parent_folder():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    paths = dir_path.split('/')
    paths.pop()
    parent_path = '/'.join(paths)
    print parent_path
    return parent_path

parent_path = get_parent_folder()
sys.path.insert(0, parent_path)

import xml_utilities as xml

def main():
    try:
        if len(sys.argv) > 1:
            filePath = sys.argv[1]

            f = open(filePath, 'r')
            fileName = os.path.basename(f.name)

            g = xml.clean_file(f)
            source = xml.get_XML_root(open(g, 'r'))

            for book in source.findall('text/body/div1'):
                print book.get('type')
                print book.get('n')

            '''

            newTextElement = newRoot.find("body").find("text")
            updateNewXMLHeader(source, newRoot)

            # Start conversion process
            iterateBooks(source, newTextElement)

            # Write the resulting XML to file
            newFileName = "output/gk_" + fileName
            newFile.write(newFileName, encoding="UTF-8", xml_declaration=True)

            f.close()

            # Reformat the XML result
            reformatXMLFile(newFileName, ["<div1", "<p"])

            print ("Output file: " + newFileName)
            '''
            print ("Conversion complete")

    except RuntimeError:
        print ("There was an error opening the source file")


if __name__ == "__main__":
    main()