import json

f = open('config_v1_spec3.json',)
data = json.load(f)
paths = data.get('paths')
# print(paths)

for path in paths:
    # skip endpoints that require an {id} or other variable
    if '{' not in path:
        get = paths.get(path).get('get')
        getter = True
        if get is None:
            getter = False
        if getter:
            summary = get.get('summary')
            # print(path + ' - ' + summary)
            if 'List' in summary:
                print('    saveList("' + path + '")')
            else:
                print('    saveEntity("' + path + '")')
f.close()
