import pandas as pd
import os



data_folder = os.getcwd() + "/data_excel"
data1 = pd.read_excel(os.path.join(data_folder,'test.xlsx'), sheet_name='1')
data2 = pd.read_excel(os.path.join(data_folder,'test.xlsx'), sheet_name='2')


# print(date)

data11 = data1.iloc[:,1:].sum(axis=1)
data22 = data2.iloc[:,1:].sum(axis=1)

data11.name = 'sdf'
data22.name = 'sdf'

date = data1.iloc[:,0 ]
lst = [date, data11, data22]

res = pd.concat(lst, axis=1)
res.columns = ['asdf','asdf', 'dsf']


print(res)





# data11.index.name = 'df'
# data33 = data11 + data22
# data33.columns = ['Value', 'k']
# print(type(data33))

# data.index.name = 'zaq'

# res = data1.iloc[:,0] 


# print(data1)
# print(data2)
# print(data2)