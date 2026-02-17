# requirements.txt add for py 3 -> pypiwin32
import win32com.client as win32


# Send or draft an email from Outlook
# This method supports one or more attachments
# Emails can be sent silently or a draft can be displayed for review depending on value of "send".
def send_outlook_email(text, subject, recipient, attachments, send):
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
