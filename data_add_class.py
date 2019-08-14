import xlrd
import pandas as pd
import numpy as np
from functions import *


class Data_add():
    def __init__(self,table_path):
        '''
        依次输入表格路径，输出路径，productcode，品牌，价格，型号，系列对应的列号,以及一个原始数据或者不需要预测数据的列号。
        '''
        self._table = data_load(table_path).reset_index(drop=True)
        lyst = list(self._table.columns)   
        for i in range(len(lyst)):
            if lyst[i] == 'productname':
                self._data_col = i
            if lyst[i] == 'productcode':
                self._pcode_col = i
            if lyst[i] == 'brandname':
                self._brand_col = i
            if lyst[i] == 'price':
                self._price_col = i
            if lyst[i] == '产品型号':
                self._type_col = i
            if lyst[i] == '产品系列':
                self._ser_col = i
        try:
            lyst_test = [self._data_col,self._pcode_col,self._brand_col,self._price_col,self._type_col,self._ser_col]
        except AttributeError:
            print('没有找到指定的列，请修改data_add_class中的代码或者检查excel表格。')
        #print(self._data_col,self._pcode_col,self._brand_col,self._price_col,self._type_col,self._ser_col)
            
    
    def data_add_main(self):
        some_lyst=[self._data_col,self._pcode_col,self._price_col,self._brand_col,self._type_col]
        n = self._table.shape[1]   #列
        lyst=[]
        for i in range(n):
            if in_or_out(some_lyst,i):
                lyst.append(i)
                continue
            else:
                lyst_null=moudle11(self._table,i,self._pcode_col)
                for j in range(len(lyst_null)):
                    try:
                        table=data_add(self._table,lyst_null[j],i,self._pcode_col,self._brand_col,self._price_col,self._type_col,self._ser_col)
                    except AttributeError:
                        return 0
        loading()
        data = pre(table)
        return data
