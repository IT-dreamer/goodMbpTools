'''
Author: AFei tjtgcyf@gmail.com
Date: 2023-09-23 14:42:56
LastEditors: AFei tjtgcyf@gmail.com
LastEditTime: 2023-09-23 15:08:39
FilePath: /goodMbpTools/extractTasksDependency/extractTasksDependency.py
Description: This tool will extract task's denpendency from main function.
            The results will be output to a json file.
Usage: extractTasksDependency.py [-h] [-o OUTPUT] blxml
Copyright (c) 2023 by AFei, All Rights Reserved. 
'''
import argparse
import json
import sys
sys.path.append(r"/home/afei/Public/GitHub/goodMbpTools/common/")
from parseBlock import Root
from parseBlock import SubSystem
from parseBlock import CallBlock
from simulinkmodel import parse as blxmlParse

def locateMainBlock(blxmlRoot: Root):
    for item in blxmlRoot.children:
        if("_main" in item.blockName and type(item) == SubSystem):
            break
    return item

def extractCallBlockToDic(mainBlock) -> {}:
    blxmlBlocks = {}
    for item in mainBlock.children:
        callBlockDic = {}
        if(type(item) == CallBlock):
            callBlockDic["blockName"] = item.blockName
            callBlockDic["funcName"] = item.function
            callBlockDic["funcText"] = item.code[0].valueOf_
            number = 0
            for i in item.inputVar:
                callBlockDic["input" + str(number)] = i
                number += 1
            number = 0
            backwardBlocks = {}
            for b in item.backward:
                backwardBlocks["block" + str(number)] = b.blockName
                number += 1
            callBlockDic["DependencyBlock"] = backwardBlocks
        blxmlBlocks[item.blockName] = callBlockDic
    return blxmlBlocks

def writeDicToJson(blxmlBlocks: {}, outputJson):
    with open(outputJson, "w") as jsonFile:
        json.dump(blxmlBlocks, jsonFile, indent = 4)

def main(inputXml, outputJson):
    blxml = blxmlParse(inputXml, True)
    root = Root(blxml)
    mainBlock = locateMainBlock(root)
    blxmlBlocks = extractCallBlockToDic(mainBlock)
    writeDicToJson(blxmlBlocks, outputJson)

    print("done")
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='extract correct dependency from tasks of code')
    parser.add_argument('-o', '--output', default=" out.json ", help='output tasks dependencies json file')
    parser.add_argument('blxml', help='input code\'s BLXML', nargs=1)
    args = parser.parse_args()
    main(args.blxml[0], args.output)