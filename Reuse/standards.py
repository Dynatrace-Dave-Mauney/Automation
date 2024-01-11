# Enforce customer-specific naming standards

from Reuse import environment

supported_naming_standard_flavors = [1]
supported_entity_types = ['management zone', 'alerting profile', 'problem notification integration', 'host group']


def check_naming_standard(env_name, name, configuration_object, entity_type):
    naming_standard_flavor = environment.get_configuration('standards.naming_standard_flavor', configuration_object=configuration_object)

    if not naming_standard_flavor:
        return False, 'No naming standard flavor in configuration object'

    if naming_standard_flavor not in supported_naming_standard_flavors:
        return False, 'Naming standard flavor not in supported naming standard flavors list'

    if entity_type not in supported_entity_types:
        return False, f'Entity type "{entity_type}" not in supported entity types list'

    if naming_standard_flavor == 1:
        return check_naming_standard_flavor_1(env_name, name, configuration_object, entity_type)


def check_naming_standard_flavor_1(env_name, name, configuration_object, entity_type):
    valid_environments = environment.get_configuration(f'standards.valid_environments_{env_name}', configuration_object=configuration_object)
    if not valid_environments:
        return False, f'No naming standard valid environments list found in configuration object'

    name_split_list = name.split('-')
    name_hyphen_count = len(name_split_list) - 1
    if entity_type == 'host group' and (name_hyphen_count == 0 or name_hyphen_count > 2):
        # print('Rule 1', name, name_hyphen_count, name_split_list)
        return False, f'Entity type {entity_type} name must have one or two hyphens'
    else:
        if entity_type != 'host group' and name_hyphen_count != 1:
            # print('Rule 1', name, name_hyphen_count, name_split_list)
            return False, f'Entity type {entity_type} name must have one hyphen'
        else:
            application_environment_name = name_split_list[-1].upper()
            if application_environment_name not in valid_environments:
                # print('Rule 2', name, name_hyphen_count, name_split_list)
                return False, f'Application Environment Name {name} not found in the valid environment list: {valid_environments}'

    # print('Rule 3', name, name_hyphen_count, name_split_list)
    return True, 'Name meets standards'
