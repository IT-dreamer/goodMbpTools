import argparse
from lxml import etree

def parseBlxml(codeBlxml, modelBlxml, output) -> bool:
    codeTree = etree.parse(codeBlxml)
    modelTree = etree.parse(modelBlxml)

    newRoot = etree.Element("root")

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

    for item in modelFiles:
        newRoot.append(item)
    for item in codeFiles:
        newRoot.append(item)
    for item in codeBlocks:
        newRoot.append(item)
    for item in modelBlocks:
        newRoot.append(item)
    
    newTree = etree.ElementTree(newRoot)
    newTree.write(output, encoding = "utf-8", xml_declaration=True)

    return True

def main(inputs, output):
    codeBlxml = inputs[0]
    modelBlxml = inputs[1]
    parseBlxml(codeBlxml, modelBlxml, output)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Concatanate code and model BLXML')
    parser.add_argument('-o', '--output', help='output BLXML File')
    parser.add_argument('blxmls', help='input BLXMLs', nargs='+')
    args = parser.parse_args()
    main(args.blxml, args.output)
