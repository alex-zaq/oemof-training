import datetime as dt



months = {
    'январь':1,
    'февраль':2,
    'март':3,
    'апрель':4,
    'май':5,
    'июнь':6,
    'июль':7,
    'август':8,
    'сентябрь':9,
    'октябрь':10,
    'ноябрь':11,
    'декабрь':12,
}


def set_label(*items, sep = '_'):
  return sep.join(items)

def set_natural_gas_price(usd_per_1000_m3):
  return usd_per_1000_m3 / 0.108

def convert_Mwth_to_1000_m3(Mwth):
    return Mwth * 0.108

def set_XY_label(ax, x_label, y_label):
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  
def get_time_slice(df, data_time_options):
    return df.loc[(df['date'] >= data_time_options['start_date'])
                     & (df['date'] <= data_time_options['end_date'])]
      
def find_first_monday(year, month, day):
    d = dt.datetime(year, int(month), 7)
    offset = -d.weekday() #weekday = 0 means monday
    return d + dt.timedelta(offset) 
  
def set_bus_group(group_name, bus_list):
    for bus in bus_list:
        bus.heat_demand_group_name = group_name
  
  
class Custom_counter:
	def __init__(self):
		self.index = 0
    
	def next(self):
		self.index+=1
		return self.index

	def reset_index(self):
		self.index = 0
  
  
  