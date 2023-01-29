import sys
import pandas as pd
sys.path.insert(0, './')
from custom_modules.excel_operations import get_excel_reader


excel_reader = get_excel_reader(folder ='./results/', file = 'res.xlsx' )
df = excel_reader(sheet_name='Sheet1')

blocks_types = list(df.columns)[1:]

time_stamp = list(df.iloc[:,0])

new_df = pd.DataFrame(columns=['blocks_type', 'timestamp', 'power'])

value = df[blocks_types[1]][5]

# new_df =  new_df.append({ 'blocks_type':1, 'timestamp': 2, 'power':4  }, ignore_index = True)
# new_df =  new_df.append({ 'blocks_type':1, 'timestamp': 2, 'power':4  }, ignore_index = True)

for block_type in blocks_types:
    for i, hour in enumerate(time_stamp):
        power = df[block_type][i]
        new_df = new_df.append({ 'blocks_type':block_type, 'timestamp': hour, 'power':power  }, ignore_index = True)
        


# data22 = data2.iloc[:,0:].sum(axis=1)

print('')