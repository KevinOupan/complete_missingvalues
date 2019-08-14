import pandas as pd
import matrix_completion as mc
import numpy as np
import xlrd


class Com:
    def __init__(self, addr_in):
        """从csv文件中读取数据
        addr_in为缺失的csv文件地址
        addr_out为补全后的数据输出地址"""
        self.addr_in = addr_in
        datafile = xlrd.open_workbook(self.addr_in)
        table = datafile.sheets()[0]
        self.matrix_text = pd.DataFrame([])
        for i in range(table.ncols):
            self.matrix_text[i] = table.col_values(i)
        self.matrix_text.rename(columns=self.matrix_text.iloc[0, :], inplace=True)
        self.matrix_text.drop([0], axis=0, inplace=True)
        self.matrix_text = self.matrix_text[['产品类型', '双面器', '最大复印尺寸', '网络打印卡', '质保时间']]
        self.m, self.n = self.matrix_text.shape
        self.name_col = self.matrix_text.columns

    def map1(self):
        """将文本数据（类别数据）映射为数值数据
        matrix_text:表示需要映射的文本矩阵
        matrix_num：为输出数据（数值矩阵）
        """
        self.matrix_num = pd.DataFrame([])
        for j in range(self.n):
            data_col = self.matrix_text.iloc[:, j].copy()
            data_col.dropna(inplace=True)
            set_text = list(set(data_col))
            for i in range(self.m):
                if self.matrix_text.iloc[i, j] == '' or self.matrix_text.iloc[i, j] == 'nan' \
                        or self.matrix_text.iloc[i, j] == '图片识别':
                    self.matrix_num.loc[i, j] = 999
                else:
                    self.matrix_num.loc[i, j] = set_text.index(self.matrix_text.iloc[i, j])

    def index(self):
        """读取出空缺值的横坐标和纵坐标"""
        self.index_x = []
        self.index_y = []
        for j in range(self.n):
            for i in range(self.m):
                if self.matrix_num.iloc[i, j] == 999:
                    self.index_x.append(i)
                    self.index_y.append(j)

    def matrix_compl(self):
        """完成数据补全过程
        调用mc模块中的MF方法
        """
        matrix_tra = np.array(self.matrix_num, dtype=np.float)
        matrix_tra[matrix_tra == 999] = np.nan
        mf = mc.MF(matrix_tra, k=5, alpha=0.005, beta=0.0035, iterations=500)
        mf.train()
        self.matrix_fore = pd.DataFrame(mf.full_matrix())

    def fore_int(self):
        """将填补缺失值的小数转化为能够识别的整数形式
        matrix_na：存在缺失的数值矩阵
        matrix_fore：填补缺失值（预测的缺失值为小数）后的数值矩阵
        index_x：缺失值的x坐标
        index_y：缺失值的y坐标
        matrix_int.astype('int'):为输出数据，填补缺失后的矩阵（整型数据）
        """
        self.matrix_int = self.matrix_num.astype('int')
        for k in range(len(self.index_x)):
            num = list(set(self.matrix_int.iloc[:, self.index_y[k]]))
            num.remove(999)
            for i in range(len(num)):
                if (self.matrix_fore.iloc[self.index_x[k], self.index_y[k]] >= num[i] - 0.5) \
                        and (self.matrix_fore.iloc[self.index_x[k], self.index_y[k]] < num[i] + 0.5):
                    self.matrix_int.iloc[self.index_x[k], self.index_y[k]] = int(num[i])
                elif self.matrix_fore.iloc[self.index_x[k], self.index_y[k]] >= num[i] + 0.5:
                    self.matrix_int.iloc[self.index_x[k], self.index_y[k]] = int(num[i])
                elif self.matrix_fore.iloc[self.index_x[k], self.index_y[k]] < num[i] - 0.5:
                    self.matrix_int.iloc[self.index_x[k], self.index_y[k]] = int(num[i])

    def map2(self):
        # matrix_num, matrix_text_na
        """将数值数据反映射为文本数据
        matrix_num：表示已经填好缺失值后数值矩阵（整型数据）
        matrix_text：存在缺失值的文本矩阵
        matrix_text_fore：为输出数据（文本矩阵）
        """
        self.matrix_text_fore = pd.DataFrame([])
        for j in range(self.n):
            data_col = pd.Series(list(set(self.matrix_text.iloc[:, j])))
            data_col.dropna(inplace=True)
            set_text = list(data_col)
            for i in range(self.m):
                values = int(self.matrix_int.iloc[i, j])
                self.matrix_text_fore.loc[i, j] = set_text[values]
        # return self.matrix_text_fore

    def out_data(self):
        """将数据导出
        matrix_text：导出数据
        addr：导出地址
        """
        self.matrix_text_fore.columns = self.name_col
        # self.matrix_text_fore.to_csv(self.addr_out, sep=',', index=0, encoding='utf_8_sig', mode='a')
        # return self.matrix_text_fore

    def train_out(self):
        """调用train_out方法,做缺失值补全过程"""
        print("正在填写缺失数据。。。")
        self.map1()
        self.index()
        self.matrix_compl()
        self.fore_int()
        self.map2()
        self.out_data()
        return self.matrix_text_fore

