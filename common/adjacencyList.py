'''
Author: AFei tjtgcyf@gmail.com
Date: 2023-09-21 15:08:26
LastEditors: AFei tjtgcyf@gmail.com
LastEditTime: 2023-09-21 16:31:17
FilePath: /goodMbpTools/common/adjacencyList.py
Description: 

Copyright (c) 2023 by AFei, All Rights Reserved. 
'''
from parseBlock import Block

class Vertex(Block):
    def __init__(self, block: Block = None):
        if block is None:
            self.name = ""
            self.inDegree = 0
            self.outDegree = 0
            self.inVertices = []
            self.outVertices = []
            self.number
        
        else:
            self.name = block.blockName
            self.inDegree = block.input.__sizeof__()
            self.outDegree = block.output.__sizeof__()
            self.inVertices = block.input
            self.outVertices = block.output
            self.number

    def getName(self):
        return self.name
    
    def getInDegree(self):
        return self.inDegree

    def getOutDegree(self):
        return self.outDegree

    def getBackVertices(self):
        return self.inVertices
    
    def getForwardVertices(self):
        return self.outVertices
    
    def getNumber(self):
        return self.number

class AdjList:
    def __init__(self, name = "adjacency list") -> None:
        self.name = name
        self.count = 0
        self.list = {}
    
    def addVertex(self, vertex: Vertex):
        innerList = []
        for item in vertex.inVertices:
            innerList.append(item.blockName)
        self.list[vertex.name] = innerList

    def print(self):
        #keys = list(self.list.keys())
        for key, value in self.list.items():
            print(" [%s]" %key, end = '')
            for v in value:
                print("->%s "%v, end = '')
            print("->^")

    
        