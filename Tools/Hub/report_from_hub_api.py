from Reuse import dynatrace_api
from Reuse import environment


def process_hub_categories(env, token):
    print('Hub Categories')
    print(f'id|name|description')
    endpoint = '/api/v2/hub/categories'
    hub_categories_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for hub_categories_json in hub_categories_json_list:
        inner_hub_categories_json_list = hub_categories_json.get('items')
        for inner_hub_categories_json in inner_hub_categories_json_list:
            hub_category_id = inner_hub_categories_json.get('id')
            hub_category_name = inner_hub_categories_json.get('name')
            hub_category_description = inner_hub_categories_json.get('description')
            print(f'{hub_category_id}|{hub_category_name}|{hub_category_description}')


def process_hub_items(env, token, show_description_blocks):
    print('Hub items')
    print(f'id|name|description')
    print('type|id|name|description|tags|documentationLink|marketingLink|comingSoon|artifactId')
    endpoint = '/api/v2/hub/items'
    hub_items_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    for hub_items_json in hub_items_json_list:
        inner_hub_items_json_list = hub_items_json.get('items')
        for inner_hub_items_json in inner_hub_items_json_list:
            hub_item_type = inner_hub_items_json.get('type')
            hub_item_id = inner_hub_items_json.get('itemId')
            hub_item_name = inner_hub_items_json.get('name')
            hub_item_description = inner_hub_items_json.get('description')
            hub_item_tags = inner_hub_items_json.get('tags')
            hub_item_documentation_link = inner_hub_items_json.get('documentationLink')
            hub_item_marketing_link = inner_hub_items_json.get('marketingLink')
            hub_item_coming_soon = inner_hub_items_json.get('comingSoon')
            hub_item_artifact_id = inner_hub_items_json.get('artifactId')
            has_description_blocks = inner_hub_items_json.get('hasDescriptionBlocks')
            if show_description_blocks and has_description_blocks:
                hub_technology_description_list = get_technology_description_blocks(env, token, hub_item_id)
                print(f'{hub_item_type}|{hub_item_id}|{hub_item_name}|{hub_item_description}|{hub_item_tags}|{hub_item_documentation_link}|{hub_item_marketing_link}|{hub_item_coming_soon}|{hub_item_artifact_id}')
                for hub_technology_description in hub_technology_description_list:
                    print(hub_technology_description)
            else:
                print(f'{hub_item_type}|{hub_item_id}|{hub_item_name}|{hub_item_description}|{hub_item_tags}|{hub_item_documentation_link}|{hub_item_marketing_link}|{hub_item_coming_soon}|{hub_item_artifact_id}')


def get_technology_description_blocks(env, token, hub_technology_id):
    technology_description_blocks = []
    endpoint = f'/api/v2/hub/technologies/{hub_technology_id}' 
    hub_technology_json = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    if not hub_technology_json.get('error'):
        hub_technology_description_blocks = hub_technology_json.get('descriptionBlocks')
        if hub_technology_description_blocks:
            for hub_technology_description_block in hub_technology_description_blocks:
                source = technology_description_blocks.append(hub_technology_description_block.get('source'))
                if source:
                    technology_description_blocks.append(source)
    return technology_description_blocks


def main():
    friendly_function_name = 'Dynatrace Automation Tools'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    print('Hub Summary')
    # process_hub_categories(env, token)
    process_hub_items(env, token, False)


if __name__ == '__main__':
    main()
