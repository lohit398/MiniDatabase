from minidatabase.Operator import Operator
import csv

class SeqScan(Operator):
    def __init__(self,file):
        self.cols = []
        self.pos = 0
        self.file = None # CSV File for data
        self.reader = self.open(file)
        

    def getColNames(self,header:list):
        cols = []
        for col in header:
            cols.append(col)
        return cols

    def open(self,file):
        self.file = open(file,newline="")
        reader = csv.reader(self.file)
        self.cols = self.getColNames(next(reader)) # define cols
        return reader

    
    def next(self):
        row = next(self.reader,None)
        if row == None:
            return None
        r = {}
        for index,col in enumerate(self.cols):
            if row[index] == "":
                r[col] = None
            else:
                r[col] = (row[index]).strip()
        return r
        

    
    def close(self):
        if(self.file != None):
            self.file.close()
        return





