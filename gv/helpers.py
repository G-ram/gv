def exists(name, loc1, loc2={}):
	if type(loc1) is not dict:
		return hasattr(loc1, name)
	return (name in loc1.keys()) or (name in loc2.keys())
