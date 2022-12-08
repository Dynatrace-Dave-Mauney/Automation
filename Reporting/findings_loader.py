# Load findings to use in environment summary
def get_findings_dictionary(env):
	findings = {}

	file_name = '../$Input/Reporting/findings_' + env + '.txt'
	try:
		file = open(file_name, 'r')
	except FileNotFoundError:
		print(f'No findings loaded.')
		print('To add findings:')
		print(f'1. Create {file_name}.')
		print('2. Copy the section titles from the html report that need findings added.')
		print('3. Add your findings text below them.')
		print('Example:')
		print('Network Zone Summary:')
		print('Many OneAgents are currently using the "Default" Network Zone.')
		return findings

	current_finding_key = ''

	current_finding_values = []
	if file:
		for line in file:
			if "Summary:" in line:
				if current_finding_key != '':
					findings[current_finding_key] = current_finding_values
					current_finding_key = line.replace(':\n', '')
					current_finding_values = []
				else:
					current_finding_key = line.replace(':\n', '')
			else:
				if current_finding_key != '':
					current_finding_values.append(line)
		file.close()

	# Handle the last summary section before EOF
	if current_finding_key != '':
		findings[current_finding_key] = current_finding_values

	# print(findings)
	# print(findings.keys())
	return findings

# Test locally:
# dict = get_findings_dictionary("Prod")
# print(dict)
# print(dict.keys())
