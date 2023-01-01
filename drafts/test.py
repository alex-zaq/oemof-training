import sys
sys.path.insert(0, './modules')
from collections import namedtuple
from wrapper_excel_operations import *
# group_options = namedtuple("group_options", "station_name turb_name")


def set_group(*items, separator = '_'):
  return separator.join(items)


print(set_group('aad', 'sasdf'))


# g = group_options("минская тэц-4","Т-250")

# print(g.station_name)


# reader = get_reader_by_folder('./drafts', '1.xlsx')

# res = reader('hw')[:24]


# print(res)




# def counter():
# 	i = 0
# 	while True:
# 		i+=1
# 		yield i
  
# a = counter()

# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))
# print(next(a))