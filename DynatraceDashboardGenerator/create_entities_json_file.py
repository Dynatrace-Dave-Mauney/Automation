#
# Save entities from Dynatrace REST API to a file.
# This requires getting all entity types first (from REST rather than file, for convenience)
#

import json
import sys

from Reuse import dynatrace_api

def get_entity_types(url, token):
    # print(f'get_entity_types({url}, {token})')
    endpoint = '/api/v2/entityTypes'
    params = 'pageSize=500'
    json_list = dynatrace_api.get(url, token, endpoint, params)
    entity_types = []
    for json_dict in json_list:
        entity_types.extend(json_dict.get('types'))
    return entity_types


def get_entities(url, token, entity_types):
    print(f'get_entities({url}, {token}, {entity_types})')
    all_entities = []
    for entity_type_dict in entity_types:
        entity_type = entity_type_dict.get('type')
        # entity_type_properties = entity_type_dict.get('properties')
        # entity_type_fields = get_entity_type_fields(entity_type_properties)
        endpoint = '/api/v2/entities'
        params = 'entitySelector=type(' + entity_type + ')&from=now-1y&pageSize=1000'
        # Note:  This is a huge amount of data.  To reduce it, you can remove all but "+properties" or get even more
        # specific with the necessary properties, which are at the time of this comment just for SERVICE, and limited
        # to the databaseVendor property, which is used to distinguish database services from regular services.
        # To maintain even this level of detail may require some "pagination" work in larger environments.
        fields = 'fromRelationships,+lastSeenTms,+firstSeenTms,+managementZones,+toRelationships,+tags,+properties'
        # if entity_type == 'SERVICE':
        params = params + '&fields=' + fields
        entities_list = dynatrace_api.get(url, token, endpoint, params)
        # print(entities_list[0])
        # exit()

        for entities in entities_list:
            total_count = int(entities.get('totalCount'))
            if total_count > 0:
                entities_per_type = entities.get('entities')
                for entity in entities_per_type:
                    all_entities.append(entity.copy())

    return all_entities


def write_entities_file(url, token):
    entity_types = get_entity_types(url, token)
    entities = get_entities(url, token, entity_types)

    json_string = json.dumps(entities)
    # Custom pretty print logic:
    # 1. Add newline after opening brace of metrics list
    # 2. Add newline after each metric in list
    # 3. Add newline before closing brace of metrics list
    json_string = json_string.replace('[{"entityId":', '[\n{"entityId":')
    json_string = json_string.replace(', {"entityId":', ',\n{"entityId":')
    # json_string = json_string.replace('}]', '}\n]')

    with open('entities.json', 'w') as file:
        file.write(json_string)


def process(arguments):
    # Assume tenant/environment URL followed by Token
    url = arguments[1]
    token = arguments[2]

    print('url: ' + url)
    print('token: ' + token[0:31] + '.*' + ' (masked for security)')

    write_entities_file(url, token)


def main(arguments):
    help_text = '''
    create_entities_file.py creates an entities.txt file for an environment

    Usage:    create_entities_file.py <tenant/environment URL> <token>
    '''

    print('args' + str(arguments))
    if len(arguments) < 2:
        print(help_text)
        raise ValueError('Too few arguments!')
    if len(arguments) > 3:
        print(help_text)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help_text)
    elif arguments[1] in ['-v', '--entities']:
        print('1.0')
    else:
        if len(arguments) == 3:
            process(arguments)
        else:
            print(help_text)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
