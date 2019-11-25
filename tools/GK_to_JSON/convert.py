#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module for converting Latin to Greek Polytonic characters.

Author: Eric Schmidt
Version: 2019-11-24
"""

import sys
import xml.etree.ElementTree as ET
import json
import os
import re

# Python XML: https://docs.python.org/2/library/xml.etree.elementtree.html

character_hash = {}

def convert_character(c):
    """Convert a character using the JSON key.
    """
    return character_hash[c]

def open_xml_source(file):
    """Opens an XML file and return the root element.
    """
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        return root
    except RuntimeError:
        print ('There was an error opening the source file')

def init_dictionary():
    """Opens JSON conversion file, adds key/value pairs to character dict.
    """
    with open('latin_greek_text_conversion.json') as json_data:

        d = json.load(json_data)

        for k, v in d.items():
            character_hash.update({k:v})

def init_new_xml_file():
    """Create a new DOM tree for the updated text.

    Returns:
        ElementTree
    """
    root = ET.Element("work")
    body = ET.SubElement(root, "body")
    ET.SubElement(body, "text")
    tree = ET.ElementTree(root)
    return tree

def update_new_xml_header(source, new_file):
    """Transfers the metadata from the old file to the new one.
    """
    source_header = source.find("header")
    new_file.insert(0, source_header)

def update_new_xml_file(element, new_element, value):
    """Updates a XML tree with a new entry.
    """
    el = ET.SubElement(element, new_element)
    if value != None:
        el.text = value

    return el

def iterate_books(source, new_text):
    """Iterate over each book in the source.
    """
    books = source[1][0].iter("div1")

    for book in books:

        # Create a new div element in the new_text.
        new_div = update_new_xml_file(new_text, "div1", None)
        new_div.attrib["n"] = book.attrib["n"]

        # Convert the book and add a new div to the
        # output XML.
        convert_book(book, new_div)

def convert_book(div, new_div):
    """Translate the line in one book to Greek Polytonic.
    """
    lines = div.findall("p")
    counter = 0

    for line in lines:
        if line != None:

            words = line.text
            if words != None:
                para = iterate_words(words.split())

                new_para_el = update_new_xml_file(new_div, "p", para)
                counter +=1

    new_div.attrib["lines"] = str(counter)

def iterate_words(words):
    """Iterate over each word in an array of words, converting to Greek.

    Source content must be in Latin characters.
    """
    para = ""

    for word in words:
        rewritten_word = convert_word(word)
        para += rewritten_word + " "

    return para

def convert_word(word):
    """Convert a word from Latin chars to Greek polytonic characters.
    """
    converted_word = ""
    hold_vowel_char = ""
    hold_capital = ""

    for i in range(len(word)):
        c = word[i]

        # Convert the character if it's known.
        if c in character_hash:

            # Resolving a capital letter.
            if hold_capital != "":
                hold_capital += c
                converted_word += resolve(hold_vowel_char)
                converted_word += resolve(hold_capital)

            else:
                converted_word += resolve(hold_vowel_char)
                converted_word += resolve(hold_capital)
                converted_word += convert_character(c)

            hold_capital = ""
            hold_vowel_char = ""

        # The character is the beginning of a capital letter.
        elif c == '*':
            # Build the hold_capital value
            hold_capital += "*"

        # The character is a diacritical mark.
        elif is_diacritical(c):
            # Build the hold_vowel_char value
            if hold_capital != "":
                hold_capital += c

            elif hold_vowel_char != "":
                hold_vowel_char += c;

            # Started a new vowel with diacriticals.
            # Adjust the hold_vowel_char to get the previous
            # alpha numeric and adjust the converted word.
            else:
                hold_vowel_char += word[i - 1] + c
                converted_word = converted_word[0:(len(converted_word) - 1)]

        # Don't know what to do with this
        # character; convert as-is and output to the terminal.
        else:
            converted_word += c
            print (c)

    converted_word += resolve(hold_vowel_char)
    converted_word += resolve(hold_capital)

    if converted_word.find(u"σ") > -1:
        converted_word = convert_final_sigma(converted_word)

    return converted_word

def is_diacritical(character):
    """Determine whether the current character is a diacritical.

    Includes rough breathing mark, accent, iota subscript, umlaut/dieresis.
    """
    return ")(\\/=|+".find(character) > -1

def resolve(s):
    """Resolves a hold capital or hold vowel.
    """

    new_char = ""

    if (s != "") and (s in character_hash):
        new_char = convert_character(s)
    elif (s != ""):
        new_char = s

    if new_char == None:
        return ""

    return new_char

def convert_final_sigma(converted_word):
    """Replace any final sigma characters with the correct version.
    """
    trimmed_word = converted_word.replace(" ", "")
    trimmed_word_len = len(trimmed_word)
    last_char = trimmed_word[trimmed_word_len - 1]
    second_to_last = trimmed_word[trimmed_word_len - 2]
    cleaned_word = converted_word

    if last_char == u"σ":
        cleaned_word = trimmed_word[:trimmed_word_len - 1] + u"ς"

    elif (second_to_last == u"σ") and (".:;,".find(last_char) > -1):
        cleaned_word = trimmed_word[:trimmed_word_len - 2] + u"ς" +last_char

    return cleaned_word

def clean_file(f):
    """Remove all of the garbage <milestone> tags from the input file.
    """
    data = f.read()

    exp = "<milestone\W\S+\W\S+\W\S+/>"
    regex = re.compile(exp)
    matches = regex.findall(data)

    removed_items = ""
    for match in matches:
        removed_items += match + "\n"

    clean_data = re.sub(exp, "", data)

    clean_file_name = "output/linted_" + os.path.basename(f.name)
    removed_file_name = "output/removed_" + os.path.basename(f.name)

    f.close()

    with open(clean_file_name, 'w') as clean_file:
        clean_file.write(clean_data)

    # Save all of the removed tags to a file to ensure
    # that no necessary data was deleted.
    with open(removed_file_name, 'w') as removed:
        removed.write(removed_items)

    return clean_file_name

def reformat_xml_file(f_name, strings_to_replace):
    """Reformats an XML file.
    """

    file_to_format = open(f_name, 'r')
    file_text = file_to_format.read()
    file_to_format.close()

    for s in strings_to_replace:
        file_text = file_text.replace(s, "\n" + s)

    with open(f_name, 'w') as formatted_file:
        formatted_file.write(file_text)

def main():
    """Entry point for the command-line version of the module.
    """
    try:
        if len(sys.argv) > 1:
            file_path = sys.argv[1]

            f = open(file_path, 'r')
            file_name = os.path.basename(f.name)
            g = clean_file(f)

            source = open_xml_source(open(g, 'r'))

            # Populate the dictionary with entries from JSON
            init_dictionary()

            # Create new XML file
            new_file = init_new_xml_file()
            new_root = new_file.getroot()
            new_text_element = new_root.find("body").find("text")
            update_new_xml_header(source, new_root)

            # Start conversion process
            iterate_books(source, new_text_element)

            # Write the resulting XML to file
            new_file_name = "output/gk_" + file_name
            new_file.write(new_file_name, encoding="UTF-8", xml_declaration=True)

            f.close()

            # Reformat the XML result
            reformat_xml_file(new_file_name, ["<div1", "<p"])

            print ("Output file: " + new_file_name)
            print ("Conversion complete")

    except RuntimeError:
        print ("There was an error opening the source file")

if __name__ == "__main__":
    main()