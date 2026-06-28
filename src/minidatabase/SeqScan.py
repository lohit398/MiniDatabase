from minidatabase.Operator import Operator
import csv

class SeqScan(Operator):
    def __init__(self,path):
        self.cols = []
        self.pos = 0
        self.path = path
        self.file = None # CSV File for data
        self.reader = None
        

    def getColNames(self,header:list):
        cols = []
        for col in header:
            cols.append(col)
        return cols

    def open(self):
        self.file = open(self.path,newline="")
        reader = csv.reader(self.file)
        self.cols = self.getColNames(next(reader)) # define cols
        self.reader =  reader

    
    def next(self):
        row = next(self.reader,None)
        if row == None:
            return None
        r = {}
        for index,col in enumerate(self.cols):
            if row[index] == "":
                r[col] = None
            else:
                r[col] = row[index]
        return r
        

    
    def close(self):
        if(self.file != None):
            self.file.close()
        return





