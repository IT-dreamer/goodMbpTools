'''
Author: AFei tjtgcyf@gmail.com
Date: 2023-09-23 12:39:53
LastEditors: AFei tjtgcyf@gmail.com
LastEditTime: 2023-10-05 13:29:17
FilePath: /goodMbpTools/extractModelOrder/extractModelOrder.py
Description: extract a legal block calling sequence from Simulink Model's Blxml

Copyright (c) 2023 by AFei, All Rights Reserved. 
'''
import sys
import argparse
sys.path.append(r"/home/afei/Public/GitHub/goodMbpTools/common/")
import adjacencyList
import parseBlock
from simulinkmodel import parse as blxmlParse

def parseBlxml(blxml):
    adList = adjacencyList.AdjList()
    for block in blxml.block:
        tempBlock = parseBlock.SimulinkBlock(block)
        v = adjacencyList.Vertex(tempBlock)
        adList.addVertex(v)
    return adList

def writeToTxt(sortResult, output):
    with open(output, "w") as file:
        for item in sortResult:
            file.write(item + "\n")

def main(input, output):
    blxml = blxmlParse(input, True)
    adList = parseBlxml(blxml)
    result = adjacencyList.topoloSort(adList)
    writeToTxt(result, output)
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='extract a legal block calling sequence from Simulink Model\'s Blxml')
    parser.add_argument('-o', '--output', default=" out.txt ", help='output block calling sequence File')
    parser.add_argument('blxml', help='input BLXMLs', nargs=1)
    args = parser.parse_args()
    main(args.blxml[0], args.output[0])
    