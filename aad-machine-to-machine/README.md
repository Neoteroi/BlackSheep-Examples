# Machine to machine (M2M) communication using <br>Azure Active Directory

This example shows:
* how to configure an API to require access tokens issued by Azure Active Directory
* how to obtain access tokens for a confidential client (meaning an application that is
  able to handle secrets), as a background worker or daemon (without user interaction)

`server.py` contains the server definition that requires and validates access tokens.
`client.py` contains the client definition that, using MSAL for Python, obtains access
tokens using `client credentials flow` and calls the server.

## How to run this example

1. configure app registrations in a Azure Active Directory tenant
2. create a `.env` file with appropriate values, like in the example below,
   or in alternative, configure the environmental variables as in the same
   example
3. create a Python virtual environment, install the dependencies in `requirements.txt`
4. activate the virtual environment in two terminals, then:
5. run the server in one terminal `python server.py`
6. run the client file in another terminal `python client.py`

`client.py` should display that an access token is obtained successfully from Azure
Active Directory and a call to the running server was successful.

## Example .env file

```bash
# Server configuration
API_ISSUER="https://sts.windows.net/<YOUR_TENANT_ID>/"
API_AUDIENCE="<YOUR_API_AUDIENCE_OR_CLIENT_ID>"

# Client configuration
AAD_AUTHORITY="https://login.microsoftonline.com/<YOUR_TENANT_ID>/"
APP_CLIENT_ID="<YOUR_CLIENT_APP_CLIENT_ID>"
APP_CLIENT_SECRET="<YOUR_CLIENT_APP_SECRET>"
APP_CLIENT_SCOPE="<YOUR_API_APP_CLIENT_ID>/.default"
```
