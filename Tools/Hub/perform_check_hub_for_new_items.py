import hub_summary_from_api_and_web

from Reuse import environment

# env_name, env, token = environment.get_environment('Prod')
# env_name, env, token = environment.get_environment('Prep')
# env_name, env, token = environment.get_environment('Dev')
env_name, env, token = environment.get_environment('Personal')
# env_name, env, token = environment.get_environment('FreeTrial1')

hub_summary_from_api_and_web.check_hub_for_new_items(env, token)