import json
import sys

from Reuse import dynatrace_api
from Reuse import environment


def main():
    args = sys.argv[1:]
    if args:
        env_name, env, token = environment.get_environment(args[1])
        print('env_name:', env_name)
        print('env:', env)
        print('token:', token)
        client_secret = args[7]
        print('client_secret:', client_secret)
        client_id_splits = client_secret.split('.')
        client_id = client_id_splits[0] + '.' + client_id_splits[1]
        print('client_id:', client_id)
        account = args[9]
        print('account:', account)
        email_id = args[11]
        print('email_id:', email_id)
        automation_token = post_dynatrace_automation_token(env, token)
        print('automation_token:', automation_token)

        with open(f'set_Env{env_name}.bat', 'w') as windows_bat:
            windows_bat.write('')

        with open(f'set_Env{env_name}.bat', 'a') as windows_bat:
            windows_bat.write('@echo off\n')
            windows_bat.write('\n')
            windows_bat.write('rem Be sure to restart your command prompt/PyCharm IDE after this script runs to use the new environment variable settings\n')
            windows_bat.write('\n')
            windows_bat.write(f'setx DYNATRACE_PROD_TENANT {env}\n')
            windows_bat.write(f'setx DYNATRACE_DASHBOARD_OWNER {email_id}\n')
            windows_bat.write('\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_ENV_NAME {env_name}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_REPORTING_ENV_NAME {env_name}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_TOKEN_MANAGEMENT_ENV_NAME {env_name}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_TOOLS_ENV_NAME {env_name}\n')
            windows_bat.write(f'setx DYNATRACE_PLATFORM_DOCUMENT_ENV_NAME {env_name}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_REPORTING_DEPLOYMENT_ENV_NAME {env_name}\n')
            windows_bat.write('\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_{env_name.upper()}_TOKEN {automation_token}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_REPORTING_DEPLOYMENT_{env_name.upper()}_TOKEN {automation_token}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_REPORTING_{env_name.upper()}_TOKEN {automation_token}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_TOKEN_MANAGEMENT_{env_name.upper()}_TOKEN {token}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_TOOLS_{env_name.upper()}_TOKEN {automation_token}\n')
            windows_bat.write('\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_ACCOUNT_ID {account}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_CLIENT_ID {client_id}\n')
            windows_bat.write(f'setx DYNATRACE_AUTOMATION_CLIENT_SECRET {client_secret}\n')
            windows_bat.write('setx DYNATRACE_AUTOMATION_SKIP_SLOW_ACCOUNT_MANAGEMENT_API_CALLS True\n')

        with open(f'set_Env{env_name}.sh', 'w') as linux_sh:
            linux_sh.write('')

        with open(f'set_Env{env_name}.sh', 'a') as linux_sh:
            linux_sh.write(f'export DYNATRACE_PROD_TENANT={env}\n')
            linux_sh.write(f'export DYNATRACE_DASHBOARD_OWNER={email_id}\n')
            linux_sh.write('\n')
            linux_sh.write(f'export DASHBOARD_OWNER_EMAIL={email_id}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_ENV_NAME={env_name}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_REPORTING_ENV_NAME={env_name}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_TOKEN_MANAGEMENT_ENV_NAME={env_name}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_TOOLS_ENV_NAME={env_name}\n')
            linux_sh.write(f'export DYNATRACE_PLATFORM_DOCUMENT_ENV_NAME={env_name}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_REPORTING_DEPLOYMENT_ENV_NAME={env_name}\n')
            linux_sh.write('\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_{env_name.upper()}_TOKEN={automation_token}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_REPORTING_DEPLOYMENT_{env_name.upper()}_TOKEN={automation_token}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_REPORTING_{env_name.upper()}_TOKEN={automation_token}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_TOKEN_MANAGEMENT_{env_name.upper()}_TOKEN={token}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_TOOLS_{env_name.upper()}_TOKEN={automation_token}\n')
            linux_sh.write('\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_ACCOUNT_ID={account}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_CLIENT_ID={client_id}\n')
            linux_sh.write(f'export DYNATRACE_AUTOMATION_CLIENT_SECRET={client_secret}\n')
            linux_sh.write('export DYNATRACE_AUTOMATION_SKIP_SLOW_ACCOUNT_MANAGEMENT_API_CALLS=True\n')
    else:
        print('Must provide environment name argument!')


def post_dynatrace_automation_token(env, token):
    # Supports Token Key: DYNATRACE_AUTOMATION_PERSONAL_TOKEN (where "PERSONAL" can be any environment name).
    # Has every known permission needed by the automation project (and maybe some more!)
    return post_token(env, token, 'Automation', [
        "ActiveGateCertManagement",
        "CaptureRequestData",
        "DTAQLAccess",
        "DataExport",
        "DataImport",
        "DssFileManagement",
        "ExternalSyntheticIntegration",
        "InstallerDownload",
        "ReadConfig",
        "ReadSyntheticData",
        "RumJavaScriptTagManagement",
        "WriteConfig",
        "activeGateTokenManagement.read",
        "activeGates.read",
        "apiTokens.read",
        "auditLogs.read",
        "credentialVault.read",
        "entities.read",
        "entities.write",
        "events.ingest",
        "events.read",
        "events.read",
        "extensionConfigurations.read",
        "extensionEnvironment.read",
        "extensions.read",
        "geographicRegions.read",
        "hub.read",
        "logs.ingest",
        "metrics.ingest",
        "metrics.read",
        "networkZones.read",
        "problems.read",
        "releases.read",
        "settings.read",
        "settings.write",
        "slo.read",
        "slo.write",
        "syntheticExecutions.read",
        "syntheticLocations.read",
        ])


def post_token(env, token, token_name, token_scopes):
    endpoint = '/api/v2/apiTokens'
    payload = json.dumps({"name": token_name, "scopes": token_scopes})
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
    token_posted = r.json()
    secret = token_posted.get("token")

    print(f'Created token named "{token_name}" with scopes: {token_scopes}: {token_posted.get("token")}')
    print(f'Be sure to save the token displayed below in your password keeper/secrets manager/vault!')
    print(secret)

    return secret


if __name__ == '__main__':
    main()

# NOTE:
# usage: generate_environment_setup_scripts.py [-h] [-n ENVIRONMENT_NAME] [-e ENVIRONMENT] [-t TOKEN] [-cs CLIENT_SECRET] [-od ACCOUNT_ID] [-of EMAIL_ADDRESS]
# The "bootstrap" token must have "Write API tokens" permission.
# The "Automation" token will be generated using it.
# Using the "od" and "of" arguments for account and email is a temporary hack.
# Using argument positions is a temporary hack, so be sure to use the exact order specified.
# EXAMPLE:
# python generate_environment_setup_scripts.py -n Prod -e abcd1234 -t dt0c01.AAA.BBB -cs dt0s02.CCC.DDD -od aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa -of nobody@example.com
# TIP:
# Create a script named "gen_EnvXXX.bat" or "gen_EnvXXX.sh" (replacing "XXX" with the environment name) to trigger the process.
#
