'''
Author: AFei tjtgcyf@gmail.com
Date: 2023-09-21 15:08:26
LastEditors: AFei tjtgcyf@gmail.com
LastEditTime: 2023-09-21 16:10:22
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




    
        