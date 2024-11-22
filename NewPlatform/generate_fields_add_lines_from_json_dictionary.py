import json

json_data_file_name = "customer_specific_dictionary.json"
json_dictionary_variable_name = "data"


def run():
    json_data = read_json(json_data_file_name)
    print(json_data)

    keys = json_data.keys()

    for key in sorted(keys):
        # print(key)
        print(f"| fieldsAdd {key} = {json_dictionary_variable_name}[{key}]")


def read_json(path):
    with open(path, 'r', encoding='utf-8') as infile:
        json_data = json.loads(infile.read())
        return json_data


if __name__ == '__main__':
    run()
