'''
Author: AFei tjtgcyf@gmail.com
Date: 2023-09-21 15:08:26
LastEditors: AFei tjtgcyf@gmail.com
LastEditTime: 2023-09-29 11:02:18
FilePath: /goodMbpTools/common/adjacencyList.py
Description: 

Copyright (c) 2023 by AFei, All Rights Reserved. 
'''
from parseBlock import codeBlock

class Vertex(codeBlock):
    def __init__(self, block: codeBlock = None):
        if block is None:
            self.name = ""
            self.inDegree = 0
            self.outDegree = 0
            self.inVertices = []
            self.outVertices = []
            self.number = 0
        
        else:
            self.name = block.blockName
            self.inDegree = len(block.input)
            self.outDegree = len(block.output)
            self.inVertices = []
            self.outVertices = []
            self.number = 0
            for i in block.input:
                for c in i.connect:
                    self.inVertices.append(c.block)
            for o in block.output:
                for c in o.connect:
                    self.outVertices.append(c.block)

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
        self.vertList = {}
    
    def addVertex(self, vertex: Vertex):
        innerList = []
        for item in vertex.outVertices:
            innerList.append(item)
        self.list[vertex.name] = innerList
        self.vertList[vertex.name] = vertex

    def print(self):
        #keys = list(self.list.keys())
        for key, value in self.list.items():
            print(" [%s]" %key, end = '')
            for v in value:
                print("->%s "%v, end = '')
            print("->^")

'''
description: Use topological sorting to parse acyclic DAG and obtain a legal node calling sequence
param {AdjList} adjList
return {*}
'''
def topoloSort(adjList: AdjList):
    result = []
    temp = []

    while(len(adjList.vertList)):
        for key, value in adjList.vertList.items():
            if value.inDegree <= 0:
                temp.append(value)
        
        for v in temp:
            for value in v.outVertices:
                adjList.vertList[value].inDegree -= 1
            del adjList.vertList[v.name]
            result.append(v.name)

        temp.clear()

    for item in result:
        print(item)        
        