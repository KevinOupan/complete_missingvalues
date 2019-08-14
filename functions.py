import difflib
import re
import pandas as pd
import xlrd
import time

def str_split(string):
    '''
    字符分割。
    '''
    pattern = re.compile('.{1}')
    string=str(' '.join(pattern.findall(string)))
    return string.split()

def is_alphabet(uchar):
    '''
    判断一个unicode是否是英文字母
    '''
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False


def string_similar(s1, s2):
    '''
    字符串相似度计算，此处算法有待改进，有更好的算法可以直接替代此处。
    '''
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def pcode2Line_num(table,pcode):
    '''
    productcode转行号，请根据pcode的实际列数设置col的数值。
    '''
    lyst = list(table.columns)
    for i in range(len(lyst)):
        if lyst[i] == 'productcode':
            col = i
    data_col = list(table.iloc[:, col])
    n= data_col.index(pcode)
    return n


def moudle8(table,cand_pcode,pre_pcode,col):
    '''
    此模块为字符匹配，table为原始表格，cand_pcode为候选的产品productcode，pre_pcode为空缺待预测的产品prodectcode，为单一的字符串。
    '''
    p=string_similar(table.iloc[pcode2Line_num(table,cand_pcode),col],table.iloc[pcode2Line_num(table,pre_pcode),col])
    return p


def moudle9(table,mat_pcode,pre_pcode,col):
    '''
    此模块为预测数据填写，利用产品的mat_productcode匹配数据填写入待预测数据pre_pcode的相应列col中。
    '''
    #if mat_pcode !=pre_pcode:
        #print("已经把表格中 [",pcode2Line_num(table,pre_pcode),',',col,"] 空缺的参数替换为 [",pcode2Line_num(table,mat_pcode),",",col,"] 的参数。")
    table.iloc[pcode2Line_num(table,pre_pcode),col]=table.iloc[pcode2Line_num(table,mat_pcode),col]
    return table


def moudle10(table,pre_pcode,brand_col,pcode_col,ser_col=15,type_col=9):
    '''
    ser_col为系列号，type_col为型号。函数将型号按照规律赋给系列号。
    '''
    brand = str(table.iloc[pcode2Line_num(table,pre_pcode),brand_col])
    brand_lyst = list(table.iloc[:,brand_col])
    same_brand_pcode_lyst = []
    lyst = []

    for i in range(len(brand_lyst)):
        if brand_lyst[i] == brand:
            same_brand_pcode_lyst.append(table.iloc[i,pcode_col])
            lyst.append(i)
    str2pre=str_split(str(table.iloc[pcode2Line_num(table,pre_pcode),type_col]))
    str2out=[]
    if is_alphabet(str2pre[0])==False:
        if len(str2pre)<3:
            for i in range(len(str2pre)):
                str2out.append(str2pre[i])
        else:
            for i in range(3):
                str2out.append(str2pre[i])
    else:       
        for i in range(len(str2pre)):
            if is_alphabet(str2pre[i]):
                str2out.append(str2pre[i])
            else: break
    str2out=''.join(str2out)
    for i in range(len(same_brand_pcode_lyst)):
        table.iloc[pcode2Line_num(table,same_brand_pcode_lyst[i]),ser_col]=str2out
    return table


def moudle7(table,productcode,col):
    '''
    提取相应productcode的对应列数据。
    '''
    return table.iloc[col,pcode2Line_num(table,productcode)]



def moudle6(old_table,table,pre_pcode,type_col,pcode_col):
    '''
    old_code是原始表格，table是筛选后表格，pre_pcode是数据缺失值的pcode，type_col是型号的列号，输出为匹配度最高的pcode。
    '''
    pcode_col_data = list(table.iloc[:, pcode_col])
    p_max=moudle8(old_table,pcode_col_data[0],pre_pcode,type_col)
    pcode_max=pcode_col_data[0]
    for i in range(1,len(pcode_col_data)):
        p=moudle8(old_table,pcode_col_data[i],pre_pcode,type_col)
        if p>p_max:
            pcode_max=pcode_col_data[i]
            p_max=p
    return pcode_max


def moudle5(old_table,table,p_range,pre_pcode,price_col):
    '''
    table为待筛选表格，range为0-1之间的浮动范围，pre_pcode为待填写的号，price_col为价格的列号。返回去除了不在区间内产品的表格。
    '''
    price_col_data = list(table.iloc[:, price_col])           #选取的价格列表
    price_col_data = list(map(lambda x:float(x), price_col_data))          #字符串转化为浮点型
    price_line=int(old_table.iloc[pcode2Line_num(old_table,pre_pcode),price_col])
    n=[]
    for i in range(len(price_col_data)):
        if price_col_data[i] > price_line*(1+p_range) or price_col_data[i] < price_line*(1-p_range):
            n.append(i)

    if len(n) == len(price_col_data):
        D_value_min = abs(price_col_data[0]-price_line)
        min_num=0
        for j in range(len(price_col_data)):
            D_value = abs(price_col_data[j]-price_line)
            if D_value < D_value_min:
                min_num = j
                D_value_min = D_value
        n.pop(min_num)
    
    new_table=table.drop(n)
    return new_table

def moudle5_old(old_table,table,p_range,pre_pcode,price_col):
    '''
    table为待筛选表格，range为0-1之间的浮动范围，pre_pcode为待填写的号，price_col为价格的列号。返回去除了不在区间内产品的表格。
    '''
    price_col_data = list(table.iloc[:, price_col])
    price_col_data = list(map(lambda x:float(x), price_col_data))          #字符串转化为浮点型
    price_line=int(old_table.iloc[pcode2Line_num(old_table,pre_pcode),price_col])
    n=[]
    for i in range(len(price_col_data)):
        if price_col_data[i] > price_line*(1+p_range) or price_col_data[i] < price_line*(1-p_range):
            n.append(i)
    new_table=table.drop(n)
    return new_table



def moudle4(table,row,col):
    '''
    数据是否为空判断。
    '''
    data=table.iloc[row,col]    #把row行col列的数据提取出来。如果为空或无，则输出‘1’。
    if data=='NULL' or data=='nan' or data=='NAN' or data=='null' or data=='NA' or data=='':
        return True
    else: return False


def moudle3(old_table,table,pre_pcode,price_col,p_range=0.5):
    '''
    通过表格和待预测数据pcode与价格列号，通过递归实现寻找一定行数的价格近似产品价格区间。
    '''
    if p_range == 0:
        print("匹配数据太多！返回range=1")
        return p_range
    if p_range == 2:
        print("匹配数据太少！range=2时也没有匹配数据！")
        return p_range
    price_line=int(old_table.iloc[pcode2Line_num(old_table,pre_pcode),price_col])
    price_col_data = list(table.iloc[:, price_col])####???
    price_col_data = list(map(lambda x:float(x), price_col_data))
    m=0
    n=len(price_col_data)
    for j in range(len(price_col_data)):
         if price_col_data[j] <= price_line*(1+p_range) and price_col_data[j] >= price_line*(1-p_range):
            m+=1
    if m > 10 or m == n:
         p_range-=0.05
         moudle3(old_table,table,pre_pcode,price_col,p_range)
    if m < n//3 or m == 0:
         p_range+=0.05
         moudle3(old_table,table,pre_pcode,price_col,p_range)
    return p_range


def moudle2(old_table,table,pre_pcode,brand_col):
    '''
    oldtable为原始表格，table是筛选后表格，pre_pcode为待填写数据pcode，brand_col为品牌的列号。
    '''
    n=pcode2Line_num(old_table,pre_pcode)
    pre_pcode_brand=old_table.iloc[n,brand_col]
    brand_lyst=list(table.iloc[:, brand_col])
    lyst=[]
    for i in range ( len(brand_lyst)):
        if brand_lyst[i] != pre_pcode_brand:
            lyst.append(i)
    if len(lyst)==0:
        print("表格中没有该品牌产品！返回原表格。")
        return table
    new_table=table.drop(lyst)
    return new_table


def moudle1(table,col):
    '''
    输入表格和列号，返回列中元素不为无或null的table。
    '''
    all_lyst=list(table.iloc[:, col])
    lyst=[]
    for i in range(len(all_lyst)):
        if all_lyst[i] == 'NULL' or all_lyst[i] == 'nan' or all_lyst[i] == 'NAN' or all_lyst[i] == 'null' \
                or all_lyst[i] == 'NA' or all_lyst[i] == '' or all_lyst[i] == '图片识别':
            lyst.append(i)
    new_table=table.drop(lyst)
    return new_table


def moudle11(table,col,pcode_col):
    '''
    返回指定col列为空或者null的pcode。
    '''
    all_lyst=list(table.iloc[:, col])
    pcode_lyst=list(table.iloc[:, pcode_col])
    lyst=[]
    for i in range(len(all_lyst)):
        if all_lyst[i] == 'NULL' or all_lyst[i] == 'nan' or all_lyst[i]=='NAN' or all_lyst[i]=='null' or all_lyst[i]=='NA' or all_lyst[i]=='':
            lyst.append(pcode_lyst[i])
    return lyst

def loading():
    # print('正在填写非类别型数据。。。')
    time.sleep(15)

def data_load(path):
    data = xlrd.open_workbook(path)
    table = data.sheets()[0]
    ncols = table.ncols
    data2 = pd.DataFrame([])
    for i in range(ncols):
        data2[i] = table.col_values(i)
    data2.rename(columns=data2.iloc[0, :], inplace=True)
    data2.drop([0], axis=0, inplace=True)
    return data2


def in_or_out(lyst,n):
    for i in range(len(lyst)):
        if n == lyst[i]:
            return True
    else: return False


def pre(matrix_text):
    """将数据导出
    matrix_text：导出数据
    addr：导出地址
    """
    # matrix_text.to_csv(addr, sep=',', index=0, encoding='utf_8_sig', columns=matrix_text.columns)
    return matrix_text

def xlsx_to_csv_pd(csv_path,xlsx_path):
    data_xls = pd.read_excel(csv_path, index_col=0)
    data_xls.to_csv(xlsx_path, encoding='utf-8')


def moudle12(old_table,pre_pcode,price_col,pcode_col,brand_col):
    '''
    在整个品牌都缺失某项参数，将价格最相近的产品的参数赋予这个空值。
    '''
    price_col_data = list(old_table.iloc[:, price_col])
    price_col_data = list(map(lambda x:float(x), price_col_data))          #字符串转化为浮点型
    brand_col_data = list(old_table.iloc[:, brand_col])

    pcode_col_data = list(old_table.iloc[:, pcode_col])

    price_line=int(old_table.iloc[pcode2Line_num(old_table,pre_pcode),price_col])
    max_row=0
    min_sub=abs(price_col_data[max_row]-price_line)

    for i in range(1,len(price_col_data)):
        if  brand_col_data[i] != old_table.iloc[pcode2Line_num(old_table,pre_pcode),brand_col]:
            sub = abs(price_col_data[i]-price_line)
            if sub < min_sub:
                min_sub = sub
                max_row = i
    fit_pcode = pcode_col_data[max_row]
    return fit_pcode


def na(data_matrix, h):
    """随机赋空h个值"""
    import numpy as np
    data_nan = data_matrix.copy()
    xx = np.random.randint(data_matrix.shape[0], size=h)
    yy = np.random.randint(data_matrix.shape[1], size=h)
    for i in range(h):
        data_nan.iloc[xx[i], yy[i]] = 0
    return data_nan, xx, yy


def if_none(table,):
    lyst=list(table.iloc[:, 0])
    if len(lyst) == 0:
        return True


def data_add(table,pcode,col,pcode_col,brand_col,price_col,type_col,ser_col):
    table_new=table
    table_new=moudle2(table,table_new,pcode,brand_col)                           #原始表格序号从0开始排。
    if if_none(table_new):
        return table
    table_new = table_new.reset_index(drop=True)           #reset后序号从0开始排。
    
    table_new=moudle1(table_new,col)
    if if_none(table_new):
        '''
        此处添加价格判断函数，寻找所有品牌价格最相近行。
        '''
        if col == ser_col:
            table=moudle10(table,pcode,brand_col,pcode_col,ser_col,type_col)
        else:
            match_max_pcode = moudle12(table,pcode,price_col,pcode_col,brand_col)
            table=moudle9(table,match_max_pcode,pcode,col)
        return table
    table_new = table_new.reset_index(drop=True)           #reset
    
    p=0.5
    table_new=moudle5(table,table_new,p,pcode,price_col)
    if if_none(table_new):
        return table
    table_new = table_new.reset_index(drop=True)               #reset
    
    match_max_pcode=moudle6(table,table_new,pcode,type_col,pcode_col)
    table=moudle9(table,match_max_pcode,pcode,col)
    return table