# Machine to machine (M2M) communication using <br>Azure Active Directory

This example shows:
* how to configure an API to require access tokens issued by Azure Active Directory
* how to obtain access tokens for a confidential client (meaning an application that is
  able to handle secrets), running as a background worker or daemon, without user interaction

`server.py` contains the server definition that requires and validates access tokens.
`client_using_secret.py` contains a client definition that, using [MSAL for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python), obtains access
tokens using the `client credentials flow` **with a secret**, and calls the server.

`client_using_certificate.py` contains a client definition that, using [MSAL for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python), obtains access
tokens using the `client credentials flow` **with a certificate**, and calls the server.
Refer to the information under `certs` folder to have a reference on how to generate valid
certificates for Azure Active Directory.

`client_http_example.py` shows an example using the client credentials flow
with secret with an HTTP POST request to the token endpoint, without using MSAL for Python.

The following scheme describes the flow of this example.

![Scheme](https://gist.githubusercontent.com/RobertoPrevato/38a0598b515a2f7257c614938843b99b/raw/7ccbef683b18379ccf003ae9c7823ee03f3dc9f5/client-credentials-flow.png)

* Client is the application running as daemon, connecting to the API
* AAD is Azure Active Directory
* API is the web application exposing an API and requiring access tokens

## How to run this example

To run the example using the secret:

1. configure app registrations in a Azure Active Directory tenant
2. create a `.env` file with appropriate values, like in the example below,
   or in alternative, configure the environmental variables as in the same
   example
3. create a Python virtual environment, install the dependencies in `requirements.txt`
4. activate the virtual environment in two terminals, then:
5. run the server in one terminal `python server.py`
6. run the client file in another terminal `python client_using_secret.py`

The client file should display that an access token is obtained successfully
from Azure Active Directory and a call to the running server was successful.

`http_example.py` shows an example of how the client credentials flow with secret can be
used with HTTP, without using MSAL for Python.

## Example .env file

To configure application settings to run these examples, create an `.env` file
with contents like in the following block:

```bash
# Server configuration
API_ISSUER="https://sts.windows.net/<YOUR_TENANT_ID>/"
API_AUDIENCE="<YOUR_API_AUDIENCE_OR_CLIENT_ID>"

# Client configuration
AAD_AUTHORITY="https://login.microsoftonline.com/<YOUR_TENANT_ID>/"
APP_CLIENT_ID="<YOUR_CLIENT_APP_CLIENT_ID>"
APP_CLIENT_SECRET="<YOUR_CLIENT_APP_SECRET>"
APP_CLIENT_SCOPE="<YOUR_API_APP_CLIENT_ID>/.default"

# For the example using a certificate:
APP_CLIENT_CERT_THUMBPRINT="<YOUR_CERT_THUMBPRINT>"
```

The `.env` file is read using `python-dotenv` when the examples are run.
