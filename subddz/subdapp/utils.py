

def check_dict(data, keys):
	for key in keys:
		if key not in data:
			raise Exception('required')
	return