/**
 * This script translates Perseus Project Classics texts from XML to
 * a lightweight JSON format.
 *
 * @author Eric M Schmidt
 * @version 1.0.0 2019-01-06
 */
const jsdom = require("jsdom"),
      fs = require('fs')
const { JSDOM } = jsdom;

function main() {
    fs.readFile('output/linted_caes.bg_lat.xml', 'utf8', (err, data) => {
         readXML(data);
    });
}

/**
 * Read an XML file as a series of nodes and translate into JSON.
 *
 * @param xml the XML file as string to read
 * @return JSON object
 */
function readXML(xml) {
    // Pass in 'text/xml' content to be able to parse individual XML nodes
    const dom = new JSDOM(xml, { contentType: 'text/xml' });
    let div1 = dom.window.document.querySelector('div1');
    let output = createJSONChapter(div1);
    console.log(output);
}

/**
 * Prints data about an XML node.
 *
 * @param n the node element to print
 */
function printNode(n) {
    if (n.nodeType === 3) {
        console.log(`Text node: ${n.nodeValue}`)
    } else if (n.nodeType === 1) {
        const unitType = n.getAttribute('unit') || "no unit",
              num = n.getAttribute('n') || "no number";
        console.log(`${n.nodeName}: ${unitType}, ${num}`);
    }
}

/**
 * Transfers '@section' text from XML p element into JSON array.
 *
 * @param p the p element to translate
 * @return JSON object
 */
function createJSONSections(p) {
    let children = p.childNodes;
    let sectionArray = [];

    children.forEach((n, i) => {
        // Node type 3 is text node
        if (n.nodeType === 3) {
            sectionArray.push(n.nodeValue);
        } // TODO: put in some sort of check that array index matches XML num?
    });
    return { 'sections': sectionArray };
}

/**
 * Transfers '@chapter' text from XML div element into JSON array.
 *
 * @param div the div element to translate
 * @return JSON object
 */
function createJSONChapter(d) {
    let result = {};
    let children = d.querySelectorAll('p');
    let chapterArray = [];

    children.forEach((p, i) => {
        chapterArray.push(createJSONSections(p));
    });

    return { 'chapters': chapterArray };
}

main();
