"""

This module creates YAML files from Tivoli configuration files.

The YAML files are later used to raise problems when various MQ thresholds are violated.

Although the conversion process is very specific to a particular customer, the same technique can likely be adapted for
other Tivoli configurations.

"""
import xml.etree.ElementTree as ET
import glob
import os
import os.path
import yaml


def process_xml(filename, yaml_dict, queue_depth_unit):
	sitname = cmd = pdt = text = situation_name = slot_msg_value = slot_notify_value = slot_queue_name_value = queue_name = distribution = ''
	lower_threshold = upper_threshold = '0'
	tree = ET.parse(filename)
	root = tree.getroot()
	# print(root)
	for child in root:
		if child.tag == 'ROW':
			# print(filename)
			for row_child in child:
				# print(row_child.tag, row_child.text)
				if row_child.tag == 'SITNAME':
					sitname = row_child.text
				if row_child.tag == 'CMD':
					# print(row_child.tag, row_child.text)
					cmd = row_child.text
					cmd_splits = cmd.split(' ')
					distribution = cmd_splits[-1]
					if '@' not in distribution:
						if "-to " in cmd:
							cmd_splits = cmd.split('-to ')
							distribution = cmd_splits[1].split(' ')[0]
						else:
							# if distribution == '*NONE':
							distribution = ''
				if row_child.tag == 'PDT':
					# print(row_child.tag, row_child.text)
					pdt = row_child.text.replace("Queue_Name *EQ ' ", "Queue_Name *EQ '")
					# print(f'pdt: {pdt}')

					if "Queue_Name *EQ" in pdt:
						pdt_splits = pdt.split("Queue_Name *EQ")
						queue_name = pdt_splits[1].strip().split(" ")[0].replace("'", "")
						if queue_name == '':
							# queue_name = pdt_splits[1].replace("'", "")
							queue_name = pdt_splits[1].strip().split("'")[0].replace("'", "")
							if queue_name == '':
								print(f'Queue name: "{queue_name}"', f'"{pdt_splits[1]}"', pdt_splits, pdt)
							else:
								if ' ' in queue_name:
									print(f'Space in queue name: "{queue_name}"', pdt, pdt_splits, pdt_splits[1])
					# else:
					# 	queue_name = pdt
					# print(f'queue_name: {queue_name}')
					if "Percent_Full *GE " in pdt:
						pdt_splits = pdt.split("Percent_Full *GE ")
						lower_threshold = pdt_splits[1].split(" ")[0]
						# print(pdt)
						# print(pdt_splits)
						# print(pdt_splits[1])
						# print(lower_threshold)
					if "Percent_Full *GT " in pdt:
						pdt_splits = pdt.split("Percent_Full *GT ")
						lower_threshold = pdt_splits[1].split(" ")[0]
						# print(pdt)
						# print(pdt_splits)
						# print(pdt_splits[1])
						# print(lower_threshold)
					if "Percent_Full *LE " in pdt:
						pdt_splits = pdt.split("Percent_Full *LE ")
						upper_threshold = pdt_splits[1].split(" ")[0]
						# print(pdt)
						# print(pdt_splits)
						# print(pdt_splits[1])
						# print(upper_threshold)
					if "Percent_Full *LT " in pdt:
						pdt_splits = pdt.split("Percent_Full *LT ")
						upper_threshold = pdt_splits[1].split(" ")[0]
						# print(pdt)
						# print(pdt_splits)
						# print(pdt_splits[1])
						# print(upper_threshold)
					# if "Percent_Full *GE " not in pdt and "Percent_Full *GT " not in pdt and "Percent_Full *LT " not in pdt:
					# 	lower_threshold = pdt
					if "Current_Depth *GE " in pdt:
						pdt_splits = pdt.split("Current_Depth *GE ")
						lower_threshold = pdt_splits[1].split(" ")[0]
						# print(pdt)
						# print(pdt_splits)
						# print(pdt_splits[1])
						# print(lower_threshold)
					if "Current_Depth *GT " in pdt:
						pdt_splits = pdt.split("Current_Depth *GT ")
						lower_threshold = pdt_splits[1].split(" ")[0]
						# print(pdt)
						# print(pdt_splits)
						# print(pdt_splits[1])
						# print(lower_threshold)
					if "Oldest_Message_Seconds *GT " in pdt:
						pdt_splits = pdt.split("Oldest_Message_Seconds *GT ")
						lower_threshold = pdt_splits[1].split(" ")[0]
						# print(pdt)
						# print(pdt_splits)
						# print(pdt_splits[1])
						# print(lower_threshold)
					if "Oldest_Message_Seconds *GE " in pdt:
						pdt_splits = pdt.split("Oldest_Message_Seconds *GE ")
						lower_threshold = pdt_splits[1].split(" ")[0]
						# print(pdt)
						# print(pdt_splits)
						# print(pdt_splits[1])
						# print(lower_threshold)
				if row_child.tag == 'TEXT':
					# print(row_child.tag, row_child.text)
					text = row_child.text
				if row_child.tag == 'MAP':
					# print('map row', row_child.tag, row_child.text)
					map_root = ET.fromstring(row_child.text)
					# print('map root', map_root.tag, map_root.attrib)
					situation_name = map_root.attrib.get('name')
					for map_child in map_root:
						slot_name = map_child.attrib.get('slotName')
						# print(slot_name)
						# print('map child', map_child.tag, map_child.attrib)
						for child_of_map_child in map_child:
							# print('child of map child', child_of_map_child.tag, child_of_map_child.text, child_of_map_child.attrib)
							if slot_name == 'msg' and child_of_map_child.tag == 'literalString':
								slot_msg_value = child_of_map_child.attrib.get('value')
							if slot_name == 'notify' and child_of_map_child.tag == 'literalString':
								slot_notify_value = child_of_map_child.attrib.get('value')
							if slot_name == 'queue_name' and child_of_map_child.tag == 'mappedAttributeValue':
								slot_queue_name_value = child_of_map_child.attrib.get('name')

	print_row(sitname, cmd, pdt, text, situation_name, slot_msg_value, slot_notify_value, slot_queue_name_value, queue_name, distribution, lower_threshold, upper_threshold)

	if 'Percent_Full *G' in pdt and queue_depth_unit == 'message':
		pass
	else:
		if 'Current_Depth *G' in pdt and queue_depth_unit == 'percent':
			pass
		else:
			if queue_name == '':
				print(f'No queue name for {filename}: {pdt}')
			else:
				if lower_threshold == '0':
					print(f'Lower threshold is zero for {filename}: {pdt}')
				else:
					# print(queue_name, slot_msg_value, slot_notify_value, distribution, lower_threshold,upper_threshold)
					if yaml_dict.get(queue_name):
						yaml_dict[queue_name].append({'msg': slot_msg_value, 'notify': slot_notify_value, 'distribution': distribution, 'lower': lower_threshold, 'upper': upper_threshold})
					else:
						yaml_dict[queue_name] = [{'msg': slot_msg_value, 'notify': slot_notify_value, 'distribution': distribution, 'lower': lower_threshold, 'upper': upper_threshold}]


def process_all_files_in_path(path, output_filename, queue_depth_unit):
	yaml_dict = {}

	for filename in glob.glob(path):
		if os.path.isfile(filename):
			process_xml(filename, yaml_dict, queue_depth_unit)

	write_yaml(yaml_dict, output_filename)


def write_yaml(any_dict, filename):
	with open(filename, 'w') as file:
		yaml.dump(any_dict, file, sort_keys=False)


def print_row(sitname, cmd, pdt, text, situation_name, slot_msg_value, slot_notify_value, slot_queue_name_value, queue_name, distribution, lower_threshold, upper_threshold):
	pass
	# print(sitname, cmd, pdt, text, situation_name, slot_msg_value, slot_notify_value, slot_queue_name_value)
	# return

	# print(f'sitname: {sitname}')
	# print(f'cmd: {cmd}')
	# print(f'pdt: {pdt}')
	# print(f'text: {text}')
	# print(f'situation_name: {situation_name}')
	# print(f'slot_msg_value: {slot_msg_value}')
	# print(f'slot_notify_value: {slot_notify_value}')
	# print(f'slot_queue_name_value: {slot_queue_name_value}')
	# print(f'queue_name: {queue_name}')
	# print(f'distribution: {distribution}')
	# print(f'lower_threshold: {lower_threshold}')
	# print(f'upper_threshold: {upper_threshold}')

	# if upper_threshold != 0:
	# 	print(f'upper_threshold: {upper_threshold}')


def main():
	pass

	path = 'SITUATIONS/SITUATION/MQ/*Aging*.xml'
	output_filename = 'oldest_message.yaml'
	queue_depth_unit = ''
	process_all_files_in_path(path, output_filename, queue_depth_unit)

	path = 'SITUATIONS/SITUATION/MQ/*Depth*.xml'
	output_filename = 'queue_depth_full.yaml'
	queue_depth_unit = 'message'
	process_all_files_in_path(path, output_filename, queue_depth_unit)

	path = 'SITUATIONS/SITUATION/MQ/*Depth*.xml'
	output_filename = 'queue_depth_pct.yaml'
	queue_depth_unit = 'percent'
	process_all_files_in_path(path, output_filename, queue_depth_unit)


if __name__ == '__main__':
	main()
