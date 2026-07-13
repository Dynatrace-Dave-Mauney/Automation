import glob
import os


def main():
    file_dict = {}
    input_glob_pattern = "../../Dashboards/Templates-Overview-Splits/*.json"
    for file_name in glob.glob(input_glob_pattern, recursive=True):
        if os.path.isfile(file_name) and '.' in os.path.basename(file_name):
            base_name = os.path.basename(file_name)
            print("    put_dashboards(env_name, f'Custom/Overview-{env_name}/" + base_name + "', owner=owner, skip_list=current_customer_skip_list)")


if __name__ == '__main__':
    main()
