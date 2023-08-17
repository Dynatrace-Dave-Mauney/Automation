#
# Process "nslookup_output.txt" file created a command such as
#
# nslookups.bat 1> nslookups_output.txt 2>&1
#
# where nslookups.bat is a series of nslookup commands like
#
# nslookup 10.10.10.1
# nslookup 10.10.10.2
#

import os

infile_name = '../../$Input/Tools/Files/nslookup_output.txt'

def process_nslookup_file():
    with open(infile_name, 'r', encoding='utf-8') as f:
        infile_lines = f.readlines()
        print(infile_lines)

        for infile_line in infile_lines:
            line = infile_line.strip()
            if 'nslookup' in line:
                host = line.split(' ')[1]
            if 'Non-existent domain' in line:
                print(f'{host} not found')
            if 'Name:' in line:
                host_name = line.replace('Name:', '').strip()
                print(f'{host}:{host_name}')


def main():
    process_nslookup_file()


if __name__ == '__main__':
    main()
