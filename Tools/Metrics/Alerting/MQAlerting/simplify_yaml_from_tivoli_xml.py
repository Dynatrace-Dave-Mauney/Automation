"""

This module converts a specific YAML file to consolidate some repeating list elements.

If there are three list elements that are equal other than having different thresholds are consolidated into one element.

It is very customer specific, and unlikely to be useful for other use cases.

"""
import yaml


def process_yaml(input_filename, output_filename):
	yaml_dict = read_yaml(input_filename)
	new_yaml_dict = read_yaml(input_filename)

	for key in yaml_dict.keys():
		alert_list = yaml_dict.get(key)
		alert_keys_equal = False
		if len(alert_list) == 3:
			# print(key)
			# print(alert_list)
			if alert_list[0].get('msg') and alert_list[0].get('notify') and alert_list[0].get('distribution') and alert_list[0].get('lower') and alert_list[0].get('upper'):
				if alert_list[0].get('upper') == '0' and alert_list[1].get('upper') == '0' and alert_list[2].get('upper') == '0':
					for alert_key in ['msg' , 'notify', 'distribution']:
						# print(alert_list[0].get(alert_key))
						# print(alert_list[1].get(alert_key))
						# print(alert_list[2].get(alert_key))
						if alert_list[0].get(alert_key) == alert_list[1].get(alert_key) == alert_list[2].get(alert_key):
							alert_keys_equal = True
			else:
				pass
				# print('Missing key...')
				# print(alert_list[0].get('msg'))
				# print(alert_list[0].get('notify'))
				# print(alert_list[0].get('distribution'))
				# print(alert_list[0].get('lower'))
				# print(alert_list[0].get('upper'))
			if alert_keys_equal:
				new_yaml_dict.pop(key)
				new_yaml_dict[key] = [{'msg': alert_list[0].get('msg'), 'notify': alert_list[0].get('notify'), 'distribution': alert_list[0].get('distribution'), 'thresholds': [alert_list[0].get('lower'), alert_list[1].get('lower'), alert_list[2].get('lower')]}]

	write_yaml(new_yaml_dict, output_filename)


def read_yaml(input_file_name):
	with open(input_file_name, 'r') as file:
		document = file.read()
		yaml_data = yaml.load(document, Loader=yaml.FullLoader)
	return yaml_data


def write_yaml(any_dict, filename):
	with open(filename, 'w') as file:
		yaml.dump(any_dict, file, sort_keys=False)


def main():
	pass

	input_filename = 'queue_depth_full.yaml'
	output_filename = 'queue_depth.yaml'
	process_yaml(input_filename, output_filename)


if __name__ == '__main__':
	main()
