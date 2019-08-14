from data_add_class import Data_add
import matrix_completion_zd as mc_zd
import pandas as pd
import xlrd
import openpyxl
"""主程序：分别通过调用matrix_completion_zd、
data_add_class模块中的Com类和Data_add类
其中：
address_in为文件读入地址
address_out为文件输出地址
"""
address_in = "lib_nonstand-stand_price.xlsx"
address_out = 'com_lib_nonstand-stand.xlsx'


com_1 = mc_zd.Com(address_in)
data_1 = com_1.train_out()
com_2 = Data_add(address_in)
data_2 = com_2.data_add_main()
data_com = pd.concat([data_2, data_1], axis=1, ignore_index=False)
# data_com.to_csv(address_out, sep=',', index=0, encoding='utf_8_sig', mode='a')   # 导出为csv文件
data_com.to_excel(address_out, index=0)                                            # 导出为xlsx文件
print("填写完成！输出文件为当前目录下的", address_out, "文件")
