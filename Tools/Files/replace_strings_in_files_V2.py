import os

from Reuse import environment


def main():
    configuration_file = 'configurations.yaml'
    old_strings = environment.get_configuration('replace_strings_in_files_V2_old_strings', configuration_file=configuration_file)
    new_strings = environment.get_configuration('replace_strings_in_files_V2_new_strings', configuration_file=configuration_file)
    input_directory_name = environment.get_configuration('replace_strings_in_files_V2_input_directory_name', configuration_file=configuration_file)
    output_directory_name = environment.get_configuration('replace_strings_in_files_V2_output_directory_name', configuration_file=configuration_file)

    print('Input Directory Name: ', input_directory_name)
    print('Output Directory Name:', output_directory_name)

    try:
        for file_name in os.listdir(input_directory_name):
            src = f'{input_directory_name}/{file_name}'
            dst = f'{output_directory_name}/{file_name}'

            with open(src, 'r', encoding='utf-8') as infile:
                new_string = infile.read()
                index = 0
                for old_string in old_strings:
                    from_string = old_string
                    to_string = new_strings[index]
                    new_string = new_string.replace(from_string, to_string)
                    print(f'Replacing {from_string} with {to_string}')
                    index += 1
                print(f'{src} {dst} {new_string}')
                with open(dst, 'w', encoding='utf-8') as outfile:
                    outfile.write(new_string)

    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
