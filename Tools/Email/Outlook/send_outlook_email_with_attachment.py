# requirements.txt add for py 3 -> pypiwin32
import win32com.client as win32
from Reuse import email
from Reuse import environment


# For local testing, if ever needed...
def send_email(text, subject, recipient, attachments, send):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.Subject = subject
    mail.HtmlBody = text
    for attachment in attachments:
        mail.Attachments.Add(attachment)
    if send:
        mail.Send()
    else:
        mail.Display(False)


def main():
    configuration_file = 'configurations.yaml'
    subject = environment.get_configuration('subject', configuration_file=configuration_file)
    body = environment.get_configuration('body', configuration_file=configuration_file)
    path = environment.get_configuration('path', configuration_file=configuration_file)
    address = environment.get_configuration('address', configuration_file=configuration_file)
    attachments = [path]
    email.send_outlook_email(body, subject, address, attachments, True)
    # send_email(body, subject, address, attachments, True)


if __name__ == '__main__':
    main()
