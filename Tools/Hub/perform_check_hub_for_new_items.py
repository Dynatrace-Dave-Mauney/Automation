import os
import hub_summary_from_api_and_web

# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'

masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

print(f'Environment Name: {env_name}')
print(f'Environment:      {env}')
print(f'Token:            {masked_token}')

print('')

hub_summary_from_api_and_web.check_hub_for_new_items(env, token)