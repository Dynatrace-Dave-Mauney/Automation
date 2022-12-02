# Load findings to use in environment summary
def get_findings_dictionary(env):
	file_name = '../$Input/Reporting/findings_' + env + '.txt'
	file = open(file_name, 'r')

	current_finding_key = ''

	findings = {}
	current_finding_values = []
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
