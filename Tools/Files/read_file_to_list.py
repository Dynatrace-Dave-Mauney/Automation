filename = 'app_list_from_ui.txt'
with open(filename, 'r') as f:
    lines = f.readlines()
    for line in lines:
        print(line.strip())