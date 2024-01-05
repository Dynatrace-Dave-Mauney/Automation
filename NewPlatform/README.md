# OAuth Client Details
The "NewPlatform" modules make use of the "Document service" API endpoint.

The easy way to make sure they each have all the permissions needed is to create an OAuth Client with every permission under the "Document Service".

- In the "Old UI", use the Person icon at the top right to navigate to "Account Settings", or just navigate directly to https://myaccount.dynatrace.com/accounts.

- Select the Account you need an OAuth Client for (if needed).

- Select "Identity & access management" at the top.

- Select the "OAuth Clients" option from the dropdown.

- Click the "Create client" button.

- Enter your Dynatrace login email.

- Scroll to the "Document Service" section.

- Check all the boxes under the "Document Service" section, or choose just the ones you plan to use to adhere to the "principle of least privilege".

- Click the "Create client" button.

- Copy the "Client ID", "Client secret" and "Dynatrace account URN" using the "copy" icon to the right of each one.

- Save these items in your password keeper/secrets manager (and no, Notepad is not a password keeper.  If you don't have a password keeper, I suggest trying "Bitwarden").
