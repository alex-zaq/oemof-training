

def set_label(*items, sep = '_'):
  return sep.join(items)

def counter():
	i = 0
	while True:
		i+=1
		yield i

def set_natural_gas_price(usd_per_1000_m3):
  return usd_per_1000_m3 * 0.107