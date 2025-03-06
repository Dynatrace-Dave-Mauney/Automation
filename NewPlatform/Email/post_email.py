import json

from Reuse import environment
from Reuse import new_platform_api


def run():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)

    email_to = 'nobody@dynatrace.com'
    email_cc = 'nobody@dynatrace.com'
    email_bcc = 'nobody@dynatrace.com'
    email_subject = 'Some Subject'
    email_body = 'Some Body'
    email_notification_url = 'https://xxxxxxxx.apps.dynatrace.com'

    post_email(env, client_id, client_secret, email_to, email_cc, email_bcc, email_subject, email_body, email_notification_url)


def post_email(env, client_id, client_secret, email_to, email_cc, email_bcc, email_subject, email_body, email_notification_url):
    scope = 'email:emails:send'

    payload = {
      "toRecipients": {
        "emailAddresses": [
          ""
        ]
      },
      "ccRecipients": {
        "emailAddresses": [
          ""
        ]
      },
      "bccRecipients": {
        "emailAddresses": [
          ""
        ]
      },
      "subject": "",
      "body": {
        "contentType": "text/plain",
        "body": ""
      },
      "notificationSettingsUrl": ""
    }

    payload['toRecipients']['emailAddresses'][0] = email_to
    payload['ccRecipients']['emailAddresses'][0] = email_cc
    payload['bccRecipients']['emailAddresses'][0] = email_bcc
    payload['subject'] = email_subject
    payload['body']['contentType'] = 'text/plain'
    payload['body']['body'] = email_body
    payload['notificationSettingsUrl'] = email_notification_url

    payload = json.dumps(payload)
    print(payload)

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    api_url = f'{env}/platform/email/v1/emails'
    new_platform_api.post(oauth_bearer_token, api_url, payload)


if __name__ == '__main__':
    run()
