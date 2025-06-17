# Read utf-8 encoded text file and write it out as is with no additional carriage return or line feed characters

import codecs

document_type = 'launchpad'
always_use_alias = False

input_directory = 'test/input'
output_directory = 'test/output'
file_name = 'test.txt'


def run():
    with codecs.open(f'{input_directory}/{file_name}', encoding='utf-8') as f:
        file_contents = f.read()
        with open(f'{output_directory}/{file_name}', 'bw') as file:
            file.write(bytes(file_contents, encoding="utf-8"))


if __name__ == '__main__':
    run()
