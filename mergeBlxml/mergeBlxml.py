'''
Author: AFei tjtgcyf@gmail.com
Date: 2023-09-20 14:23:53
LastEditors: AFei tjtgcyf@gmail.com
LastEditTime: 2023-09-23 15:02:02
FilePath: /goodMbpTools/mergeBlxml/mergeBlxml.py
Description: This tool can merge code's blxml and model's blxml.
Useage: Python3 mergeBlxml.py [-h] [-o OUTPUT] blxmls [blxmls ...]
Copyright (c) 2023 by AFei, All Rights Reserved. 
'''
import argparse
from lxml import etree

def parseBlxml(codeBlxml, modelBlxml, output) -> bool:
    codeTree = etree.parse(codeBlxml)
    modelTree = etree.parse(modelBlxml)
    modelRoot = modelTree.getroot()

    if not "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation" in modelRoot.attrib:
        return parseBlxml(modelBlxml, codeBlxml, output)
    
    modelName = modelRoot.attrib["name"]

    codeFiles = []
    codeBlocks = []
    
    for element in codeTree.xpath('//file[not(ancestor::file)]'):
        codeFiles.append(element)

    for element in codeTree.xpath('//block[not(ancestor::block)]'):
        codeBlocks.append(element)
    
    modelFiles = []
    modelBlocks = []
    
    for element in modelTree.xpath('//file[not(ancestor::file)]'):
        modelFiles.append(element)

    for element in modelTree.xpath('//block[not(ancestor::block)]'):
        modelBlocks.append(element)

    nameSpaceMap = {
        'sm': 'http://example.com/SimulinkModel',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'        
    }
    newRoot = etree.Element('{%s}blocks' % nameSpaceMap['sm'], nsmap=nameSpaceMap)
    newRoot.set('name', modelName)
    newRoot.set('{%s}schemaLocation' % nameSpaceMap['xsi'], 'http://example.com/SimulinkModel SimulinkModel.xsd')

    for item in modelFiles:
        newRoot.append(item)
    for item in codeFiles:
        newRoot.append(item)
    for item in codeBlocks:
        newRoot.append(item)
    for item in modelBlocks:
        newRoot.append(item)
    
    newTree = etree.ElementTree(newRoot)
    newTree.write(output, encoding = "utf-8", pretty_print=True, xml_declaration=True)

    return True

def main(inputs, output="out.xml"):
    codeBlxml = inputs[0]
    modelBlxml = inputs[1]
    parseBlxml(codeBlxml, modelBlxml, output)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='merge code and model BLXML')
    parser.add_argument('-o', '--output', default=" out.xml ", help='output BLXML File')
    parser.add_argument('blxmls', help='input BLXMLs', nargs='+')
    args = parser.parse_args()
    main(args.blxmls, args.output)
