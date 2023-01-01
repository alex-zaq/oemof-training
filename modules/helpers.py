

def set_label(*items, sep = '_'):
  return sep.join(items)

def counter():
	i = 0
	while True:
		i+=1
		yield i
